@echo off
REM ================================================================
REM AI Sales Commander - Development Mode (Without Docker)
REM Run backend and frontend separately for faster development
REM ================================================================

echo.
echo ========================================
echo  AI Sales Commander - Development Mode
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    echo Please install Python 3.11+ and try again.
    pause
    exit /b 1
)

REM Check if Node is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed!
    echo Please install Node.js 20+ and try again.
    pause
    exit /b 1
)

echo [INFO] Starting PostgreSQL and Redis with Docker...
docker-compose up -d postgres redis

echo.
echo [INFO] Waiting for database to be ready...
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo  Starting Backend and Frontend
echo ========================================
echo.
echo Backend will run on: http://localhost:8000
echo Frontend will run on: http://localhost:3000
echo.
echo Press Ctrl+C in each window to stop
echo.

REM Start backend in new window
start "Backend Server" cmd /k "cd backend && python -m venv venv 2>nul && call venv\Scripts\activate && pip install -q -r requirements.txt && uvicorn app.main:app --reload"

REM Wait a bit for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend in new window
start "Frontend Server" cmd /k "cd frontend && npm install && npm run dev"

echo.
echo [SUCCESS] Servers are starting in separate windows!
echo.
pause
