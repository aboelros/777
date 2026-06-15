# WA-Gateway Integration Setup Guide

## What is WA-Gateway?

WA-Gateway is a self-hosted WhatsApp gateway that allows you to connect WhatsApp to your application using QR code authentication (similar to WhatsApp Web).

## Prerequisites

1. **WA-Gateway Instance**: You need a running WA-Gateway instance
   - GitHub: https://github.com/mimamch/wa-gateway
   - Can be deployed on Railway, Render, or any Node.js hosting
   - Example URL: `https://your-wa-gateway.railway.app`

## How to Create WA-Gateway Integration

### Step 1: Create Integration via API

When creating a WhatsApp integration with WA-Gateway, you need to provide:

```json
{
  "provider": "whatsapp",
  "config": {
    "whatsapp_provider": "wa_gateway",
    "session_id": "your-unique-session-id",
    "base_url": "https://your-wa-gateway.railway.app",
    "api_key": "optional-api-key-if-configured"
  }
}
```

**Important Fields:**
- `whatsapp_provider`: Must be `"wa_gateway"` (not `"business_api"`)
- `session_id`: A unique identifier for this WhatsApp session (e.g., `"my-shop-whatsapp"`)
- `base_url`: The URL of your WA-Gateway instance (e.g., `"https://wa-gateway.railway.app"`)
- `api_key`: Optional API key if your WA-Gateway requires authentication

### Step 2: Start Session and Get QR Code

After creating the integration, call the start session endpoint:

```
POST /api/v1/integrations/{project_id}/whatsapp/{integration_id}/wa-gateway/start-session
```

This will:
1. Connect to your WA-Gateway instance
2. Generate a QR code
3. Return the QR code URL for scanning

### Step 3: Scan QR Code

1. Open WhatsApp on your phone
2. Go to **Settings → Linked Devices → Link a Device**
3. Scan the QR code returned from the API
4. Wait for the connection to establish

### Step 4: Webhook Configuration

Configure your WA-Gateway to send webhooks to:

**Message Webhook:**
```
POST https://your-backend.railway.app/api/v1/webhooks/wa-gateway/message
```

**Session Webhook:**
```
POST https://your-backend.railway.app/api/v1/webhooks/wa-gateway/session
```

## Frontend Integration Creation

When creating the integration from the frontend, ensure the form includes:

```javascript
const integrationData = {
  provider: "whatsapp",
  config: {
    whatsapp_provider: "wa_gateway",
    session_id: sessionId,  // User input
    base_url: baseUrl,      // User input (e.g., "https://wa-gateway.railway.app")
    api_key: apiKey         // Optional user input
  }
};
```

## Troubleshooting

### Error: "WA-Gateway base URL not found in integration config"

**Solution:** Make sure you're providing the `base_url` field when creating the integration:

```json
{
  "config": {
    "base_url": "https://your-wa-gateway.railway.app"
  }
}
```

### Error: "Failed to start session: ConnectError"

**Solution:** Check that:
1. Your WA-Gateway instance is running and accessible
2. The `base_url` is correct (include `https://` or `http://`)
3. Your backend can reach the WA-Gateway URL (no firewall blocking)

### Error: "Session ID is required"

**Solution:** Provide a `session_id` in the config:

```json
{
  "config": {
    "session_id": "my-whatsapp-session"
  }
}
```

## Example: Complete Integration Creation

```bash
curl -X POST "https://your-backend.railway.app/api/v1/integrations/{project_id}/connect" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "whatsapp",
    "config": {
      "whatsapp_provider": "wa_gateway",
      "session_id": "shop-whatsapp-001",
      "base_url": "https://wa-gateway.railway.app"
    }
  }'
```

Then start the session:

```bash
curl -X POST "https://your-backend.railway.app/api/v1/integrations/{project_id}/whatsapp/{integration_id}/wa-gateway/start-session" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Response:
```json
{
  "status": "success",
  "session_id": "shop-whatsapp-001",
  "qr_url": "data:image/png;base64,iVBORw0KGgoAAAANS...",
  "message": "Scan QR code with WhatsApp mobile app"
}
```

## Notes

- Each integration can have its own WA-Gateway instance
- Multiple integrations can share the same WA-Gateway instance (using different session IDs)
- The `base_url` is stored per-integration, so you don't need a global environment variable
