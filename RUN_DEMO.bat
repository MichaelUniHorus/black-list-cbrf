@echo off
echo ========================================
echo OPEN BLACK - DEMO LAUNCHER
echo ========================================
echo.

echo Killing existing processes...
taskkill /IM python.exe /F 2>nul
taskkill /IM uvicorn.exe /F 2>nul
timeout /t 2 /nobreak >nul

cd backend

echo Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)

echo.
echo Installing dependencies...
pip install -q fastapi uvicorn sqlalchemy pydantic pydantic-settings httpx python-dotenv celery redis alembic

echo.
echo ========================================
echo Starting demo server...
echo ========================================
echo.

python run_demo.py

pause
