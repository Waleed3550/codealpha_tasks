@echo off
title CodeAlpha Social Media App - Launcher
echo ============================================
echo   Starting CodeAlpha Social Media App
echo ============================================
echo.

REM --- Start Django backend in its own window ---
echo Starting backend (Django) on http://127.0.0.1:8000 ...
start "Backend - Django" cmd /k "cd /d "C:\Users\hp\Desktop\social app" && venv\Scripts\activate && cd socialmedia_backend && python manage.py runserver"

REM --- Wait a couple seconds so backend has time to boot ---
timeout /t 3 /nobreak >nul

REM --- Start React frontend in its own window ---
echo Starting frontend (React/Vite) on http://localhost:5173 ...
start "Frontend - React" cmd /k "cd /d "C:\Users\hp\Desktop\social app\client" && npm run dev"

REM --- Wait a moment then open the browser ---
timeout /t 4 /nobreak >nul
start http://localhost:5173

echo.
echo ============================================
echo   Both servers are starting in separate windows.
echo   Close those windows (or Ctrl+C inside them) to stop the app.
echo ============================================
