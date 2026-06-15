# Quick Setup Guide - WA-Gateway Integration

## Your Current Setup

You already have:
- ✅ WA-Gateway deployed on Railway
- ✅ Environment variable configured: `WA_GATEWAY_BASE_URL=https://wa-gateway-production-1a18.up.railway.app/`

## What is the Base URL?

The **base URL** is the web address where your WA-Gateway instance is running. In your case:
```
https://wa-gateway-production-1a18.up.railway.app/
```

This is the URL that the backend uses to communicate with your WA-Gateway to:
- Start WhatsApp sessions
- Generate QR codes
- Send messages
- Download media files

## How to Create Integration (Simple Way)

Since you already have `WA_GATEWAY_BASE_URL` configured in Railway, you can create integrations **without** entering the base URL:

### Step 1: Create Integration
1. Go to **Integrations** page
2. Click **Connect** on WhatsApp card
3. Select **WA-Gateway (Self-Hosted)**
4. **Leave "Base URL" field empty** (it will use your environment variable)
5. Enter a **Session ID** (e.g., `my-shop-session`)
6. Click **Connect**

### Step 2: Scan QR Code
1. A QR code will appear
2. Open WhatsApp on your phone
3. Go to **Settings → Linked Devices → Link a Device**
4. Scan the QR code
5. Wait for connection

## How It Works

```
Frontend Form (Session ID only)
    ↓
Backend receives request
    ↓
Checks integration config for base_url
    ↓
If not found, uses WA_GATEWAY_BASE_URL from environment
    ↓
Connects to: https://wa-gateway-production-1a18.up.railway.app/
    ↓
Generates QR code
    ↓
Returns to frontend
```

## When to Use Custom Base URL

You only need to enter a custom base URL if:
- You have **multiple WA-Gateway instances** for different projects
- You want to **override** the default environment variable
- You're **testing** with a different gateway

## Example Configurations

### Option 1: Use Environment Variable (Recommended for you)
```json
{
  "provider": "whatsapp",
  "config": {
    "whatsapp_provider": "wa_gateway",
    "session_id": "shop-session-001"
    // base_url is omitted - will use WA_GATEWAY_BASE_URL
  }
}
```

### Option 2: Custom Base URL (For multi-tenant setups)
```json
{
  "provider": "whatsapp",
  "config": {
    "whatsapp_provider": "wa_gateway",
    "session_id": "shop-session-001",
    "base_url": "https://custom-gateway.railway.app"
  }
}
```

## Troubleshooting

### Error: "WA-Gateway base URL not configured"
**Solution:** Make sure `WA_GATEWAY_BASE_URL` is set in Railway environment variables:
1. Go to Railway dashboard
2. Select your backend service
3. Go to **Variables** tab
4. Verify `WA_GATEWAY_BASE_URL` exists and is correct
5. Redeploy if you just added it

### Error: "Failed to start session: ConnectError"
**Solution:** Check that your WA-Gateway is running:
1. Visit: https://wa-gateway-production-1a18.up.railway.app/
2. You should see the WA-Gateway interface
3. If not, check WA-Gateway deployment logs

### QR Code Not Appearing
**Solution:** 
1. Check browser console for errors
2. Verify the session was created successfully
3. Try the "Verify" button on the integration card

## Your Environment Variables

Make sure these are set in Railway:

```bash
# Required for WA-Gateway
WA_GATEWAY_BASE_URL=https://wa-gateway-production-1a18.up.railway.app/

# Optional (if your gateway requires authentication)
WA_GATEWAY_API_KEY=your-api-key-here
```

## Next Steps

1. ✅ Deploy the updated backend code to Railway
2. ✅ Deploy the updated frontend code to Vercel
3. ✅ Try creating a WA-Gateway integration (leave base URL empty)
4. ✅ Scan the QR code
5. ✅ Test sending/receiving messages

## Summary

**TL;DR:** You don't need to enter the base URL in the form. Just enter the **Session ID** and the system will automatically use your configured gateway at `https://wa-gateway-production-1a18.up.railway.app/`.
