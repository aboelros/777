@echo off
REM ================================================================
REM AI Sales Commander - Quick Start Script (Windows)
REM ================================================================

echo.
echo ========================================
echo  AI Sales Commander - Starting Server
echo ========================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo [1/5] Checking environment files...
if not exist "backend\.env" (
    echo Creating backend .env from template...
    copy "backend\.env.example" "backend\.env" >nul
    echo [WARNING] Please configure backend\.env with your settings!
)

if not exist "frontend\.env" (
    echo Creating frontend .env from template...
    copy "frontend\.env.example" "frontend\.env" >nul
    echo [INFO] Testing mode enabled - authentication disabled!
)

echo [2/5] Starting Docker containers...
docker-compose up -d

echo.
echo [3/5] Waiting for services to be ready...
timeout /t 10 /nobreak >nul

echo [4/5] Checking database migrations...
docker-compose exec -T backend alembic upgrade head

echo.
echo [5/5] All done!
echo.
echo ========================================
echo  Server is running!
echo ========================================
echo.
echo  Frontend: http://localhost:3000
echo  Backend:  http://localhost:8000
echo  API Docs: http://localhost:8000/docs
echo  Flower:   http://localhost:5555
echo.
echo ========================================
echo  TESTING MODE ACTIVE
echo ========================================
echo.
echo  Authentication: DISABLED
echo  Access:         Direct (no login needed)
echo  Status:         Ready for testing
echo.
echo  Just open: http://localhost:3000
echo.
echo ========================================
echo  (Login disabled - can be re-enabled)
echo ========================================
echo.
echo Press Ctrl+C to stop, or close this window.
echo To view logs: docker-compose logs -f
echo.

REM Keep window open and show logs
docker-compose logs -f
