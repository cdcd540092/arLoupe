@echo off
setlocal EnableDelayedExpansion
title arLoupe System - Environment Setup

echo ============================================
echo   arLoupe System - One-Click Setup
echo ============================================
echo.

:: 1. Check Node.js
echo [1/5] Checking Node.js installation...
where npm >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Node.js (npm) is not installed!
    echo Please install Node.js from https://nodejs.org/ and try again.
    pause
    exit /b
)
echo [OK] Node.js is installed.

:: 2. Check Python
echo.
echo [2/5] Checking Python installation...
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.10+ from https://www.python.org/ and check "Add Python to PATH".
    pause
    exit /b
)
echo [OK] Python is installed.

:: 3. Install Frontend Dependencies
echo.
echo [3/5] Installing Frontend Dependencies (npm install)...
cd /d "%~dp0"
call npm install
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to install frontend dependencies.
    pause
    exit /b
)
echo [OK] Frontend setup complete.

:: 4. Setup Python Virtual Environment
echo.
echo [4/5] Setting up Backend Virtual Environment (venv)...
cd /d "%~dp0arLoupe-main\arloupe_backend"
if not exist "venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv
) else (
    echo Virtual environment already exists.
)

:: 5. Install Backend Dependencies
echo.
echo [5/5] Installing Backend Dependencies (pip install)...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to install backend dependencies.
    pause
    exit /b
)
echo [OK] Backend setup complete.

:: 6. Setup Database
echo.
echo [Bonus] Running database migrations...
python manage.py migrate

echo.
echo ============================================
echo   Setup Complete Successfully!
echo   You can now double-click "start.bat" to run the system.
echo ============================================
pause
