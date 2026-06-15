# Fix WhatsApp Session Encryption Errors

## Problem 🔴
Your WhatsApp bot shows as "offline" and has session encryption errors:
- Bad MAC errors
- Key used already or never filled
- Over 2000 messages into the future
- Failed to decrypt messages

## Solution ✅

### Option 1: Reset Session via API (Recommended)

1. **Delete the corrupted session:**
   ```bash
   # Get your session_id from the integration (usually 'fff' based on your logs)
   curl -X DELETE https://your-wa-gateway-url/session/fff
   ```

2. **In your application, disconnect the integration:**
   - Go to your frontend
   - Navigate to Integrations → WhatsApp
   - Click "Disconnect" or "Delete Integration"

3. **Reconnect WhatsApp:**
   - Click "Connect WhatsApp"
   - Scan the new QR code with your phone
   - Wait for "Connected" status

### Option 2: Reset via Database (If API doesn't work)

1. **Find your integration in the database:**
   ```sql
   SELECT id, status, extra_data->>'session_id' as session_id 
   FROM integrations 
   WHERE provider = 'whatsapp';
   ```

2. **Update the integration status to force reconnection:**
   ```sql
   UPDATE integrations 
   SET status = 'pending', 
       extra_data = jsonb_set(extra_data, '{needs_reset}', 'true')
   WHERE provider = 'whatsapp';
   ```

3. **Delete the session from WA-Gateway:**
   ```bash
   curl -X DELETE https://your-wa-gateway-url/session/fff
   ```

4. **Reconnect from the frontend**

### Option 3: Complete Clean Reset

If the above doesn't work, do a complete reset:

1. **Stop your backend server**

2. **Delete the integration from database:**
   ```sql
   DELETE FROM integrations WHERE provider = 'whatsapp';
   ```

3. **Delete all session data from WA-Gateway:**
   ```bash
   # Delete the session
   curl -X DELETE https://your-wa-gateway-url/session/fff
   
   # Or delete all sessions
   curl -X DELETE https://your-wa-gateway-url/session/all
   ```

4. **Restart your backend**

5. **Create a new WhatsApp integration from scratch**

## Prevention 🛡️

To prevent this from happening again:

### 1. **Never use the same WhatsApp number on multiple instances**
   - Only connect to ONE WA-Gateway instance
   - Don't scan the QR code multiple times

### 2. **Don't clear browser data while connected**
   - This can corrupt the session

### 3. **Monitor session health**
   Add this endpoint to check session status:
   ```python
   @router.get("/integrations/whatsapp/health")
   async def check_whatsapp_health(
       project_id: UUID,
       db: AsyncSession = Depends(get_db)
   ):
       # Get integration
       result = await db.execute(
           select(Integration)
           .where(Integration.project_id == project_id)
           .where(Integration.provider == "whatsapp")
       )
       integration = result.scalar_one_or_none()
       
       if not integration:
           return {"status": "not_configured"}
       
       # Check WA-Gateway session
       from app.services.integrations.whatsapp_gateway_service import WhatsAppGatewayService
       from app.core.config import settings
       
       gateway = WhatsAppGatewayService(
           base_url=settings.WA_GATEWAY_BASE_URL,
           api_key=settings.WA_GATEWAY_API_KEY
       )
       
       session_id = integration.extra_data.get("session_id")
       status = await gateway.get_session_status(session_id)
       
       return {
           "integration_status": integration.status,
           "session_status": status.get("status"),
           "session_id": session_id,
           "healthy": status.get("status") == "connected"
       }
   ```

### 4. **Auto-recovery mechanism**
   Add automatic session recovery when encryption errors are detected:
   ```python
   # In webhooks.py, add error detection
   if "Bad MAC" in str(error) or "Failed to decrypt" in str(error):
       logger.error("Session encryption error detected - marking for reset")
       integration.status = IntegrationStatus.ERROR
       integration.extra_data["error_type"] = "encryption_error"
       integration.extra_data["needs_reset"] = True
       await db.commit()
       
       # Optionally send notification to admin
       # await notify_admin("WhatsApp session needs reset")
   ```

## Quick Fix Command 🚀

Run this to quickly reset your WhatsApp session:

```bash
# 1. Get your WA-Gateway URL and API key
WA_GATEWAY_URL="your-wa-gateway-url"
WA_API_KEY="your-api-key"
SESSION_ID="fff"

# 2. Delete the corrupted session
curl -X DELETE "$WA_GATEWAY_URL/session/$SESSION_ID" \
  -H "X-Api-Key: $WA_API_KEY"

# 3. Create a new session
curl -X POST "$WA_GATEWAY_URL/session/start" \
  -H "X-Api-Key: $WA_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"session\": \"$SESSION_ID\"}"

# 4. Get QR code
curl "$WA_GATEWAY_URL/session/qr/$SESSION_ID" \
  -H "X-Api-Key: $WA_API_KEY"
```

Then scan the QR code with your phone.

## Verification ✅

After resetting, verify the session is working:

1. **Check session status:**
   ```bash
   curl "$WA_GATEWAY_URL/session/status/$SESSION_ID" \
     -H "X-Api-Key: $WA_API_KEY"
   ```
   
   Should return: `{"status": "connected"}`

2. **Send a test message:**
   ```bash
   curl -X POST "$WA_GATEWAY_URL/message/send-text" \
     -H "X-Api-Key: $WA_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "session": "fff",
       "to": "your-phone-number@s.whatsapp.net",
       "text": "Test message"
     }'
   ```

3. **Check for errors in logs:**
   - No "Bad MAC" errors
   - No "Failed to decrypt" errors
   - Messages should be sent successfully

## Common Issues ❓

### "Session not found"
- The session was deleted. Create a new one.

### "QR code expired"
- Generate a new QR code and scan immediately.

### "Already connected on another device"
- Logout from WhatsApp Web on all devices
- Wait 5 minutes
- Try again

### "Phone not responding"
- Make sure your phone has internet connection
- WhatsApp app is updated to latest version
- Phone is not in battery saver mode

## Need Help? 🆘

If the issue persists:

1. **Check WA-Gateway logs:**
   ```bash
   docker logs wa-gateway-container
   ```

2. **Check if WA-Gateway is running:**
   ```bash
   curl $WA_GATEWAY_URL/health
   ```

3. **Restart WA-Gateway:**
   ```bash
   docker restart wa-gateway-container
   ```

4. **Check your backend logs for webhook errors**

5. **Verify your phone number is not banned by WhatsApp**
   - Try sending a message manually from WhatsApp
   - If you can't send messages, your number might be restricted
