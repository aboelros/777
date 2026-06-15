# Evolution API - Railway Deployment Guide

## Quick Deploy (Easiest Method)

### Option 1: One-Click Deploy Button

1. Go to: https://railway.app/template/evolution-api
2. Click "Deploy Now"
3. Set your API key when prompted
4. Click "Deploy"
5. Done! ✅

### Option 2: Manual Deploy via Railway Dashboard

1. **Go to Railway**: https://railway.app/dashboard
2. **Click "New Project"**
3. **Select "Deploy from GitHub repo"**
4. **Search**: `EvolutionAPI/evolution-api`
5. **Click the repository** to deploy
6. **Add Environment Variables**:
   - Click on the service
   - Go to "Variables" tab
   - Add:
     ```
     AUTHENTICATION_API_KEY=your-secret-key-123
     SERVER_PORT=8080
     ```
7. **Deploy** - Railway will auto-deploy
8. **Get your URL** from the "Settings" → "Domains" section

### Option 3: Docker Image Deploy

1. **Go to Railway Dashboard**
2. **Click "New" → "Empty Service"**
3. **Click "Source" → "Docker Image"**
4. **Enter**: `atendai/evolution-api:latest`
5. **Add Environment Variables**:
   ```
   AUTHENTICATION_API_KEY=your-secret-key-123
   SERVER_PORT=8080
   ```
6. **Deploy**

## After Deployment

### 1. Get Your URL

Railway will give you a URL like:
```
https://evolution-api-production-xxxx.up.railway.app
```

### 2. Test the API

```bash
# Health check
curl https://your-url.railway.app/

# Should return Evolution API info
```

### 3. Create WhatsApp Instance

```bash
curl -X POST https://your-url.railway.app/instance/create \
  -H "apikey: your-secret-key-123" \
  -H "Content-Type: application/json" \
  -d '{
    "instanceName": "my-whatsapp",
    "qrcode": true
  }'
```

### 4. Get QR Code

```bash
curl https://your-url.railway.app/instance/qrcode/my-whatsapp \
  -H "apikey: your-secret-key-123"
```

## Update Your Backend

Once Evolution API is deployed, update your backend:

### File: `backend/app/services/whatsapp_baileys.py`

Find the gateway URL and update it:

```python
# Change this:
GATEWAY_URL = os.getenv("WHATSAPP_GATEWAY_URL", "http://whatsapp-gateway:8080")

# To this:
GATEWAY_URL = os.getenv("WHATSAPP_GATEWAY_URL", "https://your-evolution-api.railway.app")
```

### Environment Variable

Or set in Railway:
```
WHATSAPP_GATEWAY_URL=https://your-evolution-api.railway.app
```

## API Endpoints Reference

| Action | Endpoint | Method |
|--------|----------|--------|
| Create instance | `/instance/create` | POST |
| Get QR code | `/instance/qrcode/{name}` | GET |
| Send message | `/message/sendText/{name}` | POST |
| Get status | `/instance/connectionState/{name}` | GET |
| Delete instance | `/instance/delete/{name}` | DELETE |

## Troubleshooting

### Can't access the API
- Check Railway logs
- Ensure `SERVER_PORT=8080` is set
- Verify your domain is generated

### QR code not working
- Make sure instance is created first
- Check `AUTHENTICATION_API_KEY` matches
- View Railway logs for errors

### Need help?
- Evolution API Docs: https://doc.evolution-api.com/
- GitHub Issues: https://github.com/EvolutionAPI/evolution-api/issues

## Next Steps

1. ✅ Deploy Evolution API to Railway (use Option 1, 2, or 3 above)
2. ✅ Test the health endpoint
3. ✅ Create a WhatsApp instance
4. ✅ Get QR code and scan with WhatsApp
5. ✅ Update your backend gateway URL
6. ✅ Test sending messages
7. ✅ Remove old whatsapp-gateway services

---

**Note**: Evolution API is maintained by a professional team with 143 contributors. It's production-ready and actively updated. This is much better than maintaining our own gateway!
