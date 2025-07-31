#!/bin/bash
# Quick verification script for SkillNavigator (Linux/Mac)

echo "========================================="
echo "   SkillNavigator Quick Verification"
echo "========================================="

echo
echo "[1/5] Checking Python environment..."
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "ERROR: Python not found"
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

$PYTHON_CMD --version

echo
echo "[2/5] Checking project files..."
if [ ! -f "backend/main.py" ]; then
    echo "ERROR: backend/main.py not found"
    exit 1
fi
if [ ! -f "requirements.txt" ]; then
    echo "ERROR: requirements.txt not found"
    exit 1
fi
echo "OK: Core project files found"

echo
echo "[3/5] Checking database..."
if [ ! -f "skillnavigator.db" ]; then
    echo "INFO: Database not found, initializing..."
    $PYTHON_CMD scripts/init_db.py
    if [ $? -ne 0 ]; then
        echo "ERROR: Database initialization failed"
        exit 1
    fi
else
    echo "OK: Database file exists"
fi

echo
echo "[4/5] Checking configuration..."
if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found"
    echo "Creating from .env.example..."
    cp .env.example .env
    echo "IMPORTANT: Edit .env file with your API keys!"
else
    echo "OK: .env file exists"
fi

echo
echo "[5/5] Running comprehensive verification..."
$PYTHON_CMD scripts/verify_system.py

echo
echo "========================================="
echo "Verification complete!"
echo
echo "To start the server:"
echo "  $PYTHON_CMD -m uvicorn backend.main:app --reload"
echo
echo "To test API:"
echo "  $PYTHON_CMD scripts/test_api.py"
echo
echo "API Documentation:"
echo "  http://localhost:8000/docs"
echo "========================================="
