@echo off
title Corque Dependency Setup
cd /d "%~dp0"

setlocal enabledelayedexpansion

echo Checking required runtimes...
where winget >nul 2>&1
if errorlevel 1 (
  echo.
  echo winget not found. Please install App Installer from Microsoft Store,
  echo then re-run this script.
  pause
  exit /b 1
)

where python >nul 2>&1
if errorlevel 1 (
  echo.
  echo Installing Python via winget...
  winget install -e --id Python.Python.3.13
  if errorlevel 1 (
    echo.
    echo Python install failed.
    pause
    exit /b 1
  )
  echo Python installed. You may need to close and re-open this window.
)

where node >nul 2>&1
if errorlevel 1 (
  echo.
  echo Installing Node.js (includes npm) via winget...
  winget install -e --id OpenJS.NodeJS.LTS
  if errorlevel 1 (
    echo.
    echo Node.js install failed.
    pause
    exit /b 1
  )
  echo Node.js installed. You may need to close and re-open this window.
)

where npm >nul 2>&1
if errorlevel 1 (
  echo.
  echo npm not found after Node.js install. Please re-open this window and try again.
  pause
  exit /b 1
)

where ollama >nul 2>&1
if errorlevel 1 (
  echo.
  echo Installing Ollama via winget...
  winget install -e --id Ollama.Ollama
  if errorlevel 1 (
    echo.
    echo Ollama install failed.
    pause
    exit /b 1
  )
  echo Ollama installed. You may need to close and re-open this window.
)

echo Installing Python dependencies...
python -m pip install -r requirements-full.txt
if errorlevel 1 (
  echo.
  echo Python dependency install failed.
  pause
  exit /b 1
)

echo.
echo Installing Node dependencies for corque-ui...
cd corque-ui
npm install
if errorlevel 1 (
  echo.
  echo Node dependency install failed.
  pause
  exit /b 1
)

echo.
echo All dependencies installed successfully.
pause
exit /b 0
