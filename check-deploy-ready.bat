@echo off
echo ========================================
echo   Railway Deployment Readiness Check
echo ========================================
echo.

set READY=1

echo [1/8] Checking Git repository...
if exist .git\ (
    echo [OK] Git repository initialized
) else (
    echo [!] Git not initialized - Run: git init
    set READY=0
)
echo.

echo [2/8] Checking backend files...
if exist backend\Procfile (
    echo [OK] Procfile exists
) else (
    echo [!] Procfile missing
    set READY=0
)
if exist backend\requirements.txt (
    echo [OK] requirements.txt exists
) else (
    echo [!] requirements.txt missing
    set READY=0
)
if exist backend\railway.json (
    echo [OK] railway.json exists
) else (
    echo [!] railway.json missing
    set READY=0
)
if exist backend\nixpacks.toml (
    echo [OK] nixpacks.toml exists
) else (
    echo [!] nixpacks.toml missing
    set READY=0
)
echo.

echo [3/8] Checking frontend files...
if exist frontend\package.json (
    echo [OK] package.json exists
) else (
    echo [!] package.json missing
    set READY=0
)
if exist frontend\vite.config.js (
    echo [OK] vite.config.js exists
) else (
    echo [!] vite.config.js missing
    set READY=0
)
if exist frontend\nixpacks.toml (
    echo [OK] nixpacks.toml exists
) else (
    echo [!] nixpacks.toml missing
    set READY=0
)
echo.

echo [4/8] Checking configuration files...
if exist .gitignore (
    echo [OK] .gitignore exists
) else (
    echo [!] .gitignore missing
    set READY=0
)
if exist .railwayignore (
    echo [OK] .railwayignore exists
) else (
    echo [!] .railwayignore missing
    set READY=0
)
echo.

echo [5/8] Checking documentation...
if exist RAILWAY_DEPLOYMENT.md (
    echo [OK] RAILWAY_DEPLOYMENT.md exists
) else (
    echo [!] RAILWAY_DEPLOYMENT.md missing
    set READY=0
)
if exist RAILWAY_QUICK_START.md (
    echo [OK] RAILWAY_QUICK_START.md exists
) else (
    echo [!] RAILWAY_QUICK_START.md missing
    set READY=0
)
if exist railway.env.example (
    echo [OK] railway.env.example exists
) else (
    echo [!] railway.env.example missing
    set READY=0
)
echo.

echo [6/8] Checking for sensitive files...
if exist backend\.env (
    echo [WARN] .env file exists - Make sure it's in .gitignore!
) else (
    echo [OK] No .env file to accidentally commit
)
echo.

echo [7/8] Checking Git remote...
git remote -v >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Git remote configured
    git remote -v
) else (
    echo [!] No Git remote configured
    echo     Run: git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
    set READY=0
)
echo.

echo [8/8] Summary...
echo.
if %READY% equ 1 (
    echo ========================================
    echo   ALL CHECKS PASSED! READY TO DEPLOY!
    echo ========================================
    echo.
    echo Next Steps:
    echo 1. Run: deploy-to-railway.bat
    echo 2. Go to https://railway.app
    echo 3. Click "New Project"
    echo 4. Select "Deploy from GitHub repo"
    echo 5. Configure environment variables
    echo.
    echo See RAILWAY_QUICK_START.md for quick guide!
) else (
    echo ========================================
    echo   SOME CHECKS FAILED - FIX ISSUES ABOVE
    echo ========================================
    echo.
    echo Please fix the issues marked with [!]
    echo Then run this check again.
)
echo.
pause
