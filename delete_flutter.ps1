# Delete Flutter App Files

Write-Host "Deleting Flutter app files..." -ForegroundColor Yellow

# Delete flutter-app folder
if (Test-Path "flutter-app") {
    Remove-Item -Path "flutter-app" -Recurse -Force
    Write-Host "Deleted: flutter-app/" -ForegroundColor Green
}

# Delete Flutter documentation files
$flutterDocs = @(
    "FLUTTER_APP_ALL_CODE.md",
    "FLUTTER_QUICK_START.md",
    "FLUTTER_APP_COMPLETE.md",
    "SOURCE_CODE_PART2.md"
)

foreach ($file in $flutterDocs) {
    if (Test-Path $file) {
        Remove-Item -Path $file -Force
        Write-Host "Deleted: $file" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "Flutter app deleted!" -ForegroundColor Cyan
