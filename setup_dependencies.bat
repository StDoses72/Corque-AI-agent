@echo off
setlocal

echo [Corque] Checking system dependencies...
where winget >nul 2>nul
set HAS_WINGET=1
if errorlevel 1 set HAS_WINGET=0

where python >nul 2>nul
if errorlevel 1 (
  if "%HAS_WINGET%"=="1" (
    echo [Corque] Installing Python 3.11 via winget...
    winget install --id Python.Python.3.11 -e --accept-package-agreements --accept-source-agreements
  )
)

where node >nul 2>nul
if errorlevel 1 (
  if "%HAS_WINGET%"=="1" (
    echo [Corque] Installing Node.js LTS via winget...
    winget install --id OpenJS.NodeJS.LTS -e --accept-package-agreements --accept-source-agreements
  )
)

where ollama >nul 2>nul
if errorlevel 1 (
  if "%HAS_WINGET%"=="1" (
    echo [Corque] Installing Ollama via winget...
    winget install --id Ollama.Ollama -e --accept-package-agreements --accept-source-agreements
  )
)

echo [Corque] Installing Python dependencies...
where python >nul 2>nul
if errorlevel 1 (
  echo [Error] Python not found. Please install Python 3.9+ and try again.
  exit /b 1
)

python -m pip install --upgrade pip
if errorlevel 1 exit /b 1

if exist requirements.txt (
  python -m pip install -r requirements.txt
  if errorlevel 1 exit /b 1
)

python -m pip install langchain langchain-ollama langgraph python-dotenv tzlocal tavily-python
if errorlevel 1 exit /b 1

echo [Corque] Installing Node.js dependencies...
where npm >nul 2>nul
if errorlevel 1 (
  echo [Warning] npm not found. Skipping UI dependencies.
  echo [Warning] Install Node.js if you want to run the Electron UI.
  exit /b 0
)

if exist "corque-ui\package.json" (
  pushd corque-ui
  npm install
  popd
)

echo [Corque] Dependencies installed successfully.
