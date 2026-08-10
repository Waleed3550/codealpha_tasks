@echo off
echo Starting CA-Tech (Django) Development Server...

REM Check if python is available
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH. Please install Python.
    pause
    exit /b 1
)

REM Install missing requirements automatically
python -m pip install -r requirements.txt

REM Collect static files so CSS/JS changes are always picked up
echo Collecting static files...
python manage.py collectstatic --noinput

echo Running Django Server on http://127.0.0.1:8000/
python manage.py runserver

pause
