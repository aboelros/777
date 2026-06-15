@echo off
REM Delete stuck WhatsApp instance from Evolution API

echo Deleting instance: ad55fd22-354a-47d5-a14b-5ee642dd9d3b_cfdb5cc5-391e-4aa6-9d9b-44ef0b823c7d
echo.

curl -X DELETE ^
  "https://evolution-api-production-8585.up.railway.app/instance/delete/ad55fd22-354a-47d5-a14b-5ee642dd9d3b_cfdb5cc5-391e-4aa6-9d9b-44ef0b823c7d" ^
  -H "apikey: whatsapp-secret-key-123"

echo.
echo Done! Now try connecting WhatsApp again from your frontend.
pause
