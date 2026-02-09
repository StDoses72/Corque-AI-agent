# Corque AI Agent

Corque is a personal AI assistant that runs on your computer. Think of it as a helpful assistant that can manage your todo list, check the weather, send emails, and search the web - all through a simple chat interface.

## What Can Corque Do?

Corque comes with a bunch of useful tools built right in:

- **Todo List Management**: Add tasks, check what's due, mark things as done, and see your upcoming todos
- **Email**: Send emails (with your approval first, so nothing goes out without you checking it)
- **Inbox Check**: Read unread emails from a specific date (defaults to today)
- **Weather**: Get current weather info for any location
- **Web Search**: Look things up online when you need real-time information
- **Daily News**: Pull the latest headlines on a topic
- **Time Tools**: Handle timezone conversions and date calculations automatically
- **Code Generation**: Generate code files into `workspace/` based on a detailed spec
- **Run Code**: Execute scripts safely from the `workspace/` directory

The best part? You just talk to it naturally. Ask it to "add a todo for tomorrow" or "what's the weather in New York?" and it figures out what to do.

## Getting Started

### Prerequisites

You'll need a few things installed first:

- Python 3.9 or higher
- Ollama installed and running on your system
- The `gpt-oss:120b-cloud` model (or you can change it in the config)
- Node.js + npm (only if you want to run the Electron UI in `corque-ui/`)

### Installation

1. Clone or download this repository

2. Install the required Python packages. You'll need:
   - `langchain`
   - `langchain-ollama`
   - `langchain-openai`
   - `langgraph`
   - `python-dotenv`
   - `tzlocal`
   - `tavily-python` (for web search)
   - `requests` (used by the weather tool)
   - `fastapi`, `uvicorn`, `pydantic` (for the API server/UI backend)
   - Standard library stuff like `smtplib` and `imaplib` (usually already included)

   You can install them with:
   ```
   pip install langchain langchain-ollama langchain-openai langgraph python-dotenv tzlocal tavily-python requests
   ```
   Or use the provided requirements file for the API server:
   ```
   pip install -r requirements.txt
   ```
   For a full install (agent + tools + API + UI backend):
   ```
   pip install -r requirements-full.txt
   ```
   Or just run the one-click installer on Windows:
   ```
   dependencysetup.bat
   ```
   It will install Python, Node.js (npm), and Ollama via `winget` if missing.
   If it installs a runtime, close and re-open the terminal before re-running it.

3. Set up your environment variables. Create a `.env` file in the project root with your email settings:

   ```
   EMAIL_USER=your-email@example.com
   EMAIL_PASS=your-email-password
   SMTP_SERVER=smtp.example.com
   IMAP_SERVER=imap.example.com
   SENDER_NAME=Your Name            # Optional, email signature name
   USER_NAME=Your Name              # Optional, fallback sender name
   REGION=your-region               # Optional, used by the UI settings
   TAVILY_API_KEY=your-tavily-api-key # Optional, only needed for web search
   DEDALUS_API_KEY=your-dedalus-key  # Required for the default model
   ```

   The email settings depend on your email provider. For Gmail, you'd use `smtp.gmail.com` and `imap.gmail.com`, but you'll need an app-specific password.

4. Make sure Ollama is running and has the model you want to use. The default is `gpt-oss:120b-cloud`, but you can change it in `config/settings.py` if you prefer a different model.

### Running Corque

On Windows, you can just double-click `run.bat`, or run:
```
python main.py
```

Once it starts, you'll see "Corque is ready to assist you!" and you can start chatting. Type `quit` when you're done.

If you want to run the API server (used by the UI), start it with:
```
uvicorn api_server:app --host 127.0.0.1 --port 8000 --reload
```

To launch the Electron UI on Windows, use:
```
start.bat
```
Run `npm install` inside `corque-ui/` the first time to install Electron dependencies.
Note: `corque-ui/main.js` currently starts the backend using `py -3.13`. If your Python version is different, update that command or ensure Python 3.13 is installed.

## How It Works

Corque uses LangChain and LangGraph to create an AI agent that can use tools. When you ask it something, it decides which tools (if any) it needs to use, uses them behind the scenes, and gives you a clean answer.

For example, if you say "add a todo to buy groceries tomorrow", it will:
1. Figure out what "tomorrow" means in actual time
2. Add the task to the SQLite database
3. Tell you it's done

All the technical stuff happens automatically - you just get the result.

## Email Safety

When Corque wants to send an email, it stops and asks for your approval first. You'll see the recipient, subject, and body, and you can approve it, edit it, or reject it. This way nothing goes out without you knowing about it.

## Customization

You can tweak things in `config/settings.py`:
- Change the model name (default is `gpt-oss:120b-cloud`)
- Adjust the number of threads
- Modify other settings

The todo list is stored in `data/CorqueDB.db` as a SQLite database. It gets created automatically the first time you run Corque.

## Project Structure (For Developers)

If you're looking to modify or extend Corque, here's how the code is organized:

```
Corque-AI-agent/
├── api_server.py           # FastAPI server for chat history, settings, and approvals
├── main.py                 # Entry point - starts the agent and handles the chat loop
├── run.bat                 # Windows batch file to launch Corque easily
├── start.bat               # Windows batch file to launch the Electron UI
├── dependencysetup.bat     # One-click dependency installer (Python + Node)
├── requirements.txt        # Python deps for the API server
├── requirements-full.txt   # Full dependency list for agent + tools + API + UI backend
├── LICENSE                 # Project license
├── IMAPTesting.py          # Local IMAP test script (manual debugging helper)
│
├── data/
│   └── CorqueDB.db         # SQLite database for storing todos + chat history
│
├── workspace/              # Generated code files live here (safe execution sandbox)
│   ├── calculator.py
│   └── web_spider.py
│
├── core/
│   ├── agent.py            # The main Agent class - sets up the LLM, tools, and handles requests
│   └── skill_loader.py     # Loads markdown skills into structured objects
│
├── middleware/
│   └── skill_middleware.py # Injects skill list into the system prompt
│
├── config/
│   └── settings.py         # Configuration settings - loads env vars and sets defaults
│
├── tools/                  # All the tools the agent can use
│   ├── __init__.py         # Exports all tools so they can be imported easily
│   ├── emailTools.py       # Email sending and receiving functions
│   ├── todoListTools.py    # Todo list CRUD operations (add, get, delete, change status)
│   ├── weatherTools.py     # Weather lookup using wttr.in
│   ├── timeTools.py        # Timezone conversion and date utilities
│   ├── webSearch.py        # Web search using Tavily API
│   ├── newsTools.py        # Daily news search via Tavily
│   ├── loadskillTools.py   # Loads a full skill into context on demand
│   └── codeGenTools.py     # Code generation and workspace-safe execution
│
├── skills/                 # Markdown skills that can be loaded at runtime
│   ├── Cat_persona.md
│   ├── coding_agent.md
│   ├── skillArchitect.md
│   └── toolArchitect.md
│
├── corque-ui/              # Electron-based desktop UI
│   ├── main.js             # Electron main process (starts API server)
│   ├── index.html          # Main UI shell
│   ├── history.html        # Chat history view
│   ├── email.html          # Email approval view
│   ├── settings.html       # Settings view
│   ├── tools.html          # Tools/skills marketplace view
│   ├── tools-data.json     # Sample tool/skill metadata
│   ├── cactus.png          # UI icon asset
│   ├── package.json        # Electron app manifest
│   └── package-lock.json
```

**Key files to know:**

- `main.py`: This is where everything starts. It initializes the todo database and creates the Agent instance, then runs a simple input loop.
- `core/agent.py`: The heart of the system. This is where the LangChain agent is set up with all the tools, the system prompt, and the model configuration. It also handles the human-in-the-loop middleware for email approval.
- `api_server.py`: FastAPI backend used by the Electron UI. Stores chats, messages, and pending approvals.
- `core/skill_loader.py`: Reads markdown files from `skills/` and exposes them to the agent.
- `middleware/skill_middleware.py`: Appends the skill list to the system prompt and enables `load_skill`.
- `tools/`: Each tool file contains functions decorated with `@tool` from LangChain. These are what the agent can actually do. To add a new capability, create a new tool file here and add it to the tools list in `agent.py`.
- `tools/codeGenTools.py`: Generates code into `workspace/` and optionally runs it in a sandboxed way.
- `corque-ui/`: Electron desktop UI that talks to the API server (and spawns it on launch).
- `IMAPTesting.py`: A quick local script to verify IMAP settings during development.
- `config/settings.py`: Centralized configuration. All environment variables are loaded here, and you can change defaults like the model name or number of threads.

The tools are imported through `tools/__init__.py`, which makes it easy to add new ones - just add them to the imports there and they'll be available to the agent.

## Notes

- The first time you run it, the database will be created automatically
- Email sending requires your email credentials in the `.env` file
- Web search and daily news need a Tavily API key (you can get one at tavily.com)
- The agent is designed to be direct and helpful - it won't give you extra suggestions unless you ask
- We also maintain a dedicated place for custom plugins; see https://github.com/CactusStd/Corque-Plugin-Platform

## Troubleshooting

If something's not working:
- Make sure Ollama is running and the model is downloaded
- Check that your `.env` file has all the required variables
- Ensure `DEDALUS_API_KEY` is set if you use the default model configuration
- Verify your email settings are correct (especially if using Gmail, you'll need an app password)
- Make sure all Python packages are installed
- Make sure that your CUDA toolkit and your GPU driver is correctly deployed

That's about it! Corque is pretty straightforward - just start it up and start asking it things.