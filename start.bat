@echo off
title arLoupe System Launcher

echo ============================================
echo   arLoupe System - One Click Start
echo ============================================
echo.

echo [1/3] Starting Django Backend (Port 8000)...
start "Django Backend" cmd /k "cd /d C:\Users\user\Downloads\phase-2-admin-suite\arLoupe-main\arloupe_backend && .\venv\Scripts\Activate && python manage.py runserver 8000"

echo [2/3] Starting Vue Frontend (Port 3000)...
start "Vue Frontend" cmd /k "cd /d C:\Users\user\Downloads\phase-2-admin-suite && npm run dev"

echo [3/3] Waiting for servers to start...
timeout /t 5 /nobreak >nul

echo.
echo Opening browser...
start http://localhost:3000/

echo.
echo ============================================
echo   Frontend: http://localhost:3000
echo   Backend:  http://localhost:8000
echo.
echo   Close the other 2 terminal windows
echo   to stop the servers.
echo ============================================
pause
