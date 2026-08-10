@echo off
echo Starting Project Management Tool...

echo Starting Django backend...
start "Backend" cmd /k "cd backend && (if exist venv\Scripts\activate.bat (call venv\Scripts\activate.bat) else (echo WARNING: venv\Scripts\activate.bat does not exist.)) && (if defined VIRTUAL_ENV (echo [Backend] Virtual environment activated successfully.) else (echo [Backend] ERROR: Virtual environment is NOT activated!)) && echo [Backend] Current directory: %CD%\backend && echo [Backend] Starting server on port 8000... && python manage.py runserver 8000 || pause"

echo Starting Next.js frontend...
start "Frontend" cmd /k "cd frontend && echo [Frontend] Current directory: %CD%\frontend && echo [Frontend] Starting dev server... && npm run dev || pause"

echo Project services are starting in separate windows.
pause
