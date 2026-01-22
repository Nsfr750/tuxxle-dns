@echo off
echo === DNS Server Manager - Dependency Installer ===
echo.

REM Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo Detecting Python version...
for /f "tokens=1,2" %%a in ('python --version 2^>^&1') do set PYTHON_VERSION=%%a

echo Found Python: %PYTHON_VERSION%
echo.

REM Run Python installer
python install_deps.py

if errorlevel 1 (
    echo.
    echo ❌ Installation failed!
    pause
    exit /b 1
) else (
    echo.
    echo ✅ Installation completed successfully!
    echo.
    echo You can now run the application with:
    echo    python main.py
    echo    python launcher.py
    echo    run.bat
    echo.
    pause
)
