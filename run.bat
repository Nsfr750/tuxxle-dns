@echo off
echo Starting DNS Server Manager...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if we're in the correct directory
if not exist "main.py" (
    echo Error: main.py not found. Please run this script from the project root directory.
    pause
    exit /b 1
)

REM Run the application
python main.py

REM If the application crashes, show the error
if errorlevel 1 (
    echo.
    echo Application exited with an error.
    pause
)
