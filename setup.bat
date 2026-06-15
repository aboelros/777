@echo off
REM ================================================================
REM AI Sales Commander - First Time Setup
REM ================================================================

echo.
echo ========================================
echo  AI Sales Commander - First Time Setup
echo ========================================
echo.

REM Check Docker
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo [1/4] Creating environment files...
if not exist "backend\.env" (
    copy "backend\.env.example" "backend\.env"
    echo Created backend\.env
) else (
    echo backend\.env already exists
)

if not exist "frontend\.env" (
    copy "frontend\.env.example" "frontend\.env"
    echo Created frontend\.env
) else (
    echo frontend\.env already exists
)

echo.
echo [2/4] Generating SECRET_KEY...
cd backend
python scripts\generate_secret_key.py > secret_key.txt
echo SECRET_KEY saved to backend\secret_key.txt
echo Please copy it to backend\.env
cd ..

echo.
echo [3/4] Starting services...
docker-compose up -d

echo.
echo [4/4] Waiting for services...
timeout /t 15 /nobreak >nul

echo.
echo Running database migrations...
docker-compose exec -T backend alembic upgrade head

echo.
echo ========================================
echo  Setup Complete!
echo ========================================
echo.
echo IMPORTANT: Configure the following in backend\.env:
echo   1. SECRET_KEY (see backend\secret_key.txt)
echo   2. GOOGLE_CLOUD_PROJECT
echo   3. GOOGLE_API_KEY or GOOGLE_APPLICATION_CREDENTIALS
echo.
echo After configuration, restart with: run.bat
echo.
pause
