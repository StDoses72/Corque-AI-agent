import os
import datetime

# Configuration
MEMORY_FILE = "memory.md"

def _ensure_memory_file():
    """Ensures the memory file exists with a header."""
    if not os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
            f.write("# Corque Long-Term Memory\n\n")

def remember(content: str, category: str = "general", tags: str = ""):
    """
    Saves a structured memory snippet.
    
    Args:
        content (str): The core information to remember.
        category (str): Classification (e.g., 'user_preference', 'project_info', 'task_status').
        tags (str): Comma-separated keywords for easier retrieval.
    """
    _ensure_memory_file()
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tag_list = [t.strip() for t in tags.split(',') if t.strip()]
    
    # Construct YAML Frontmatter style block (manual formatting to avoid deps)
    entry = f"""
---
date: {timestamp}
category: {category}
tags: {tag_list}
---
{content}
"""
    try:
        with open(MEMORY_FILE, 'a', encoding='utf-8') as f:
            f.write(entry)
        return f"Memory saved: [{category}] {content[:30]}..."
    except Exception as e:
        return f"Error saving memory: {str(e)}"

def recall(query: str, limit: int = 5):
    """
    Retrieves memories based on keyword matching (category, tags, or content).
    
    Args:
        query (str): The keyword to search for.
        limit (int): Max number of entries to return.
    """
    if not os.path.exists(MEMORY_FILE):
        return "No memory file found."
    
    found_entries = []
    
    try:
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            raw_data = f.read()
            
        # Split by the YAML separator '---'
        # Data format: [empty, metadata, content, metadata, content...]
        parts = raw_data.split('---')
        
        # Simple parser loop
        # We start from index 1 because index 0 is usually the file header or empty
        i = 1
        while i < len(parts) - 1:
            meta_block = parts[i].strip()
            content_block = parts[i+1].strip()
            
            # Basic parsing of metadata lines
            meta = {}
            for line in meta_block.split('\n'):
                if ':' in line:
                    key, val = line.split(':', 1)
                    meta[key.strip()] = val.strip()
            
            full_text = (meta_block + " " + content_block).lower()
            
            if query.lower() in full_text:
                date_str = meta.get('date', 'Unknown Date')
                cat_str = meta.get('category', 'General')
                found_entries.append(f"[{date_str}] ({cat_str}): {content_block}")
            
            i += 2
                
        # Return most recent matches first (reverse list)
        found_entries.reverse()
        results = found_entries[:limit]
        
        if not results:
            return f"No memories found matching '{query}'."
            
        return "\n\n---\n\n".join(results)

    except Exception as e:
        return f"Error recalling memory: {str(e)}"

def read_full_memory():
    """Reads the entire memory file (use with caution for context window)."""
    if not os.path.exists(MEMORY_FILE):
        return "Memory is empty."
    with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
        return f.read()

# Test block
if __name__ == "__main__":
    # Test creating a memory
    print(remember("User prefers Python over Java for backend tasks.", "user_preference", "coding, preferences"))
    # Test recalling it
    print("\nRecall Result:")
    print(recall("Python"))
