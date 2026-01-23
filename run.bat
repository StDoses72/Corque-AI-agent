@echo off
title Corque Agent
cd /d "%~dp0"

echo Starting Corque...
echo.

python main.py

echo.
echo Corque exited.
pause

