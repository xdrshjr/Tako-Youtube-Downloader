@echo off
REM YouTube Downloader API Startup Script for Windows
REM 
REM This batch file provides a convenient way to start the FastAPI server
REM on Windows systems.

echo.
echo ========================================
echo   YouTube Downloader API Server
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if we're in the correct directory
if not exist "requirements.txt" (
    echo ERROR: requirements.txt not found
    echo Please run this script from the project root directory
    pause
    exit /b 1
)

REM Install dependencies if needed
echo Checking dependencies...
python -c "import fastapi, uvicorn, pydantic" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing required dependencies...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Create necessary directories
if not exist "downloads" mkdir downloads
if not exist "logs" mkdir logs
if not exist "config" mkdir config

echo Dependencies OK
echo.

REM Set default values
set HOST=0.0.0.0
set PORT=8000
set MODE=production

REM Parse command line arguments
:parse_args
if "%1"=="--dev" (
    set MODE=development
    shift
    goto parse_args
)
if "%1"=="--port" (
    set PORT=%2
    shift
    shift
    goto parse_args
)
if "%1"=="--host" (
    set HOST=%2
    shift
    shift
    goto parse_args
)
if not "%1"=="" (
    shift
    goto parse_args
)

echo Configuration:
echo   Host: %HOST%
echo   Port: %PORT%
echo   Mode: %MODE%
echo.

echo API Endpoints:
echo   Health Check: http://%HOST%:%PORT%/health
echo   API Docs: http://%HOST%:%PORT%/docs
echo   ReDoc: http://%HOST%:%PORT%/redoc
echo   API Info: http://%HOST%:%PORT%/api/v1/info
echo.

echo Starting API server...
echo Press Ctrl+C to stop the server
echo.

REM Start the server based on mode
if "%MODE%"=="development" (
    python start_api.py --host %HOST% --port %PORT% --dev
) else (
    python start_api.py --host %HOST% --port %PORT%
)

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to start the server
    pause
    exit /b 1
)

echo.
echo Server stopped gracefully
pause 