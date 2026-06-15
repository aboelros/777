@echo off
echo Starting WhatsApp Baileys Gateway...
echo.

REM Check if .env exists
if not exist .env (
    echo Error: .env file not found!
    echo Please copy .env.example to .env and configure it.
    pause
    exit /b 1
)

REM Check if node_modules exists
if not exist node_modules (
    echo Error: Dependencies not installed!
    echo Please run setup.bat first.
    pause
    exit /b 1
)

echo Starting server...
call npm start
