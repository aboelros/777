# WA-Gateway Session Disconnecting - Advanced Troubleshooting

## Current Situation

✅ `WEBHOOK_BASE_URL` is configured correctly
❌ Session connects then immediately disconnects
❌ Session ID being reused: `gg`

## Root Cause Analysis

The session is disconnecting because:

1. **Session ID Reuse**: Using the same session ID `gg` multiple times causes conflicts
2. **No Persistent Storage**: WA-Gateway needs to persist session data between restarts
3. **Missing Volume Mount**: Session credentials aren't being saved

## Solution 1: Use Unique Session IDs

### Problem
Every time you create an integration, you're using `gg` as the session ID. WA-Gateway gets confused when you try to start the same session multiple times.

### Fix
Use a **unique session ID** for each integration:

**Good examples:**
- `shop-whatsapp-001`
- `customer-service-main`
- `sales-team-2024`
- `my-business-wa`

**Bad examples:**
- `gg` (too short, gets reused)
- `test` (generic, gets reused)
- `session` (generic, gets reused)

### How to Test
1. Delete the old integration with session ID `gg`
2. Create a new integration with session ID: `my-shop-wa-2024`
3. Scan the QR code
4. Session should stay connected

---

## Solution 2: Configure Persistent Storage

### Problem
WA-Gateway stores session credentials in `/app/wa_credentials` directory. If this isn't persisted, sessions are lost on restart.

### Fix for Railway

Railway doesn't support persistent volumes by default, but WA-Gateway should still work if:

1. **Don't restart WA-Gateway** while a session is active
2. **Use unique session IDs** for each integration
3. **Keep WA-Gateway running** continuously

### Alternative: Use Railway Volumes (if available)

If Railway supports volumes for your plan:

```yaml
# In WA-Gateway deployment
volumes:
  - /app/wa_credentials
  - /app/media
```

---

## Solution 3: Check WA-Gateway Logs for Specific Errors

### What to Look For

Check your WA-Gateway Railway logs for:

```
✅ Good signs:
- "session: 'xxx' connecting"
- "session: 'xxx' connected"
- "QR code generated"

❌ Bad signs:
- "session: 'xxx' disconnected" (immediately after connecting)
- "Error: ..."
- "Failed to ..."
- "Connection closed"
```

### Common Error Messages

1. **"Session already exists"**
   - **Cause**: Trying to start a session that's already running
   - **Fix**: Use a different session ID or logout the old session first

2. **"Connection lost"**
   - **Cause**: WhatsApp mobile app disconnected
   - **Fix**: Rescan QR code

3. **"Auth failure"**
   - **Cause**: Session credentials corrupted
   - **Fix**: Delete session and create new one

---

## Solution 4: Proper Session Lifecycle

### Correct Flow

```
1. Create Integration (session_id: "my-shop-001")
   ↓
2. Start Session (GET /session/start?session=my-shop-001)
   ↓
3. QR Code Appears
   ↓
4. User Scans QR Code
   ↓
5. WA-Gateway Sends Webhook: {"session": "my-shop-001", "status": "connected"}
   ↓
6. Backend Updates Integration Status to "connected"
   ↓
7. Session Stays Active (credentials saved in /app/wa_credentials)
   ↓
8. Messages Flow Both Ways
```

### What's Happening Now

```
1. Create Integration (session_id: "gg")
   ↓
2. Start Session (GET /session/start?session=gg)
   ↓
3. Session Connects
   ↓
4. Session Immediately Disconnects ❌
   ↓
5. No webhook sent or webhook fails
```

---

## Solution 5: Test Session Manually

### Step 1: Test Session Creation Directly

Visit this URL in your browser:
```
https://wa-gateway-production-1a18.up.railway.app/session/start?session=test-manual-123
```

**Expected:**
- QR code appears
- You can scan it
- Session stays connected

**If this works:** The issue is in how your backend is creating sessions

**If this fails:** The issue is with WA-Gateway configuration

### Step 2: Check Session Status

After scanning, check session status:
```
GET https://wa-gateway-production-1a18.up.railway.app/session/status?session=test-manual-123
```

**Expected response:**
```json
{
  "session": "test-manual-123",
  "status": "connected",
  "qr": null
}
```

### Step 3: Send Test Message

```bash
curl -X POST "https://wa-gateway-production-1a18.up.railway.app/message/send-text" \
  -H "Content-Type: application/json" \
  -d '{
    "session": "test-manual-123",
    "to": "1234567890",
    "text": "Test message"
  }'
```

---

## Solution 6: Check Backend Webhook Handling

### Verify Webhook Endpoint

Test if your backend webhook is working:

```bash
curl -X POST "https://ai-sales-bot-api-production-a5d1.up.railway.app/api/v1/webhooks/wa-gateway/session" \
  -H "Content-Type: application/json" \
  -d '{
    "session": "test",
    "status": "connected"
  }'
```

**Expected:** HTTP 200 OK

**Check backend logs** for:
```
WA-Gateway session webhook received
session_id=test
status=connected
```

---

## Immediate Action Plan

### Step 1: Delete Old Integration
1. Go to Integrations page
2. Delete the integration with session ID `gg`

### Step 2: Create New Integration with Unique ID
1. Click "Connect" on WhatsApp
2. Select "WA-Gateway"
3. **Session ID:** `my-shop-wa-dec2024` (unique!)
4. Click "Connect"

### Step 3: Monitor Logs

**WA-Gateway logs should show:**
```
session: 'my-shop-wa-dec2024' connecting
session: 'my-shop-wa-dec2024' connected  ✅ Should stay here
```

**Backend logs should show:**
```
WA-Gateway session webhook received
session_id=my-shop-wa-dec2024
status=connected
```

### Step 4: Verify Integration Status

1. Refresh integrations page
2. Integration status should be "connected"
3. Try sending a test message

---

## Why Session ID Matters

WA-Gateway uses the session ID to:
1. **Store credentials** in `/app/wa_credentials/{session_id}/`
2. **Track active connections**
3. **Route messages** to the correct WhatsApp account

Using the same session ID multiple times causes:
- ❌ Credential conflicts
- ❌ Connection confusion
- ❌ Immediate disconnections

---

## Summary

**Most Likely Issue:** Session ID `gg` is being reused

**Quick Fix:**
1. Use a unique session ID (e.g., `my-business-whatsapp-2024`)
2. Delete old integrations with `gg`
3. Create fresh integration
4. Scan QR code
5. Session should stay connected

**If Still Fails:**
1. Check WA-Gateway logs for specific error
2. Test session creation manually in browser
3. Verify webhook endpoint is receiving events
4. Check if WA-Gateway has persistent storage configured
