@echo off
REM YouTube Downloader GUI Launcher for Windows
REM Double-click this file to start the GUI application

echo 🐙 TakoAI - YouTube Downloader
echo 🎬 Professional Media Solutions - Phase 3 GUI
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo.
    echo 💡 Please install Python from https://python.org
    echo    Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Check if we're in the right directory
if not exist "src\youtube_downloader" (
    echo ❌ Cannot find youtube_downloader source code
    echo.
    echo 💡 Make sure you're running this script from the project root directory
    echo    The directory should contain 'src\youtube_downloader\' folder
    echo.
    pause
    exit /b 1
)

echo ✅ Source code found
echo.

REM Try to start the GUI
echo 🚀 Starting YouTube Downloader GUI...
echo.

python run_gui.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ Failed to start the GUI application
    echo.
    echo 💡 You may need to install dependencies first:
    echo    pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo.
echo 👋 GUI application closed
pause 