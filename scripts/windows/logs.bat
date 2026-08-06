@echo off
REM ================================================================
REM AI Sales Commander - View Logs
REM ================================================================

echo.
echo Select which logs to view:
echo.
echo 1. All services
echo 2. Backend only
echo 3. Frontend only
echo 4. Database only
echo 5. Workers only
echo.
set /p choice="Enter choice (1-5): "

if "%choice%"=="1" (
    docker-compose logs -f
) else if "%choice%"=="2" (
    docker-compose logs -f backend
) else if "%choice%"=="3" (
    docker-compose logs -f frontend
) else if "%choice%"=="4" (
    docker-compose logs -f postgres
) else if "%choice%"=="5" (
    docker-compose logs -f celery-worker celery-beat
) else (
    echo Invalid choice!
    pause
)
