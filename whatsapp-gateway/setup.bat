@echo off
echo Installing WhatsApp Baileys Gateway...
echo.

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Node.js is not installed!
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo Node.js version:
node --version
echo.

REM Install dependencies
echo Installing dependencies...
call npm install

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error: Failed to install dependencies!
    pause
    exit /b 1
)

echo.
echo ✅ Installation complete!
echo.

REM Create .env if it doesn't exist
if not exist .env (
    echo Creating .env file...
    copy .env.example .env
    echo.
    echo ⚠️  Please edit .env and set your API keys!
    echo.
)

echo To start the server, run:
echo   npm start
echo.
echo Or for development mode:
echo   npm run dev
echo.

pause
