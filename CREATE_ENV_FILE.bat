@echo off
REM Create backend/.env file with Supabase configuration

echo Creating backend/.env file with Supabase databases...

(
echo # ============================================================================
echo # DATABASE CONFIGURATION - DUAL DATABASE WITH SUPABASE
echo # ============================================================================
echo.
echo # Auth Database ^(Supabase - users and authentication^)
echo AUTH_DATABASE_URL=postgresql+asyncpg://postgres:10052008mariem@db.gznafnmgtrgtlxzxxbzy.supabase.co:5432/postgres
echo.
echo # Application Database ^(Supabase - projects, orders, messages^)
echo APP_DATABASE_URL=postgresql+asyncpg://postgres:10052008mariem@db.vjdbthhdyemeugyhucoq.supabase.co:5432/postgres
echo.
echo # Connection Pool Settings
echo DB_POOL_SIZE=20
echo DB_MAX_OVERFLOW=0
echo DB_ECHO=false
echo.
echo # ============================================================================
echo # APPLICATION CONFIGURATION
echo # ============================================================================
echo.
echo APP_NAME=AI Sales Commander
echo ENVIRONMENT=development
echo DEBUG=true
echo API_VERSION=v1
echo HOST=0.0.0.0
echo PORT=8000
echo.
echo # ============================================================================
echo # SECURITY
echo # ============================================================================
echo.
echo SECRET_KEY=your-super-secret-jwt-key-change-this-in-production-min-32-chars
echo ALGORITHM=HS256
echo ACCESS_TOKEN_EXPIRE_MINUTES=15
echo REFRESH_TOKEN_EXPIRE_DAYS=7
echo.
echo # ============================================================================
echo # CORS
echo # ============================================================================
echo.
echo CORS_ORIGINS=http://localhost:3000,http://localhost:8000
echo.
echo # ============================================================================
echo # GEMINI AI API
echo # ============================================================================
echo.
echo GEMINI_API_KEY=AIzaSyAqai9GTZ7ebu0k7kl0Jdrh9zADo_lGfxM
echo GEMINI_MODEL=gemini-1.5-pro-latest
echo.
echo # ============================================================================
echo # REDIS ^(handled by docker-compose^)
echo # ============================================================================
echo.
echo REDIS_URL=redis://redis:6379/0
echo CELERY_BROKER_URL=redis://redis:6379/1
echo CELERY_RESULT_BACKEND=redis://redis:6379/2
echo.
echo # ============================================================================
echo # TESTING
echo # ============================================================================
echo.
echo TESTING_MODE=false
) > backend\.env

echo.
echo ========================================
echo SUCCESS! backend/.env file created!
echo ========================================
echo.
echo Your Supabase databases are configured:
echo   Auth DB: gznafnmgtrgtlxzxxbzy.supabase.co
echo   App DB:  vjdbthhdyemeugyhucoq.supabase.co
echo.
echo Now restart your containers:
echo   docker-compose down
echo   docker-compose up -d
echo.
pause
