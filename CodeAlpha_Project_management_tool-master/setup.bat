@echo off
echo Setting up Project Management Tool...

echo [1/2] Setting up Django backend...
cd backend
if exist venv (
    echo Removing old virtual environment...
    rmdir /s /q venv
)
echo Creating new virtual environment...
python -m venv venv
echo Activating virtual environment and installing dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org
cd ..

echo [2/2] Setting up Next.js frontend...
cd frontend
echo Installing npm dependencies...
call npm install --legacy-peer-deps
cd ..

echo Setup complete! You can now use run.bat to start the servers.
pause
