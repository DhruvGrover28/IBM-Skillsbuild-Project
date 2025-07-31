#!/bin/bash
# SkillNavigator Startup Script for Linux/Mac

echo "Starting SkillNavigator..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Install playwright browsers
echo "Installing Playwright browsers..."
playwright install chromium

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "Please edit .env file with your API keys and configuration"
    read -p "Press Enter to continue..."
fi

# Initialize database if it doesn't exist
if [ ! -f "skillnavigator.db" ]; then
    echo "Initializing database with sample data..."
    python scripts/init_db.py
fi

# Start the application
echo "Starting SkillNavigator backend..."
python -m uvicorn backend.main:app --reload --host localhost --port 8000
