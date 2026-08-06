@echo off
echo ========================================
echo   AI Sales Commander - Railway Deploy
echo ========================================
echo.

echo [1/4] Checking Git status...
git status
echo.

echo [2/4] Adding all files...
git add .
echo.

echo [3/4] Creating commit...
set /p commit_message="Enter commit message (or press Enter for default): "
if "%commit_message%"=="" set commit_message=Deploy to Railway

git commit -m "%commit_message%"
echo.

echo [4/4] Pushing to GitHub...
echo.
echo NOTE: Make sure you have created a GitHub repository first!
echo Then run: git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
echo.

choice /C YN /M "Do you want to push to GitHub now"
if errorlevel 2 goto :skip
if errorlevel 1 goto :push

:push
git push origin main
echo.
echo ========================================
echo   SUCCESS! Code pushed to GitHub!
echo ========================================
echo.
echo Next Steps:
echo 1. Go to https://railway.app
echo 2. Click "New Project"
echo 3. Select "Deploy from GitHub repo"
echo 4. Choose your repository
echo 5. Configure environment variables
echo.
echo See RAILWAY_DEPLOYMENT.md for full instructions!
pause
exit

:skip
echo.
echo Push skipped. Run manually:
echo   git push origin main
echo.
pause
