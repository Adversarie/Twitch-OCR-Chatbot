@echo off
title Twitch OCR Chatbot Web UI
echo Starting Twitch OCR Chatbot Web UI...
echo.

:: Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment 'venv' not found!
    echo Please ensure you are running this from the project folder.
    echo.
    pause
    exit /b
)

:: Activate the venv and start the Web UI
call venv\Scripts\activate.bat
start http://127.0.0.1:8000
python web.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] The Web UI crashed or exited with an error code %ERRORLEVEL%.
    pause
)

