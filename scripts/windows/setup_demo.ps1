# Setup Demo Data for AI Sales Commander
# Run this script to populate the database with test data

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " AI Sales Commander - Demo Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "[1/4] Checking Docker..." -ForegroundColor Yellow
$dockerRunning = docker ps 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}
Write-Host "✅ Docker is running" -ForegroundColor Green

# Check if containers are up
Write-Host ""
Write-Host "[2/4] Checking containers..." -ForegroundColor Yellow
docker-compose ps
Write-Host ""

# Run database migrations
Write-Host "[3/4] Running database migrations..." -ForegroundColor Yellow
docker-compose exec backend alembic upgrade head
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Database migrations complete" -ForegroundColor Green
} else {
    Write-Host "⚠️  Migration warning (may already be up to date)" -ForegroundColor Yellow
}

# Create test data
Write-Host ""
Write-Host "[4/4] Creating test data..." -ForegroundColor Yellow
docker-compose exec backend python scripts/create_test_data.py

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " Demo Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Login Credentials:" -ForegroundColor Cyan
Write-Host "   Email: 1111111@test.com" -ForegroundColor White
Write-Host "   Password: 1111111" -ForegroundColor White
Write-Host ""
Write-Host "🌐 Access Points:" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "   Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "📚 Documentation:" -ForegroundColor Cyan
Write-Host "   User Guide: USER_GUIDE.md" -ForegroundColor White
Write-Host "   Features List: FEATURES.md" -ForegroundColor White
Write-Host "   API Docs: API_DOCUMENTATION.md" -ForegroundColor White
Write-Host ""
Write-Host "🎉 Ready to explore!" -ForegroundColor Green
Write-Host ""
