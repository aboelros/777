# Update to Dual Database Setup

Write-Host "🔧 Updating to Dual Database Setup..." -ForegroundColor Cyan
Write-Host ""

$envFile = "backend\.env"

if (-Not (Test-Path $envFile)) {
    Write-Host "ERROR: backend/.env not found!" -ForegroundColor Red
    Write-Host "Please copy backend/.env.example to backend/.env first" -ForegroundColor Yellow
    exit 1
}

# Read current .env
$envContent = Get-Content $envFile -Raw

# Check if already has dual database setup
if ($envContent -match "AUTH_DATABASE_URL" -and $envContent -match "APP_DATABASE_URL") {
    Write-Host "✅ Already using dual database setup!" -ForegroundColor Green
    exit 0
}

Write-Host "📝 Adding dual database configuration..." -ForegroundColor Yellow

# Get existing DATABASE_URL if it exists
$existingDb = ""
if ($envContent -match "DATABASE_URL=(.+)") {
    $existingDb = $matches[1].Trim()
    Write-Host "Found existing DATABASE_URL: $existingDb" -ForegroundColor Gray
}

# Default values
$authDb = "postgresql+asyncpg://aisales:changeme@postgres:5432/aisales_auth"
$appDb = "postgresql+asyncpg://aisales:changeme@postgres:5432/aisales_app"

# If existing DATABASE_URL found, derive from it
if ($existingDb -ne "") {
    # Replace database name
    $authDb = $existingDb -replace "/aisales$", "/aisales_auth"
    $appDb = $existingDb -replace "/aisales$", "/aisales_app"
}

# Comment out old DATABASE_URL
$envContent = $envContent -replace "^DATABASE_URL=", "# DATABASE_URL="

# Add new database URLs after the commented line
$newConfig = @"

# Dual Database Architecture (Updated)
# Auth Database (users, authentication)
AUTH_DATABASE_URL=$authDb
# Application Database (projects, orders, messages, etc.)
APP_DATABASE_URL=$appDb

"@

# Insert after DATABASE section
if ($envContent -match "# Database") {
    $envContent = $envContent -replace "(# Database[^\r\n]*[\r\n]+)", "`$1$newConfig"
} else {
    $envContent += $newConfig
}

# Save updated .env
$envContent | Set-Content $envFile

Write-Host ""
Write-Host "✅ Configuration updated successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "New databases:" -ForegroundColor Cyan
Write-Host "  📧 AUTH: $authDb" -ForegroundColor White
Write-Host "  📊 APP:  $appDb" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Stop containers: docker-compose down" -ForegroundColor White
Write-Host "  2. Remove old volume: docker volume rm 'bot trial 2_postgres_data'" -ForegroundColor White
Write-Host "  3. Start fresh: docker-compose up -d" -ForegroundColor White
Write-Host ""
Write-Host "The system will automatically create both databases!" -ForegroundColor Cyan
