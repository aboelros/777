# Setup Supabase Databases for AI Sales Commander

Write-Host "Configuring Supabase Databases..." -ForegroundColor Cyan
Write-Host ""

$envFile = "backend\.env"
$envExample = "backend\.env.example"

# Check if .env exists, if not copy from .env.example
if (-Not (Test-Path $envFile)) {
    Write-Host "Creating backend/.env from .env.example..." -ForegroundColor Yellow
    Copy-Item $envExample $envFile
    Write-Host "backend/.env created!" -ForegroundColor Green
    Write-Host ""
}

# Read current .env
$envContent = Get-Content $envFile -Raw

# Supabase Database URLs
$authDbUrl = "postgresql+asyncpg://postgres:10052008mariem@db.gznafnmgtrgtlxzxxbzy.supabase.co:5432/postgres"
$appDbUrl = "postgresql+asyncpg://postgres:10052008mariem@db.vjdbthhdyemeugyhucoq.supabase.co:5432/postgres"

Write-Host "Database Configuration:" -ForegroundColor Cyan
Write-Host "  AUTH DB: gznafnmgtrgtlxzxxbzy.supabase.co" -ForegroundColor White
Write-Host "  APP DB:  vjdbthhdyemeugyhucoq.supabase.co" -ForegroundColor White
Write-Host ""

# Update AUTH_DATABASE_URL
if ($envContent -match "AUTH_DATABASE_URL=.*") {
    $envContent = $envContent -replace "AUTH_DATABASE_URL=.*", "AUTH_DATABASE_URL=$authDbUrl"
    Write-Host "Updated AUTH_DATABASE_URL" -ForegroundColor Green
} else {
    $envContent += "`nAUTH_DATABASE_URL=$authDbUrl`n"
    Write-Host "Added AUTH_DATABASE_URL" -ForegroundColor Green
}

# Update APP_DATABASE_URL
if ($envContent -match "APP_DATABASE_URL=.*") {
    $envContent = $envContent -replace "APP_DATABASE_URL=.*", "APP_DATABASE_URL=$appDbUrl"
    Write-Host "Updated APP_DATABASE_URL" -ForegroundColor Green
} else {
    $envContent += "APP_DATABASE_URL=$appDbUrl`n"
    Write-Host "Added APP_DATABASE_URL" -ForegroundColor Green
}

# Save updated .env
$envContent | Set-Content $envFile -NoNewline

Write-Host ""
Write-Host "Configuration Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Summary:" -ForegroundColor Cyan
Write-Host "  Auth Database:    Supabase (250MB FREE)" -ForegroundColor White
Write-Host "  App Database:     Supabase (250MB FREE)" -ForegroundColor White
Write-Host "  Total Storage:    500MB FREE" -ForegroundColor White
Write-Host "  Cost:             0 dollars per month" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Start app: docker-compose up -d" -ForegroundColor White
Write-Host ""
Write-Host "Your app is now connected to Supabase cloud databases!" -ForegroundColor Cyan
