@echo off
setlocal enabledelayedexpansion

echo =======================================================
echo  Twitch OCR Chatbot - Windows Build and Installer Script
echo =======================================================

cd /d "%~dp0.."

:: Terminate running instances to release file locks on dist binaries
taskkill /F /IM TwitchOCRBot.exe >nul 2>&1
timeout /t 1 /nobreak >nul 2>&1

:: Detect Python executable (prefer local venv)
set "PYTHON_EXE=python"
if exist "venv\Scripts\python.exe" set "PYTHON_EXE=venv\Scripts\python.exe"
echo Using Python: %PYTHON_EXE%

echo [INFO] Running PyInstaller build using TwitchOCRBot.spec...
"%PYTHON_EXE%" -m PyInstaller TwitchOCRBot.spec --clean --noconfirm
if errorlevel 1 (
    echo [ERROR] PyInstaller build failed.
    exit /b 1
)

if not exist "dist\TwitchOCRBot\TwitchOCRBot.exe" (
    echo [ERROR] dist\TwitchOCRBot\TwitchOCRBot.exe was not found.
    exit /b 1
)

echo =======================================================
echo [SUCCESS] Windows standalone build complete.
echo Output directory: dist\TwitchOCRBot\
echo Executable:       dist\TwitchOCRBot\TwitchOCRBot.exe
echo =======================================================

if defined SIGNTOOL_ARGS (
    echo [INFO] Signing dist\TwitchOCRBot\TwitchOCRBot.exe with signtool...
    signtool sign %SIGNTOOL_ARGS% "dist\TwitchOCRBot\TwitchOCRBot.exe"
)

set "ISCC_EXE="
if exist "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" set "ISCC_EXE=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" set "ISCC_EXE=C:\Program Files\Inno Setup 6\ISCC.exe"
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" set "ISCC_EXE=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if exist "C:\Program Files (x86)\Inno Setup 7\ISCC.exe" set "ISCC_EXE=C:\Program Files (x86)\Inno Setup 7\ISCC.exe"
if exist "C:\Program Files\Inno Setup 7\ISCC.exe" set "ISCC_EXE=C:\Program Files\Inno Setup 7\ISCC.exe"

if not defined ISCC_EXE (
    echo [WARNING] Inno Setup ISCC.exe not found. Skipping installer compilation.
    exit /b 0
)

echo [INFO] Compiling Windows installer with Inno Setup: "%ISCC_EXE%"
"%ISCC_EXE%" "installer.iss"
if errorlevel 1 (
    echo [ERROR] Inno Setup installer compilation failed.
    exit /b 1
)

if defined SIGNTOOL_ARGS (
    echo [INFO] Signing dist\TwitchOCRBot-Setup-v1.0.0.exe with signtool...
    signtool sign %SIGNTOOL_ARGS% "dist\TwitchOCRBot-Setup-v1.0.0.exe"
)

echo =======================================================
echo [SUCCESS] Installer compiled: dist\TwitchOCRBot-Setup-v1.0.0.exe
echo =======================================================
endlocal
