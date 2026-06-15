@echo off
REM ================================================================
REM Toggle Testing Mode - Enable/Disable Authentication
REM ================================================================

echo.
echo ========================================
echo  Testing Mode Toggle
echo ========================================
echo.
echo Choose an option:
echo.
echo  [1] DISABLE Authentication (Testing Mode ON)
echo  [2] ENABLE Authentication (Testing Mode OFF)
echo  [3] View Current Status
echo  [4] Exit
echo.
set /p choice="Enter choice (1-4): "

if "%choice%"=="1" goto :enable_testing
if "%choice%"=="2" goto :disable_testing
if "%choice%"=="3" goto :show_status
if "%choice%"=="4" goto :end
echo Invalid choice!
pause
exit /b 1

:enable_testing
echo.
echo Enabling Testing Mode (Disabling Authentication)...
echo.

REM Update frontend .env
powershell -Command "(Get-Content frontend\.env) -replace 'VITE_TESTING_MODE=false', 'VITE_TESTING_MODE=true' | Set-Content frontend\.env"

REM Update backend .env
powershell -Command "(Get-Content backend\.env) -replace 'TESTING_MODE=false', 'TESTING_MODE=true' | Set-Content backend\.env"

echo ✅ Testing Mode ENABLED
echo.
echo Status: Authentication DISABLED
echo Access: Direct (no login required)
echo.
echo Restarting services...
docker-compose restart >nul 2>&1
echo.
echo ========================================
echo  Ready for Testing!
echo ========================================
echo.
echo  Open: http://localhost:3000
echo  No login needed!
echo.
pause
goto :end

:disable_testing
echo.
echo Disabling Testing Mode (Enabling Authentication)...
echo.

REM Update frontend .env
powershell -Command "(Get-Content frontend\.env) -replace 'VITE_TESTING_MODE=true', 'VITE_TESTING_MODE=false' | Set-Content frontend\.env"

REM Update backend .env
powershell -Command "(Get-Content backend\.env) -replace 'TESTING_MODE=true', 'TESTING_MODE=false' | Set-Content backend\.env"

echo ✅ Testing Mode DISABLED
echo.
echo Status: Authentication ENABLED
echo Access: Login required
echo.
echo Login credentials:
echo   Email:    1111111@test.com
echo   Password: 1111111
echo.
echo Restarting services...
docker-compose restart >nul 2>&1
echo.
echo ========================================
echo  Authentication Active!
echo ========================================
echo.
echo  Open: http://localhost:3000
echo  Login required!
echo.
pause
goto :end

:show_status
echo.
echo ========================================
echo  Current Configuration
echo ========================================
echo.
echo Frontend (.env):
findstr "VITE_TESTING_MODE" frontend\.env
echo.
echo Backend (.env):
findstr "TESTING_MODE" backend\.env
echo.
echo ========================================
echo.
pause
goto :end

:end
exit /b 0
