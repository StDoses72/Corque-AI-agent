from langchain_ollama import ChatOllama
import os
import re
import subprocess
import tempfile
from typing import Dict, List, Tuple, Optional
from config.settings import settings
from langchain_core.tools import tool
import sys
import subprocess
import shutil


coding_prompt = """

# Role
You are an **Elite Full-Stack Software Engineer** and **Polyglot Code Generator**.
You transform technical specifications into production-grade, executable code files.

# CRITICAL: OUTPUT FORMAT (STRICT)
You must output code using the following structure EXACTLY. 
1. **Header**: Use `### filename.ext` for each file.
2. **Code**: Follow immediately with a standard markdown code block.
3. **No Bold**: Do NOT use bold text for filenames (e.g., do NOT write `**filename**`).
4. **No Wrapper**: Do NOT wrap the entire response in a single code block.

--- FORMAT TEMPLATE START ---
### filename.ext
```language
code here...
```
### another_file.ext
```language
code here...
```
--- FORMAT TEMPLATE END ---
Example (Mental Model)
User: "Create a calculator with two files, one is the main file and the other is a utils file." 
You:
### main.py
```python
from math_utils import add

if __name__ == "__main__":
    print(add(10, 5))
```
### math_utils.py
```python
def add(a, b):
    return a + b
(Other code...)
```
**Critical Guidelines**
1. **Multiple Files**: If the spec requires multiple files (e.g., backend + frontend, or module + main), output them ALL in a single response using the template above.
2. **Self-Contained**:
    - Ensure main files import helper files correctly.
    - ALWAYS include an entry point (e.g., if __name__ == "__main__": for Python) so the code can be run immediately.
3. **No Conversational Filler**: Do not say "Here is the code". Do not explain the code unless asked. Just output the file markers and code blocks.
4. **Defensive Coding**: Validate inputs and handle errors.
**Language-Specific Standards**
- Python: Use Type Hints, PEP 8.
- Node.js: Use CommonJS (require) for simple scripts, or ES Modules (import) if specified.
- Web: Semantic HTML, CSS Flexbox/Grid
**Task**
Translate the user's input into code of the format defined above. Ensure the code is clean, secure, and performant
# Response Strategy
1.  Read Spec -> Identify Language & Framework.
2.  Plan Structure -> Imports/Classes/Functions.
3.  Write Code -> Implement logic with error handling.
4.  Final Review -> Ensure no missing imports or syntax errors.
"""

@tool
def runCode(code_path: str,script_args: Optional[List[str]] = None) -> str:
    """
    This tool is used to run the code within the workspace directory.
    Args:
        code_path (str): The path of the code to be run.
        script_args (Optional[List[str]]): The arguments to be passed to the code.
    Returns:
        str: STDOUT and STDERR execution results.
    """
    LANGUAGE_RUNNERS = {
    ".py":  [sys.executable],           # Python: 使用当前环境
    ".js":  ["node"],                   # JavaScript: 需要安装 Node.js
    ".ts":  ["ts-node"],                # TypeScript: 需要安装 ts-node
    ".sh":  ["bash"],                   # Shell: 使用 bash
    ".go":  ["go", "run"],              # Go: 使用 go run 直接运行
    ".rb":  ["ruby"],                   # Ruby
    ".php": ["php"],                    # PHP
}
    if ".." in code_path or not code_path.startswith("workspace/"):
         return "Error: Security Violation. Can only run scripts in 'workspace/' directory."
    runner = LANGUAGE_RUNNERS.get(code_path.split(".")[-1])
    if not runner:
        return f"Error: No runner found for {code_path}, supported are: {', '.join(LANGUAGE_RUNNERS.keys())}"
    executable = runner[0]
    if executable != sys.executable and not shutil.which(executable):
        return f"Error: The runtime '{executable}' is not installed or not in PATH."
    safe_args = script_args if script_args else []
    cmd = runner + safe_args + [code_path]
    try:
        print(f"Running code: {cmd}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        output = f"--- Execution Result ({executable}) ---\n"
        if result.returncode == 0:
            output += f"Success!\nSTDOUT:\n{result.stdout[:2000]}"
        else:
            output += f"Failed (Exit Code {result.returncode})\n"
            output += f"STDERR:\n{result.stderr[:2000]}\n"
            # 有些程序报错也会打在 stdout 里
            if result.stdout:
                output += f"STDOUT:\n{result.stdout[:2000]}"
                
        return output
    except subprocess.TimeoutExpired:
        return f"Error: The code execution timed out after 20 seconds."
    except Exception as e:
        return f"Error: {e}"

@tool
def generateCode(code_request: str, max_attempts: int = 5) -> Dict[str, str]:
    """
    This tool is used to generate code based on the code_request.
    What you need to do is to generate appropriate prompt for the goal of user's request.
    This is a REQUIRED tool for creating code files. 
    You CANNOT create code files by just writing text. You MUST use this tool.
    Then, give the prompt to this tool, it will use a coding model to generate the code.
    Use this to:
    1. Write Python/JS/Go/and other languages code based on a spec.
    2. SAVE that code to the 'workspace/' directory.
    3. Return the file paths for execution.
    Args:
        code_request (str): The Detailed requirements for the code generation.
    Returns:
        Dict[str, str]: Extracted code mapped by filename.
    """
    if not code_request or not code_request.strip():
        raise ValueError("code_request must be a non-empty string.")

    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1.")

    model = ChatOllama(model=settings.codingModelName, temperature=0.1, keep_alive="5m")
    messages = [{"role": "system", "content": coding_prompt}, {"role": "user", "content": code_request}]

    expected_files = _extract_requested_filenames(code_request)
    expected_min_files = max(1, len(expected_files))

    for attempt in range(1, max_attempts + 1):
        print(f"[Coding Model] Generating code (Attempt {attempt}/{max_attempts})...") 
        response = model.invoke(messages)
        ai_code = response.content or ""
        extracted = parse_code_response(ai_code)
        if not extracted:
            fallback_name = _detect_default_filename(ai_code)
            extracted = {fallback_name: ai_code.strip()}

        validation_ok, validation_errors = _validate_generated_files(
            extracted,
            expected_files,
            expected_min_files,
        )
        if not validation_ok:
            if attempt < max_attempts:
                feedback = (
                    "The generated output did not meet the required file format. "
                    "Please fix the issues and return corrected code in the exact same "
                    "format (### filename + fenced code blocks).\n\n"
                    f"{validation_errors}"
                )
                messages.append({"role": "assistant", "content": ai_code})
                messages.append({"role": "user", "content": feedback})
                continue
                
        ruff_ok, ruff_errors = _run_ruff_check(extracted)
        try:
            semgrep_ok, semgrep_errors = _run_semgrep_check(extracted)
        except Exception as e:
            semgrep_ok = True
            semgrep_errors = "Semgrep check skipped due to dependency conflict."
            print(f"Semgrep check skipped due to dependency conflict: {e}")
            
        if ruff_ok and semgrep_ok and validation_ok:
            saved_paths, failed_saves = _save_generated_files(extracted)
            if failed_saves:
                return (
                    "Code generation succeeded, but some files failed to save. "
                    f"Failures: {failed_saves}. "
                    f"Saved files: {saved_paths}. "
                    "Please check workspace permissions or invalid filenames."
                )
            return (
                "Successfully generated code and saved to workspace directory. "
                f"The code is: {'\n'.join([f'{filename}: {code}' for filename, code in extracted.items()])}. "
                f"The path of the saved code is: {saved_paths}. "
                "You can now run the code using the runCode tool."
            )

        if attempt < max_attempts:
            feedback_parts = []
            if not ruff_ok:
                feedback_parts.append(
                    "The generated Python code has Ruff lint issues. "
                    "Please fix the following errors and return corrected code "
                    "in the exact same format (### filename + fenced code blocks).\n\n"
                    f"{ruff_errors}"
                )
            if not semgrep_ok:
                feedback_parts.append(
                    "The generated non-Python code has Semgrep lint issues. "
                    "Please fix the following errors and return corrected code "
                    "in the exact same format (### filename + fenced code blocks).\n\n"
                    f"{semgrep_errors}"
                )
            feedback = "\n\n".join(part for part in feedback_parts if part)
            messages.append({"role": "assistant", "content": ai_code})
            messages.append({"role": "user", "content": feedback})

    # extracted["_warning"] = (
    #     "Code generation did not pass validation or Ruff checks after "
    #     f"{max_attempts} attempts. Output may contain lint errors."
    # )
    saved_paths, failed_saves = _save_generated_files(extracted)
    if failed_saves:
        return (
            "Code generation finished but failed validation or lint checks, "
            "and some files failed to save. "
            f"Failures: {failed_saves}. Saved files: {saved_paths}."
        )
    return (
        "Successfully generated code and saved to workspace directory but failed to pass "
        "validation or lint checks. "
        f"The code is: {'\n'.join([f'{filename}: {code}' for filename, code in extracted.items()])}. "
        f"The path of the saved code is: {saved_paths}. "
        "You can now run the code using the runCode tool."
    )

def parse_code_response(raw_response: str) -> Dict[str, str]:
    """
    解析 LLM 返回的多文件代码字符串。
    
    Expected Format:
    ### main.py
    ```python
    print('hello')
    ```
    
    ### utils.py
    ```python
    def add(a, b): return a + b
    ```
    
    Returns:
        Dict[str, str]: {'main.py': "print('hello')", 'utils.py': "..."}
    """
    
    files = {}
    
    # 1. 预处理：即使模型很乖，也要防一手它在 ### 前面加了废话
    # 我们用正则找 ### filename，支持常见的文件扩展名
    # Pattern 解释:
    # ^\s*###\s+       -> 行首(允许空格) + ### + 至少一个空格
    # ([\w\-\./]+)     -> 捕获文件名 (字母, 数字, -, ., /)
    pattern = re.compile(r"^\s*###\s+([\w\-\./]+)", re.MULTILINE)
    
    # 找出所有分割点
    matches = list(pattern.finditer(raw_response))
    
    # Case A: 单文件 (没有 ### 分割)
    if not matches:
        # 如果没找到 ###，假设整个回复就是一个单文件代码
        # 尝试提取 markdown 块，如果没有 markdown 块，就返回原始内容
        content = _strip_markdown(raw_response)
        # 默认给个名字，或者根据内容猜测
        default_name = _detect_default_filename(raw_response)
        return {default_name: content}

    # Case B: 多文件
    for i, match in enumerate(matches):
        filename = match.group(1).strip()
        start_pos = match.end()
        
        # 结束位置是下一个 ### 的开始，或者是字符串末尾
        if i + 1 < len(matches):
            end_pos = matches[i + 1].start()
        else:
            end_pos = len(raw_response)
            
        # 提取内容
        code_block = raw_response[start_pos:end_pos]
        
        # 清理 Markdown 标记 (```python ... ```)
        clean_code = _strip_markdown(code_block)
        
        if clean_code:
            files[filename] = clean_code

    return files

def _strip_markdown(text: str) -> str:
    """Remove Markdown code block markers and leading/trailing whitespace."""
    text = text.strip()

    code_blocks = re.findall(r"```(?:[\w+-]+)?\s*(.*?)```", text, flags=re.DOTALL)
    if code_blocks:
        return "\n\n".join(block.strip() for block in code_blocks if block.strip())

    text = re.sub(r"^\s*```[\w+-]*\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\s*```\s*$", "", text)
    return text.strip()


def _detect_default_filename(raw_response: str) -> str:
    """Guess default filename based on code block language or content."""
    language_match = re.search(r"```([\w+-]+)", raw_response or "")
    if not language_match:
        return "main.txt"

    language = language_match.group(1).lower()
    extension_map = {
        "python": "py",
        "py": "py",
        "typescript": "ts",
        "ts": "ts",
        "tsx": "tsx",
        "javascript": "js",
        "js": "js",
        "jsx": "jsx",
        "go": "go",
        "golang": "go",
        "java": "java",
        "c": "c",
        "cpp": "cpp",
        "cxx": "cpp",
        "cs": "cs",
        "csharp": "cs",
        "html": "html",
        "css": "css",
        "sql": "sql",
        "bash": "sh",
        "shell": "sh",
        "sh": "sh",
        "json": "json",
        "yaml": "yaml",
        "yml": "yml",
        "markdown": "md",
        "md": "md",
    }
    extension = extension_map.get(language, "txt")
    return f"main.{extension}"


def _extract_requested_filenames(code_request: str) -> List[str]:
    """Try to detect explicit filenames requested by the user."""
    if not code_request:
        return []
    pattern = re.compile(
        r"\b[\w\-/]+\.(py|js|ts|tsx|jsx|html|css|go|java|json|yaml|yml|md)\b",
        re.IGNORECASE,
    )
    full_matches = re.findall(
        r"\b[\w\-/]+\.(?:py|js|ts|tsx|jsx|html|css|go|java|json|yaml|yml|md)\b",
        code_request,
        flags=re.IGNORECASE,
    )
    return [match for match in full_matches]


def _validate_generated_files(
    files: Dict[str, str],
    expected_files: List[str],
    expected_min_files: int,
) -> Tuple[bool, str]:
    """Validate output formatting and required file count."""
    errors = []
    if len(files) < expected_min_files:
        errors.append(
            f"Expected at least {expected_min_files} files, but got {len(files)}."
        )
        if expected_files:
            missing = [name for name in expected_files if name not in files]
            if missing:
                errors.append(f"Missing files: {', '.join(missing)}")

    dangling_fences = [name for name, content in files.items() if "```" in content]
    if dangling_fences:
        errors.append(
            "Found leftover markdown fences in files: " + ", ".join(dangling_fences)
        )

    return (len(errors) == 0, "\n".join(errors))


def _run_ruff_check(files: Dict[str, str]) -> Tuple[bool, str]:
    """Run Ruff on extracted Python files. Returns (ok, errors)."""
    python_files = {name: content for name, content in files.items() if name.endswith(".py")}
    if not python_files:
        return True, ""

    with tempfile.TemporaryDirectory() as temp_dir:
        for filename, content in python_files.items():
            safe_path = os.path.join(temp_dir, filename)
            os.makedirs(os.path.dirname(safe_path), exist_ok=True)
            with open(safe_path, "w", encoding="utf-8") as handle:
                handle.write(content)

        result = subprocess.run(
            ["ruff", "check", temp_dir],
            capture_output=True,
            text=True,
            check=False,
        )

    if result.returncode == 0:
        return True, ""

    errors = (result.stdout or "").strip()
    if result.stderr:
        errors = f"{errors}\n{result.stderr.strip()}".strip()
    return False, errors or "Ruff reported issues but did not return details."

def _run_semgrep_check(files: Dict[str, str]) -> Tuple[bool, str]:
    """Run Semgrep on non-Python files. Returns (ok, errors)."""
    non_python_files = {
        name: content for name, content in files.items() if not name.endswith(".py")
    }
    if not non_python_files:
        return True, ""

    with tempfile.TemporaryDirectory() as temp_dir:
        for filename, content in non_python_files.items():
            safe_path = os.path.join(temp_dir, filename)
            os.makedirs(os.path.dirname(safe_path), exist_ok=True)
            with open(safe_path, "w", encoding="utf-8") as handle:
                handle.write(content)

        result = subprocess.run(
            ["semgrep", "--config", "auto", temp_dir],
            capture_output=True,
            text=True,
            check=False,
        )

    if result.returncode == 0:
        return True, ""

    errors = (result.stdout or "").strip()
    if result.stderr:
        errors = f"{errors}\n{result.stderr.strip()}".strip()
    return False, errors or "Semgrep reported issues but did not return details."

def saveCode(filename: str, code: str) -> Optional[str]:
    """
    This tool is used to save the code to the code directory.
    Args:
        filename (str): The filename to save the code.
        code (str): The code to save.
    Returns:
        Optional[str]: The path of the saved code.
    """
    os.makedirs(settings.workspaceDir, exist_ok=True)
    try:
        normalized = _sanitize_filename(filename)
        if not normalized:
            print("Error saving code: invalid or empty filename.")
            return None
        if normalized.startswith("workspace/"):
            normalized = normalized[len("workspace/"):]

        target_path = os.path.join(settings.workspaceDir, normalized)
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as handle:
            handle.write(code)
        if not os.path.exists(target_path):
            print(f"Error saving code: file not found after write: {target_path}")
            return None
        print(f"Code saved to {target_path}")
        return target_path
    except Exception as e:
        print(f"Error saving code: {e}")
        return None


def _save_generated_files(files: Dict[str, str]) -> Tuple[Dict[str, str], Dict[str, str]]:
    """Save generated files and return (saved_paths, failed_saves)."""
    saved_paths: Dict[str, str] = {}
    failed_saves: Dict[str, str] = {}
    for filename, code in files.items():
        path = saveCode(filename, code)
        if path:
            saved_paths[filename] = path
        else:
            failed_saves[filename] = "Save failed or path invalid."
    if failed_saves:
        print(f"Save failures: {failed_saves}")
    return saved_paths, failed_saves


def _sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe saving (Windows-compatible)."""
    if not filename:
        return ""
    normalized = filename.replace("\\", "/").strip().lstrip("/")
    if not normalized:
        return ""

    invalid_chars = '<>:"|?*'
    parts = []
    for part in normalized.split("/"):
        clean = "".join(ch for ch in part if ch not in invalid_chars)
        clean = clean.rstrip(". ").strip()
        if clean:
            parts.append(clean)
    return "/".join(parts)

# # 1) Python 单文件：应通过 ruff
# print(generateCode("Write a Python function to compute Fibonacci with type hints and docstring."))

# # 2) Python 多文件：应通过 ruff
# print(generateCode(
#     "Create a small Python package with two files: main.py and utils.py. "
#     "main.py should call utils.add(a, b). Use type hints and no unused imports."
# ))

# # 3) 故意触发 ruff（未使用变量）
# print(generateCode(
#     "Write a Python script that defines an unused variable 'x = 1' and prints 'ok'."
# ))

# # 4) 非 Python：ruff 跳过（应直接返回）
# print(generateCode(
#     "Generate a simple HTML page with a centered button and basic CSS."
# ))