# Integrations Guide

This document provides an exhaustive and comprehensive overview of all platform integrations supported by the system. It covers official cloud APIs, self-hosted gateways, eCommerce platforms, social media channels, centralized webhook architecture, and extensive troubleshooting and testing practices.

---

## 1. Introduction to System Integrations

Our system acts as a centralized omni-channel communication and commerce hub. By unifying multiple disparate APIs, we provide a single cohesive interface for customer interaction, order management, and support. 

### Core Tenets:
- **Resilience:** All integrations must gracefully handle rate limits and temporary outages.
- **Security:** Strict validation of webhooks via HMAC signatures and secure token management.
- **Normalization:** Every incoming event, regardless of source platform, is normalized into a standard system schema.

---

## 2. WhatsApp Business API (official Meta Cloud API)

The official WhatsApp Business API (Cloud API) is hosted by Meta. It provides a reliable, scalable way to send and receive WhatsApp messages without managing physical devices.

### 2.1 Prerequisites
- A verified Meta Developer Account.
- A registered Facebook Business app.
- A verified WhatsApp Business account.
- A phone number not currently registered on the standard WhatsApp mobile app.

### 2.2 Configuration Steps
1. **Create the App:**
   Navigate to the Meta App Dashboard and create a new app of type "Business".
2. **Add WhatsApp Product:**
   Select "WhatsApp" from the available products. Follow the onboarding flow to link your phone number.
3. **Generate Access Token:**
   Obtain a System User Access Token from the Business Manager settings. Temporary tokens expire in 24 hours; generate a permanent token for production.
4. **Register Phone Number:**
   Complete the OTP verification for the added phone number.

### 2.3 Credentials Needed
Store these in your `.env` file safely:
```env
# Official WhatsApp Cloud API Credentials
WHATSAPP_CLOUD_API_KEY="EAA..."
WHATSAPP_PHONE_NUMBER_ID="1023456789..."
WHATSAPP_BUSINESS_ACCOUNT_ID="1098765432..."
WHATSAPP_WEBHOOK_VERIFY_TOKEN="your_secure_verify_token_here_123"
```

### 2.4 Webhook Configuration
- **URL:** `https://api.your-domain.com/webhooks/whatsapp/cloud`
- **Verify Token:** Must perfectly match `WHATSAPP_WEBHOOK_VERIFY_TOKEN`.
- **Subscribed Fields:** Ensure you subscribe to `messages`, `message_deliveries`, and `message_reads`.

### 2.5 Sending a Message Example
```bash
curl -X POST 'https://graph.facebook.com/v17.0/1023456789/messages' \
  -H 'Authorization: Bearer EAA...' \
  -H 'Content-Type: application/json' \
  -d '{
    "messaging_product": "whatsapp",
    "to": "15551234567",
    "type": "template",
    "template": {
      "name": "hello_world",
      "language": { "code": "en_US" }
    }
  }'
```

---

## 3. WA-Gateway (self-hosted Baileys gateway)

For scenarios requiring multi-device support or using existing standard WhatsApp numbers (unverified businesses), we deploy a self-hosted Baileys-based WA-Gateway.

### 3.1 Installation
Clone the WA-Gateway repository or pull the provided Docker container.

```bash
git clone https://github.com/your-repo/wa-gateway.git
cd wa-gateway
npm install
cp .env.example .env
```

### 3.2 Configuration
Modify the `.env` file to set up the gateway:
```env
PORT=3000
SESSION_DIR=./sessions
WEBHOOK_URL=https://api.your-domain.com/webhooks/wa-gateway
WEBHOOK_SECRET=wa_gateway_secret_123
MAX_RETRIES=5
```

### 3.3 Session Management and QR Scan
To initialize a session, start the gateway and request a QR code.
```bash
npm start
```
1. Send a request to the `/session/start?id=session_primary` endpoint.
2. The API will generate and return a Base64-encoded QR code.
3. Open WhatsApp on your mobile device, go to "Linked Devices", and scan the QR code.
4. Upon successful link, session data is stored in the `SESSION_DIR`. Do not delete these files unless you wish to log out.

### 3.4 Webhook Behavior
Incoming messages from the Baileys client are forwarded to the `WEBHOOK_URL` using a JSON payload:
```json
{
  "event": "message",
  "session": "session_primary",
  "data": {
    "remoteJid": "1234567890@s.whatsapp.net",
    "message": { "conversation": "Hello self-hosted bot!" },
    "timestamp": 1696152000
  }
}
```

---

## 4. Facebook Messenger

Integration with Facebook Messenger uses the standard Meta Graph API.

### 4.1 Meta App Setup
1. Go to the Meta Developer Dashboard.
2. Select your existing app or create a new one.
3. Add the "Messenger" product in the app dashboard.

### 4.2 Page Token Generation
1. Under Messenger Settings, link your Facebook Page.
2. Generate a Page Access Token. This token is required to send messages to users who interact with your page.

### 4.3 Credentials Needed
```env
MESSENGER_PAGE_ACCESS_TOKEN="EAA..."
MESSENGER_APP_SECRET="abc123def456..."
MESSENGER_VERIFY_TOKEN="messenger_secure_token"
```

### 4.4 Webhook Subscription
- **Callback URL:** `https://api.your-domain.com/webhooks/messenger`
- **Verify Token:** Must match `MESSENGER_VERIFY_TOKEN`.
- Subscriptions: `messages`, `messaging_postbacks`, `messaging_optins`.

---

## 5. Instagram DMs

Instagram integration is managed through the Meta Graph API but requires a professional Instagram account linked to a Facebook Page.

### 5.1 Prerequisites
- An Instagram Business or Creator account.
- The Instagram account must be linked to the Facebook Page managed by your Meta App.
- "Allow Access to Messages" must be toggled ON in the Instagram mobile app settings under Privacy > Messages.

### 5.2 Credentials Needed
Shares token infrastructure with Messenger:
```env
IG_PAGE_ACCESS_TOKEN="EAA..."
IG_APP_SECRET="abc123def..."
IG_VERIFY_TOKEN="instagram_secure_token"
```

### 5.3 Webhook Subscription
- **Callback URL:** `https://api.your-domain.com/webhooks/instagram`
- **Verify Token:** `instagram_secure_token`
- Subscriptions: `messages`, `messaging_postbacks`, `comments`, `story_mentions`.

---

## 6. Telegram Bot

Telegram bots are configured via BotFather and use webhooks for real-time interaction.

### 6.1 BotFather Setup
1. Open Telegram and search for `@BotFather`.
2. Send `/newbot` and follow prompts.
3. Save the HTTP API Token provided.

### 6.2 Command Registration
Configure commands by sending `/setcommands` to BotFather:
```text
start - Initialize the bot
help - Show help message
status - Check service status
settings - Configure user preferences
support - Connect to a human agent
```

### 6.3 Webhook Registration
Register your webhook using an HTTP GET request. The endpoint must use HTTPS.
```bash
curl -X GET "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://api.your-domain.com/webhooks/telegram"
```

### 6.4 Credentials Needed
```env
TELEGRAM_BOT_TOKEN="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
TELEGRAM_WEBHOOK_SECRET="telegram_secret_token"
```

---

## 7. Shopify

Shopify integration reacts to eCommerce events (orders, inventory) in real-time.

### 7.1 API Key Setup
1. Log in to Shopify Admin.
2. Navigate to Settings > Apps and sales channels > Develop apps.
3. Create a new custom app.
4. Assign Admin API scopes: `read_orders`, `write_orders`, `read_products`, `read_customers`.
5. Install the app to generate the Access Token.

### 7.2 Credentials Needed
```env
SHOPIFY_SHOP_NAME="your-store.myshopify.com"
SHOPIFY_ACCESS_TOKEN="shpat_..."
SHOPIFY_WEBHOOK_SECRET="whsec_..."
```

### 7.3 Webhook Events
Register webhooks in the admin panel or via API for:
- `orders/create`
- `orders/updated`
- `orders/paid`
- `customers/create`
- `products/update`

---

## 8. TikTok Business

TikTok integration handles commerce sync and lead generation.

### 8.1 Configuration
1. Register on the TikTok Developer Portal.
2. Create a Business app to obtain the App Key and Secret.
3. Request necessary permissions (TikTok Shop API or Lead Generation).

### 8.2 Credentials Needed
```env
TIKTOK_APP_KEY="tiktok_app_123"
TIKTOK_APP_SECRET="tiktok_secret_abc"
TIKTOK_SHOP_ID="shop_xyz"
```

### 8.3 Webhooks
- **URL:** `https://api.your-domain.com/webhooks/tiktok`
- Make sure to acknowledge receipt of TikTok webhooks within 2 seconds.

---

## 9. Discord

Discord integration enables automated community support.

### 9.1 App Setup
1. Go to the Discord Developer Portal.
2. Create a new Application.
3. Add a "Bot" to the application.
4. Copy the Bot Token.

### 9.2 Credentials Needed
```env
DISCORD_BOT_TOKEN="MTAx..."
DISCORD_PUBLIC_KEY="discord_public_key_abc"
DISCORD_GUILD_ID="123456789012345678"
```

### 9.3 Verification & Gateway
- Set the "Interactions Endpoint URL" to `https://api.your-domain.com/webhooks/discord`.
- Validate the `ed25519` signature for all incoming requests before processing.

---

## 10. Webhook Architecture

The system utilizes a unified, highly scalable webhook architecture to funnel events into a central processing engine.

### 10.1 The Pipeline Flow
1. **Ingress:** Webhooks arrive at `/webhooks/{platform}`.
2. **Security Gateway:** Verifies platform-specific HMAC signatures. Invalid requests are rejected with a 401 Unauthorized status.
3. **Normalization:** The raw payload is transformed into a `StandardEvent` object. This decouples the core logic from platform-specific payload structures.
4. **Queueing:** The `StandardEvent` is pushed to Redis/RabbitMQ. The webhook HTTP request is immediately closed with a 200 OK.
5. **Worker Processing:** Background workers pop events, trigger NLP/Bot logic, and dispatch replies via the platform API SDKs.

### 10.2 Normalized Payload Example
```json
{
  "event_id": "evt_987654321",
  "source_platform": "whatsapp_cloud",
  "timestamp": "2023-10-01T12:00:00Z",
  "user": {
    "platform_id": "1234567890",
    "display_name": "John Doe",
    "locale": "en_US"
  },
  "message": {
    "type": "text",
    "content": "I need help with my order.",
    "raw_payload": { ... }
  }
}
```

---

## 11. Troubleshooting

### 11.1 General Webhook Issues
- **Missed Events:** If a platform experiences repeated 500 errors or timeouts (>3 seconds), it may temporarily suspend webhooks. Ensure the queueing mechanism is fast.
- **Signature Validation Failing:** Ensure your middleware uses the raw request body buffer to compute HMACs. Parsing it to JSON first can alter whitespace and break the hash.

### 11.2 WhatsApp Cloud API
- **Error 131030 (Message Undeliverable):** The recipient is outside the 24-hour customer service window. You must use an approved template message.
- **Token Expiry:** You are likely using a temporary token instead of a permanent System User token.

### 11.3 WA-Gateway (Baileys)
- **Session Disconnects (Error 503):** WhatsApp forced a logout. Delete the specific session folder inside `SESSION_DIR` and re-scan the QR code.
- **Decryption Errors:** Happens when the session keys fall out of sync. Restart the gateway service.

### 11.4 Facebook Messenger / Instagram
- **Webhook Not Firing:** Verify the Page is correctly subscribed in the App settings.
- **Error 10 (No Permission):** Access token is missing `pages_messaging` or `instagram_manage_messages` scopes.
- **Instagram Inbox Not Showing Bot Replies:** Ensure "Allow Access to Messages" is enabled in the IG App.

### 11.5 Telegram
- **Webhook Registration Failure:** Telegram requires a valid SSL certificate. If using a self-signed cert, you must upload it during registration.
- **Bot Not Responding to Commands:** Privacy mode might be enabled, preventing the bot from seeing messages that don't start with a slash `/`.

### 11.6 Shopify
- **Missing HMAC Header:** Sometimes proxies strip headers. Ensure `x-shopify-hmac-sha256` is forwarded by your load balancer.

### 11.7 Token Errors
- **Rotation:** If a token is compromised, rotate it immediately in the developer portal and restart your application pods.
- **Environment Handling:** Never hardcode tokens in the repository.

---

## 12. Testing Integrations

### 12.1 Local Webhook Simulation
Use a secure tunnel (e.g., ngrok) to expose your local environment for testing.

```bash
# Start ngrok on port 3000
ngrok http 3000
```
Copy the ngrok HTTPS URL and update your webhook configurations in the respective developer portals.

### 12.2 cURL Payload Simulation
Simulate a Telegram webhook locally:

```bash
curl -X POST http://localhost:3000/webhooks/telegram \
  -H "Content-Type: application/json" \
  -d '{
        "update_id": 123456789,
        "message": {
          "message_id": 1,
          "from": { "id": 1111111, "is_bot": false, "first_name": "LocalTest" },
          "chat": { "id": 1111111, "type": "private" },
          "date": 1600000000,
          "text": "/start"
        }
      }'
```

### 12.3 Unit and Integration Testing
Write Jest tests to validate your HMAC validation middleware without needing external services.

```javascript
// Example Jest test for Shopify Webhook Validator
const crypto = require('crypto');
const secret = 'test_secret';
const payload = JSON.stringify({ test: "data" });
const hmac = crypto.createHmac('sha256', secret).update(payload).digest('base64');

test('validates valid shopify hmac', () => {
    const req = { headers: { 'x-shopify-hmac-sha256': hmac }, rawBody: payload };
    expect(validateShopifyWebhook(req, secret)).toBe(true);
});
```

### 12.4 Checking Logs and Observability
Detailed logging is crucial for monitoring integrations.

```bash
# Docker logs for WA-Gateway
docker logs -f wa-gateway --tail 100

# App server logs
tail -f /var/log/myapp/webhooks.log
```

Watch for `HTTP 200 OK` vs `HTTP 500` entries to quickly spot platform delivery failures.

---
*End of Guide.*
