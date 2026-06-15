# PowerShell Script to Update Gemini API Keys in .env file
# Run this script to automatically add your 12 Gemini API keys

$envFile = "backend\.env"

Write-Host "🔑 Updating Gemini API Keys in $envFile..." -ForegroundColor Cyan

# Check if .env exists
if (-Not (Test-Path $envFile)) {
    Write-Host "❌ Error: $envFile not found!" -ForegroundColor Red
    Write-Host "📝 Creating .env from .env.example..." -ForegroundColor Yellow
    Copy-Item "backend\.env.example" $envFile
}

# Read current .env content
$envContent = Get-Content $envFile

# Remove old GEMINI_API_KEY lines
$envContent = $envContent | Where-Object { $_ -notmatch "^GEMINI_API_KEY" }

# Add new API keys
$geminiKeys = @"

# ===== GEMINI API KEYS (12 keys = 720 req/min) =====
GEMINI_API_KEY=AIzaSyBG5xvEO2APM2UFNgKsmrvECylnRsYnDpg
GEMINI_API_KEY_1=AIzaSyCHgELRACD-xYeI6q_UJNy7OKaZUq52lWM
GEMINI_API_KEY_2=AIzaSyCph-7MtU2XDeVS6AdmSZ_zot0tY__8Nag
GEMINI_API_KEY_3=AIzaSyBwwE2E9y4XkzoPqEZI7btEBO9UpM5PCCk
GEMINI_API_KEY_4=AIzaSyCCmePVW8xWpNJ4up17TKopTY-U3yRs4mc
GEMINI_API_KEY_5=AIzaSyD2ofs2bp0YijCJKdPld6-qkBxwpaxkBAY
GEMINI_API_KEY_6=AIzaSyDnqNvIXqjsT9If1x5-DPeJ7oDMzmrF3iE
GEMINI_API_KEY_7=AIzaSyBIxJ0BOsjRAHRs9mLfvaLfdde3lfjY5w8
GEMINI_API_KEY_8=AIzaSyATwKEiuLLme0OGyegsKmuupyNiLQNYoqU
GEMINI_API_KEY_9=AIzaSyAGe4YoIxS2hBCgGvta7SubR2aKqExbNQE
GEMINI_API_KEY_10=AIzaSyC6hg_lsmnmHt0NvbiyD-TsEq2aEOtdAxw
GEMINI_API_KEY_11=AIzaSyDcKyWxZwA7cdD1ob5LzsDY3FXgB4IBJXM
"@

# Write updated content
$envContent + $geminiKeys | Set-Content $envFile

Write-Host "✅ Successfully added 12 Gemini API keys!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Your new capacity:" -ForegroundColor Cyan
Write-Host "   • 12 API keys" -ForegroundColor White
Write-Host "   • 720 requests/minute" -ForegroundColor White
Write-Host "   • 43,200 requests/hour" -ForegroundColor White
Write-Host "   • 1,036,800 requests/day" -ForegroundColor White
Write-Host ""
Write-Host "🔄 Restarting backend container..." -ForegroundColor Yellow

# Restart backend
docker-compose restart backend

Write-Host ""
Write-Host "🎉 Done! Your AI bot now has 12 API keys with automatic rotation!" -ForegroundColor Green
Write-Host "💡 Check logs with: docker-compose logs backend" -ForegroundColor Gray
