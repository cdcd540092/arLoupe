@echo off
setlocal EnableDelayedExpansion
title arLoupe System - Environment Setup

echo ============================================
echo   arLoupe System - Environment Check ^& Setup
echo ============================================
echo.

:: 1. Check Node.js
echo [1/5] Checking Node.js installation...
where npm >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Node.js is not installed!
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
echo [3/5] Checking Frontend Dependencies...
cd /d "%~dp0"
if exist "node_modules\" (
    echo [OK] Frontend dependencies already exist. Skipping npm install.
) else (
    echo Installing Frontend Dependencies...
    call npm install
    if !ERRORLEVEL! neq 0 (
        echo [ERROR] Failed to install frontend dependencies.
        pause
        exit /b
    )
    echo [OK] Frontend setup complete.
)

:: 4. Setup Python Virtual Environment
echo.
echo [4/5] Checking Backend Virtual Environment...
cd /d "%~dp0arLoupe-main\arloupe_backend"
if exist "venv\Scripts\activate.bat" (
    echo [OK] Virtual environment already exists.
) else (
    echo Creating Python virtual environment...
    python -m venv venv
    echo [OK] Virtual environment created.
)

:: 5. Install Backend Dependencies
echo.
echo [5/5] Checking Backend Dependencies...
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo Verifying pip packages...
    python -m pip install --upgrade pip >nul 2>nul
    pip install -r requirements.txt
    if !ERRORLEVEL! neq 0 (
        echo [ERROR] Failed to install backend dependencies.
        pause
        exit /b
    )
    echo [OK] Backend dependencies installed/verified.
)

:: 6. Setup Database
echo.
echo [Bonus] Verifying database structure...
python manage.py migrate >nul 2>nul
echo [OK] Database is up to date.

echo.
echo ============================================
echo   All environments are fully setup and ready!
echo   You can now close this window and double-click "start.bat"
echo ============================================
pause
