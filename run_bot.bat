@echo off
title Twitch OCR Chatbot
echo Starting Twitch OCR Chatbot...
echo.

:: Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment 'venv' not found!
    echo Please ensure you are running this from the project folder.
    echo.
    pause
    exit /b
)

:: Activate the venv and start the bot
call venv\Scripts\activate.bat
python main.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] The bot crashed or exited with an error code %ERRORLEVEL%.
    pause
)
