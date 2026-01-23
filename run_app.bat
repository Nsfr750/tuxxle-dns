@echo off
echo === Tuxxle-DNS Launcher ===
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\python.exe" (
    echo Error: Virtual environment not found!
    echo Please run install_deps.bat first.
    pause
    exit /b 1
)

REM Check if main script exists
if not exist "main.py" (
    echo Error: main.py not found!
    pause
    exit /b 1
)

REM Run the application
echo Starting Tuxxle-DNS...
echo.
venv\Scripts\python.exe main.py

if errorlevel 1 (
    echo.
    echo ❌ Application failed to start!
    pause
    exit /b 1
)
