@echo off
REM Quick verification script for SkillNavigator (Windows)
echo =========================================
echo    SkillNavigator Quick Verification
echo =========================================

echo.
echo [1/5] Checking Python environment...
python --version
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found or not in PATH
    pause
    exit /b 1
)

echo.
echo [2/5] Checking project files...
if not exist "backend\main.py" (
    echo ERROR: backend\main.py not found
    pause
    exit /b 1
)
if not exist "requirements.txt" (
    echo ERROR: requirements.txt not found
    pause
    exit /b 1
)
echo OK: Core project files found

echo.
echo [3/5] Checking database...
if not exist "skillnavigator.db" (
    echo INFO: Database not found, initializing...
    python scripts\init_db.py
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Database initialization failed
        pause
        exit /b 1
    )
) else (
    echo OK: Database file exists
)

echo.
echo [4/5] Checking configuration...
if not exist ".env" (
    echo WARNING: .env file not found
    echo Creating from .env.example...
    copy .env.example .env >nul
    echo IMPORTANT: Edit .env file with your API keys!
) else (
    echo OK: .env file exists
)

echo.
echo [5/5] Running comprehensive verification...
python scripts\verify_system.py

echo.
echo =========================================
echo Verification complete!
echo.
echo To start the server:
echo   python -m uvicorn backend.main:app --reload
echo.
echo To test API:
echo   python scripts\test_api.py
echo.
echo API Documentation:
echo   http://localhost:8000/docs
echo =========================================
pause
