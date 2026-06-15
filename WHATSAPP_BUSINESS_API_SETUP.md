# WhatsApp Business API Setup Guide

## ✅ Implementation Complete!

I've implemented the official WhatsApp Business Cloud API integration. Here's what was added:

### Files Created:
1. **`backend/app/services/whatsapp_business_api.py`** - WhatsApp Business API client
2. **`backend/app/services/integrations/whatsapp_business.py`** - Integration service
3. Updated **`backend/app/core/config.py`** - Added new environment variables
4. Updated **`backend/app/api/v1/webhooks.py`** - Added webhook endpoints

## 🚀 Next Steps: Get Your Meta Credentials

### Step 1: Create Meta Business Account

1. Go to: https://business.facebook.com/
2. Click "Create Account"
3. Follow the setup wizard

### Step 2: Create Meta App

1. Go to: https://developers.facebook.com/apps
2. Click "Create App"
3. Select "Business" as app type
4. Give it a name (e.g., "My Business WhatsApp")
5. Click "Create App"

### Step 3: Add WhatsApp Product

1. In your app dashboard, find "WhatsApp" in the products list
2. Click "Set up"
3. Select your Business Account
4. Click "Continue"

### Step 4: Get Test Phone Number

Meta provides a test number for free:
1. Go to "WhatsApp" → "API Setup"
2. You'll see a test phone number provided by Meta
3. Copy the **Phone Number ID** (looks like: `123456789012345`)

### Step 5: Get Access Token

1. In "WhatsApp" → "API Setup"
2. Find "Temporary access token"
3. Copy the token (starts with `EAA...`)
4. **Note**: This is temporary (24 hours). For production, you'll need a permanent token.

### Step 6: Get Business Account ID

1. Go to "WhatsApp" → "API Setup"
2. Find "WhatsApp Business Account ID"
3. Copy the ID

### Step 7: Create Verify Token

Create your own random string for webhook verification:
```
whatsapp_verify_secret_12345
```

## 📝 Configure Railway Environment Variables

Add these to your **backend** service in Railway:

```env
# WhatsApp Business API
WHATSAPP_PHONE_NUMBER_ID=123456789012345
WHATSAPP_BUSINESS_ACCOUNT_ID=987654321098765
WHATSAPP_ACCESS_TOKEN=EAAxxxxxxxxxxxxxxxxxxxxxxxxx
WHATSAPP_VERIFY_TOKEN=whatsapp_verify_secret_12345
```

## 🔗 Configure Webhooks in Meta Dashboard

1. Go to "WhatsApp" → "Configuration"
2. Click "Edit" next to "Webhook"
3. Set **Callback URL**: `https://your-backend.railway.app/webhooks/whatsapp`
4. Set **Verify Token**: `whatsapp_verify_secret_12345` (same as above)
5. Click "Verify and Save"
6. Subscribe to these webhook fields:
   - ✅ `messages`
   - ✅ `message_status`

## 🧪 Test Your Integration

### Test 1: Send a Message via API

```bash
curl -X POST "https://graph.facebook.com/v18.0/YOUR_PHONE_NUMBER_ID/messages" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "messaging_product": "whatsapp",
    "to": "1234567890",
    "type": "text",
    "text": {"body": "Hello from WhatsApp Business API!"}
  }'
```

### Test 2: Receive a Message

1. Send a WhatsApp message to your test number
2. Check your backend logs in Railway
3. You should see "WhatsApp Business API message received"

### Test 3: From Your Frontend

1. Update your frontend to use the new API
2. Send a test message
3. Verify it's delivered

## 🗑️ Remove Old Gateway Code (Optional)

Once WhatsApp Business API is working, you can remove:

1. **Evolution API service** from Railway
2. **whatsapp-gateway-go** directory
3. Old gateway client files:
   - `backend/app/services/whatsapp_gateway_client.py`
   - `backend/app/services/whatsapp_linked_device_service.py`
   - `backend/app/services/integrations/whatsapp_baileys.py`

## 💰 Pricing

- **Free Tier**: 1,000 conversations/month
- **Paid**: $0.005 - $0.09 per conversation (varies by country)
- A "conversation" = 24-hour window with a customer

## 📚 Resources

- **Getting Started**: https://developers.facebook.com/docs/whatsapp/cloud-api/get-started
- **API Reference**: https://developers.facebook.com/docs/whatsapp/cloud-api/reference
- **Webhooks**: https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks

## ✅ Summary

**What's Done:**
- ✅ WhatsApp Business API client created
- ✅ Integration service implemented
- ✅ Webhook endpoints added
- ✅ Configuration updated
- ✅ Code committed and pushed

**What You Need to Do:**
1. Create Meta Business Account
2. Create Meta App
3. Get credentials (Phone Number ID, Access Token, Business Account ID)
4. Add environment variables to Railway
5. Configure webhooks in Meta dashboard
6. Test!

**Questions?** Let me know if you need help with any step!
