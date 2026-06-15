# Add 8 MORE Gemini API Keys (Total will be 20 keys!)

$envFile = "backend\.env"

Write-Host "Adding 8 more Gemini API Keys..." -ForegroundColor Cyan

if (-Not (Test-Path $envFile)) {
    Write-Host "ERROR: .env file not found!" -ForegroundColor Red
    exit 1
}

# Read current .env content
$envContent = Get-Content $envFile -Raw

# Add new keys 12-19
$newKeys = @"

# Additional Keys 12-19 (8 more keys!)
GEMINI_API_KEY_12=AIzaSyClyBUKXO30LFQt_ulNVedWW17eL-FHSP0
GEMINI_API_KEY_13=AIzaSyAZaMJsxDN7_to5RH0byKFhoBLOeDev45Y
GEMINI_API_KEY_14=AIzaSyBJpk3Dopj4iFTV5el3owDxB5dZscsekNU
GEMINI_API_KEY_15=AIzaSyBAa67DnLNYFm74lpo0DQRapz_kF3PTHFY
GEMINI_API_KEY_16=AIzaSyDhi4yq9YYW7dUCQXkfOZIvLHphJ-V3VKk
GEMINI_API_KEY_17=AIzaSyBe4eU6VBxsljylyKSWT-pXxiRoQOwZCdI
GEMINI_API_KEY_18=AIzaSyBD1IVIpy2mAjbZwNhkK-n9sG31C42R8zs
GEMINI_API_KEY_19=AIzaSyCVsjBt1jg03qXpYtezXijZUOLszHeYAD8
"@

# Append new keys
$envContent + $newKeys | Set-Content $envFile

Write-Host "SUCCESS: Added 8 more API keys!" -ForegroundColor Green
Write-Host ""
Write-Host "NEW TOTAL:" -ForegroundColor Cyan
Write-Host "   • 20 API keys total" -ForegroundColor White
Write-Host "   • 1,200 requests/minute" -ForegroundColor Yellow
Write-Host "   • 72,000 requests/hour" -ForegroundColor Yellow
Write-Host "   • 1,728,000 requests/day" -ForegroundColor Yellow
Write-Host ""
Write-Host "Restarting backend..." -ForegroundColor Yellow

docker-compose restart backend

Write-Host ""
Write-Host "DONE! Backend now has 20 API keys!" -ForegroundColor Green
