@echo off
REM ================================================================
REM AI Sales Commander - Stop Server
REM ================================================================

echo.
echo ========================================
echo  Stopping AI Sales Commander
echo ========================================
echo.

docker-compose down

echo.
echo [SUCCESS] All services stopped!
echo.
pause
