# Add 24 MORE Gemini API Keys (Total will be 44 keys!)

$envFile = "backend\.env"

Write-Host "Adding 24 more Gemini API Keys..." -ForegroundColor Cyan

if (-Not (Test-Path $envFile)) {
    Write-Host "ERROR: .env file not found!" -ForegroundColor Red
    exit 1
}

# Read current .env content
$envContent = Get-Content $envFile -Raw

# Add new keys 20-43
$newKeys = @"

# Additional Keys 20-43 (24 more keys!)
GEMINI_API_KEY_20=AIzaSyBcL0jEFeOWUuUGt-4ZgzrZOBwfoptufOo
GEMINI_API_KEY_21=AIzaSyCztSF4_xn3ivXxC-Zag2QKxKIjzfjtWEU
GEMINI_API_KEY_22=AIzaSyASkB8fo062UUnb9P3Z434AzTu-IIeQ3I4
GEMINI_API_KEY_23=AIzaSyBqs-4Yu7LuK4iRo3jNXQsQbIPPrWxvDDU
GEMINI_API_KEY_24=AIzaSyCLGb2ahrSdQB5DFPy3OeH0qo0yC81B05A
GEMINI_API_KEY_25=AIzaSyBa0X2SalpIIu2Ui4DMY3zbHCL758nMjfc
GEMINI_API_KEY_26=AIzaSyCTrLvxr6NLzvm2rJ2JBvV3s8YqQOqBkPo
GEMINI_API_KEY_27=AIzaSyCK6cUYOJrL_Rsedkxxtn5_xiOpebbGySo
GEMINI_API_KEY_28=AIzaSyB3TQSqKKCdCQOzWQErJcFGkx-v2vFzBvk
GEMINI_API_KEY_29=AIzaSyDwrmjZcwmwFNhZovZw7TRumx7aYv_5PFg
GEMINI_API_KEY_30=AIzaSyBqX5MLHGNHFzMPIcfaUBSHG_u9I_RMyTw
GEMINI_API_KEY_31=AIzaSyAGkUQfdrccRZmPXvDcJHfIMcezdB-ZILU
GEMINI_API_KEY_32=AIzaSyB3-vyjBPd4C2cuqoW8l7fnLRZwZCrQdjg
GEMINI_API_KEY_33=AIzaSyB9b_tRAGaO7h4OZ5GZB7SZ5naw_2XxnXg
GEMINI_API_KEY_34=AIzaSyDDNgL_Y7gcDL0XbvgpILhymBz87WdAllg
GEMINI_API_KEY_35=AIzaSyD6c8K-29M6rHkafM5hkYqDtuoUk_8vmaU
GEMINI_API_KEY_36=AIzaSyC7TLNgDzSa9wUeVMv6XZqIzWMo2un4ELQ
GEMINI_API_KEY_37=AIzaSyAfhZGN3WNZ7-VVyEYU0Kc2_AKLfY6TYYs
GEMINI_API_KEY_38=AIzaSyCKhY2jfioBLgf6o5ZH-nn9Zz9hu8sTbiQ
GEMINI_API_KEY_39=AIzaSyAaueTsJpTIYI7C9e1H76Bl8wzMX8tGLHg
GEMINI_API_KEY_40=AIzaSyBqfHBsGeaIUR7A4zttZnToFmU6I4xMChI
GEMINI_API_KEY_41=AIzaSyABf7tIMZDjSFDMyRmOrUDYZp98AfZ-9hY
GEMINI_API_KEY_42=AIzaSyCw7gMM-8J_8KL1YowUSnY-NGa-R220qEM
GEMINI_API_KEY_43=AIzaSyB7BMizW3evWKF7Aq6nWnfM0n3AQ2Qr3Go
"@

# Append new keys
$envContent + $newKeys | Set-Content $envFile

Write-Host "SUCCESS: Added 24 more API keys!" -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "NEW TOTAL: 44 API KEYS!" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "MASSIVE CAPACITY:" -ForegroundColor Cyan
Write-Host "   • 44 API keys total" -ForegroundColor White
Write-Host "   • 2,640 requests/minute" -ForegroundColor Yellow
Write-Host "   • 158,400 requests/hour" -ForegroundColor Yellow
Write-Host "   • 3,801,600 requests/day" -ForegroundColor Yellow
Write-Host "   • 114,048,000 requests/month!" -ForegroundColor Green
Write-Host ""
Write-Host "Restarting backend..." -ForegroundColor Yellow

docker-compose restart backend

Write-Host ""
Write-Host "DONE! Backend now has 44 API keys!" -ForegroundColor Green
Write-Host "You are now running at ENTERPRISE SCALE!" -ForegroundColor Cyan
