@echo off
REM SkillNavigator Startup Script for Windows
echo Starting SkillNavigator...

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Install playwright browsers
echo Installing Playwright browsers...
playwright install chromium

REM Check if .env file exists
if not exist ".env" (
    echo Creating .env file from .env.example...
    copy .env.example .env
    echo Please edit .env file with your API keys and configuration
    pause
)

REM Initialize database if it doesn't exist
if not exist "skillnavigator.db" (
    echo Initializing database with sample data...
    python scripts\init_db.py
)

REM Start the application
echo Starting SkillNavigator backend...
python -m uvicorn backend.main:app --reload --host localhost --port 8000

pause
