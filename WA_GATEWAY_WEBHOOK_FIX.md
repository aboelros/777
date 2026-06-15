# WA-Gateway Session Disconnecting - Fix

## Problem

The WA-Gateway session connects but immediately disconnects:
```
session: 'gg' connecting
session: 'gg' disconnected
```

## Root Cause

**WA-Gateway requires the `WEBHOOK_BASE_URL` environment variable** to know where to send session and message events. Without this, the session disconnects immediately after connecting.

## Solution

### Step 1: Configure WA-Gateway Webhook URL

In your **WA-Gateway Railway service**, add this environment variable:

```bash
WEBHOOK_BASE_URL=https://ai-sales-bot-api-production-412b.up.railway.app/api/v1/webhooks/wa-gateway
```

**Important:** 
- Use your **backend** Railway URL (not the WA-Gateway URL)
- Do NOT include trailing slash
- Do NOT include `/session` or `/message` - WA-Gateway adds these automatically

### Step 2: How WA-Gateway Uses Webhooks

When you set `WEBHOOK_BASE_URL`, WA-Gateway will send webhooks to:

1. **Session Events:**
   ```
   POST https://your-backend.railway.app/api/v1/webhooks/wa-gateway/session
   ```
   Payload:
   ```json
   {
       "session": "gg",
       "status": "connected"  // or "disconnected", "connecting"
   }
   ```

2. **Message Events:**
   ```
   POST https://your-backend.railway.app/api/v1/webhooks/wa-gateway/message
   ```
   Payload:
   ```json
   {
       "session": "gg",
       "from": "1234567890@s.whatsapp.net",
       "text": "Hello",
       "message": { ... }
   }
   ```

### Step 3: Verify Backend Webhook Endpoints

Your backend already has these endpoints (✅ already implemented):

**File:** `backend/app/api/v1/webhooks.py`

```python
# Session webhook - receives connection status updates
@router.post("/wa-gateway/session")
async def wa_gateway_session_webhook(...)

# Message webhook - receives incoming messages
@router.post("/wa-gateway/message")
async def wa_gateway_message_webhook(...)
```

### Step 4: Complete WA-Gateway Environment Variables

Your WA-Gateway service should have:

```bash
# Required: Where to send webhooks
WEBHOOK_BASE_URL=https://ai-sales-bot-api-production-412b.up.railway.app/api/v1/webhooks/wa-gateway

# Optional: API key for security
KEY=your-secret-key-here

# Optional: Port (Railway auto-configures this)
PORT=5001
```

### Step 5: Redeploy WA-Gateway

After adding the environment variable:
1. Go to WA-Gateway service in Railway
2. Click "Variables" tab
3. Add `WEBHOOK_BASE_URL`
4. Click "Deploy" or it will auto-redeploy

### Step 6: Test the Connection

1. **Create a new integration** with a new session ID (e.g., `test-session-001`)
2. **Modal will appear** with iframe showing QR code
3. **Scan the QR code** with WhatsApp mobile app
4. **Watch the logs:**
   - WA-Gateway logs should show: `session: 'test-session-001' connected`
   - Backend logs should show: `WA-Gateway session webhook received`
5. **Integration status** should update to "connected"

## Why This Happens

WA-Gateway is designed as a **webhook-based system**:

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   WhatsApp  │ ◄─────► │ WA-Gateway   │ ◄─────► │   Backend   │
│   Mobile    │         │  (Railway)   │         │  (Railway)  │
└─────────────┘         └──────────────┘         └─────────────┘
                              │
                              │ Sends webhooks to:
                              │ WEBHOOK_BASE_URL
                              ▼
                        Backend receives:
                        - Session status
                        - Messages
```

Without `WEBHOOK_BASE_URL`:
- ❌ WA-Gateway doesn't know where to send events
- ❌ Session connects but can't communicate
- ❌ Immediately disconnects

With `WEBHOOK_BASE_URL`:
- ✅ WA-Gateway sends session status to backend
- ✅ Backend updates integration status
- ✅ Session stays connected
- ✅ Messages flow both ways

## Troubleshooting

### Issue: Session still disconnects after adding WEBHOOK_BASE_URL

**Check:**
1. WA-Gateway can reach your backend:
   ```bash
   # From WA-Gateway container, test:
   curl https://ai-sales-bot-api-production-412b.up.railway.app/health
   ```

2. Backend webhook endpoint is accessible:
   ```bash
   curl -X POST https://ai-sales-bot-api-production-412b.up.railway.app/api/v1/webhooks/wa-gateway/session \
     -H "Content-Type: application/json" \
     -d '{"session":"test","status":"connected"}'
   ```

3. Check WA-Gateway logs for webhook errors

### Issue: Backend not receiving webhooks

**Solution:**
1. Verify `WEBHOOK_BASE_URL` is exactly:
   ```
   https://ai-sales-bot-api-production-412b.up.railway.app/api/v1/webhooks/wa-gateway
   ```
2. No trailing slash
3. Uses `https://` not `http://`
4. Backend service is running and healthy

### Issue: QR code doesn't appear in iframe

**Possible causes:**
1. **CORS restrictions** - WA-Gateway might block iframe embedding
2. **X-Frame-Options header** - WA-Gateway might prevent framing

**Solution:**
- Use the "Open in New Tab" button in the modal
- Or configure WA-Gateway to allow iframe embedding

## Expected Flow

### Correct Session Flow:

1. **User creates integration** → Backend creates integration record
2. **User clicks "Connect"** → Backend generates session URL
3. **Modal appears** → Shows WA-Gateway page in iframe
4. **User scans QR code** → WhatsApp connects to WA-Gateway
5. **WA-Gateway sends webhook** → `POST /webhooks/wa-gateway/session {"status": "connected"}`
6. **Backend updates status** → Integration status = "connected"
7. **User sends message** → WA-Gateway sends webhook → `POST /webhooks/wa-gateway/message`
8. **Backend processes** → AI responds → Backend sends via WA-Gateway API

## Quick Fix Checklist

- [ ] Add `WEBHOOK_BASE_URL` to WA-Gateway environment variables
- [ ] Use your backend URL: `https://your-backend.railway.app/api/v1/webhooks/wa-gateway`
- [ ] Redeploy WA-Gateway service
- [ ] Create new integration with new session ID
- [ ] Scan QR code
- [ ] Verify session stays connected
- [ ] Send test message to verify end-to-end flow

## Summary

The session disconnects because **WA-Gateway doesn't know where to send webhooks**. Add the `WEBHOOK_BASE_URL` environment variable to your WA-Gateway service pointing to your backend's webhook endpoint, and the session will stay connected.
