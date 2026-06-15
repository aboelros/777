@echo off
echo ========================================
echo Running Backend WITHOUT Docker
echo ========================================
echo.
echo This bypasses Docker networking issues!
echo.

cd backend

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Starting backend server...
echo Backend will run on: http://localhost:8000
echo.

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
