# Fix for WA-Gateway Issues

## Problem 1: Groq Not Initializing

### Issue
The startup logs show no Groq initialization message, which means media processing (voice notes and images) won't work.

### Root Cause
`GROQ_API_KEY` environment variable is not set.

### Solution

#### Option 1: Get a Free Groq API Key (Recommended)

1. **Go to Groq Console**: https://console.groq.com/
2. **Sign up** for a free account
3. **Create an API Key**:
   - Go to "API Keys" section
   - Click "Create API Key"
   - Copy the key (starts with `gsk_...`)

4. **Add to Railway**:
   - Go to your Railway backend service
   - Click "Variables" tab
   - Add new variable:
     ```
     GROQ_API_KEY=gsk_your_key_here
     ```
   - Redeploy

5. **Verify**:
   - Check logs after deployment
   - You should see: `Groq client initialized successfully with key: gsk_...`

#### Option 2: Disable Groq (Not Recommended)

If you don't want to use Groq, the system will still work but:
- ❌ Voice notes won't be transcribed
- ❌ Images won't be analyzed
- ✅ Text messages will work fine

No action needed - it's already optional.

---

## Problem 2: ReadTimeout on Session Start

### Issue
```
Failed to generate QR code: Failed to start session: ReadTimeout
```

### Root Cause
The WA-Gateway takes longer than 5 seconds to generate the QR code, causing a timeout.

### Solution Applied
✅ Increased timeout from 5 seconds to 30 seconds in `whatsapp_gateway_service.py`

### Additional Debugging

The WA-Gateway logs show:
```
session: 'gg' connecting
session: 'gg' disconnected
```

This suggests the session is starting but disconnecting immediately. This could be due to:

1. **WA-Gateway Webhook Not Configured**
   - Your WA-Gateway needs to know where to send webhooks
   - Check WA-Gateway environment variables

2. **Network Issues**
   - WA-Gateway might not be able to reach your backend
   - Check if both services are on Railway and can communicate

### Fix WA-Gateway Webhook Configuration

#### Step 1: Update WA-Gateway Environment Variables

In your WA-Gateway Railway service, add/update:

```bash
# Your backend webhook URL
WEBHOOK_BASE_URL=https://ai-sales-bot-api-production-412b.up.railway.app/api/v1/webhooks/wa-gateway

# Optional: API key for webhook authentication
KEY=your-secret-key-here
```

#### Step 2: Verify WA-Gateway is Running

1. Visit: https://wa-gateway-production-1a18.up.railway.app/
2. You should see the WA-Gateway interface
3. If you see an error, check WA-Gateway deployment logs

#### Step 3: Test Session Creation Manually

Try creating a session directly via WA-Gateway:

```bash
curl "https://wa-gateway-production-1a18.up.railway.app/session/start?session=test123"
```

You should get an HTML page with a QR code.

---

## Complete Environment Variables Checklist

### Backend (AI Sales Commander)

```bash
# Required
DATABASE_URL=postgresql://...
GEMINI_API_KEY=AIza...

# WA-Gateway Integration
WA_GATEWAY_BASE_URL=https://wa-gateway-production-1a18.up.railway.app/
WA_GATEWAY_API_KEY=your-secret-key-here  # Optional, if WA-Gateway requires auth

# Media Processing (Recommended)
GROQ_API_KEY=gsk_your_groq_key_here

# Other integrations (optional)
WHATSAPP_PHONE_NUMBER_ID=...
WHATSAPP_ACCESS_TOKEN=...
```

### WA-Gateway Service

```bash
# Webhook configuration
WEBHOOK_BASE_URL=https://ai-sales-bot-api-production-412b.up.railway.app/api/v1/webhooks/wa-gateway

# Optional: API key for security
KEY=your-secret-key-here

# Port (usually auto-configured by Railway)
PORT=5001
```

---

## Testing Steps

### 1. Test Groq Initialization

After adding `GROQ_API_KEY`:

1. Redeploy backend
2. Check logs for: `Groq client initialized successfully`
3. If you see `No GROQ_API_KEY found`, the variable wasn't set correctly

### 2. Test WA-Gateway Connection

1. Create a new WhatsApp integration
2. Select "WA-Gateway (Self-Hosted)"
3. Enter Session ID: `test123`
4. Leave Base URL empty (uses environment variable)
5. Click "Connect"

**Expected Result:**
- QR code appears within 30 seconds
- No timeout error

**If Still Fails:**
- Check WA-Gateway logs in Railway
- Verify `WEBHOOK_BASE_URL` is set in WA-Gateway
- Ensure both services can communicate (same Railway project)

### 3. Test Media Processing

After Groq is configured:

1. Send a voice note to your WhatsApp bot
2. Check logs for: `Transcribing audio with Groq Whisper`
3. Bot should respond with transcribed text

---

## Quick Fix Summary

### Immediate Actions

1. ✅ **Add GROQ_API_KEY** to Railway backend variables
   ```
   GROQ_API_KEY=gsk_your_key_here
   ```

2. ✅ **Verify WA_GATEWAY_BASE_URL** is set
   ```
   WA_GATEWAY_BASE_URL=https://wa-gateway-production-1a18.up.railway.app/
   ```

3. ✅ **Configure WA-Gateway webhooks**
   ```
   WEBHOOK_BASE_URL=https://your-backend.railway.app/api/v1/webhooks/wa-gateway
   ```

4. ✅ **Deploy updated code** (timeout fix is already in the code)

### Verification

After deployment, check logs for:
- ✅ `Groq client initialized successfully`
- ✅ `WA-Gateway session started successfully`
- ✅ QR code generation completes without timeout

---

## Troubleshooting

### Error: "No GROQ_API_KEY found"
**Solution:** Add the key to Railway environment variables and redeploy

### Error: "ReadTimeout" persists
**Solution:** 
1. Check WA-Gateway is running: visit the URL directly
2. Verify WA-Gateway logs show session creation
3. Increase timeout further if needed (edit `whatsapp_gateway_service.py`)

### Error: "session disconnected immediately"
**Solution:**
1. Configure `WEBHOOK_BASE_URL` in WA-Gateway
2. Ensure both services are in the same Railway project
3. Check WA-Gateway can reach your backend

---

## Files Modified

1. ✅ `backend/app/services/integrations/whatsapp_gateway_service.py` - Increased timeout to 30s
2. 📝 This guide - Complete troubleshooting steps

## Next Steps

1. Add `GROQ_API_KEY` to Railway
2. Verify `WEBHOOK_BASE_URL` in WA-Gateway service
3. Redeploy both services
4. Test integration creation
5. Scan QR code and verify connection
