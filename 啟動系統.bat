@echo off
chcp 65001 >nul
title arLoupe 系統啟動器

echo ============================================
echo   arLoupe 牙科影像管理系統 - 一鍵啟動
echo ============================================
echo.

echo [1/3] 啟動 Django 後端 (Port 8000)...
start "Django Backend" cmd /k "cd /d C:\Users\user\Downloads\phase-2-admin-suite\arLoupe-main\arloupe_backend && .\venv\Scripts\Activate && python manage.py runserver 8000"

echo [2/3] 啟動 Vue 前端 (Port 3000)...
start "Vue Frontend" cmd /k "cd /d C:\Users\user\Downloads\phase-2-admin-suite && npm run dev"

echo [3/3] 等待伺服器就緒...
timeout /t 5 /nobreak >nul

echo.
echo 正在開啟瀏覽器...
start http://localhost:3000/

echo.
echo ============================================
echo   系統已啟動完成！
echo   前端: http://localhost:3000
echo   後端: http://localhost:8000
echo   
echo   關閉此視窗不會影響伺服器運行。
echo   如需關閉伺服器，請關閉另外兩個終端機視窗。
echo ============================================
pause
