# 🔧 Configuration Guide - API Keys & Setup

## 📝 **What You Need to Provide:**

### **1. ✅ GEMINI API KEY (For AI Chat)**

**File:** `backend/.env`  
**Line 39:**
```env
GEMINI_API_KEY=YOUR_ACTUAL_GEMINI_KEY_HERE
```

**This Makes:**
- ✅ AI Assistant work
- ✅ AI-powered replies in chat
- ✅ Report generation
- ✅ Smart automation

---

### **2. 🔌 INTEGRATION API KEYS (For Platforms)**

These are **OPTIONAL** - only needed if you want to connect specific platforms:

#### **Shopify (E-commerce):**
```env
SHOPIFY_API_KEY=your-shopify-api-key
SHOPIFY_API_SECRET=your-shopify-api-secret
```

**How to Get:**
1. Go to Shopify Admin → Apps
2. Click "Develop apps"
3. Create new app
4. Get API credentials

---

#### **WhatsApp Business:**
```env
WHATSAPP_BUSINESS_ID=your-whatsapp-business-id
WHATSAPP_ACCESS_TOKEN=your-whatsapp-token
```

**How to Get:**
1. Sign up for Meta Business Suite
2. Create WhatsApp Business Account
3. Get API access token from Meta for Developers

---

#### **Telegram Bot:**
```env
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
```

**How to Get:**
1. Open Telegram
2. Search for `@BotFather`
3. Send `/newbot`
4. Follow instructions
5. Copy the token

---

#### **Facebook Messenger:**
```env
FACEBOOK_APP_ID=your-facebook-app-id
FACEBOOK_APP_SECRET=your-facebook-app-secret
```

**How to Get:**
1. Go to developers.facebook.com
2. Create new app
3. Add Messenger product
4. Get App ID & Secret

---

#### **Instagram:**
Uses same Facebook credentials as above

---

#### **Discord:**
```env
DISCORD_BOT_TOKEN=your-discord-bot-token
DISCORD_APPLICATION_ID=your-app-id
```

**How to Get:**
1. Go to discord.com/developers
2. Create new application
3. Go to Bot section
4. Copy bot token

---

#### **TikTok Shop:**
```env
TIKTOK_APP_KEY=your-tiktok-app-key
TIKTOK_APP_SECRET=your-tiktok-app-secret
```

**How to Get:**
1. Register at TikTok for Developers
2. Create seller app
3. Get API credentials

---

## 🚀 **Quick Setup Steps:**

### **Step 1: Add Your Gemini Key**

```bash
# Open the .env file
notepad backend\.env
```

**Find line 39 and replace:**
```env
# BEFORE:
GEMINI_API_KEY=AIzaSyAqai9GTZ7ebu0k7kl0Jdrh9zADo_lGfxM

# AFTER (with your key):
GEMINI_API_KEY=AIzaSy___YOUR_ACTUAL_KEY_HERE___
```

---

### **Step 2: Restart Backend**

```bash
docker-compose restart backend
```

---

### **Step 3: Test AI Chat**

1. Go to `http://localhost:3000/assistant`
2. Type: "Hello, can you help me?"
3. ✅ Should get AI response!

---

## 📋 **What Each Key Unlocks:**

| API Key | Feature | Required? |
|---------|---------|-----------|
| **GEMINI_API_KEY** | AI Chat, Reports, Auto-replies | ✅ **YES** |
| SHOPIFY_* | Shopify integration | ⚠️ Only if using Shopify |
| WHATSAPP_* | WhatsApp messages | ⚠️ Only if using WhatsApp |
| TELEGRAM_* | Telegram bot | ⚠️ Only if using Telegram |
| FACEBOOK_* | Messenger & Instagram | ⚠️ Only if using Facebook |
| DISCORD_* | Discord integration | ⚠️ Only if using Discord |
| TIKTOK_* | TikTok Shop | ⚠️ Only if using TikTok |

---

## 🎯 **Minimum to Get Started:**

**Just need:**
1. ✅ **GEMINI_API_KEY** - This makes the AI work!

**That's it!** The platform will work with just this.

Integration keys are only needed when you actually connect those platforms.

---

## 🔐 **How Integrations Work:**

### **Without Platform Keys (Current):**
- ✅ Can open connection modal
- ✅ Can enter credentials
- ✅ Frontend sends to backend
- ❌ Backend can't validate (no platform keys)

### **With Platform Keys:**
- ✅ Can open connection modal
- ✅ Can enter credentials
- ✅ Frontend sends to backend
- ✅ Backend validates with platform
- ✅ Full integration working!

---

## 🧪 **Test AI Chat (After Adding Gemini Key):**

```bash
# 1. Edit .env
notepad backend\.env

# 2. Add your Gemini key on line 39

# 3. Restart backend
docker-compose restart backend

# 4. Wait 10 seconds

# 5. Test in browser
# Go to: http://localhost:3000/assistant
# Type: "What can you help me with?"
# Should get AI response!
```

---

## 📝 **Full .env Example:**

```env
# AI - REQUIRED ✅
GEMINI_API_KEY=AIzaSyC_YOUR_ACTUAL_KEY_HERE_32_characters

# Integrations - OPTIONAL (only when connecting)
SHOPIFY_API_KEY=your-key-when-ready
SHOPIFY_API_SECRET=your-secret-when-ready

WHATSAPP_ACCESS_TOKEN=your-token-when-ready

TELEGRAM_BOT_TOKEN=123456:ABC-DEF-your-bot-token

FACEBOOK_APP_ID=your-app-id
FACEBOOK_APP_SECRET=your-app-secret
```

---

## ⚡ **What Works Right Now:**

With just **GEMINI_API_KEY**:
- ✅ AI Assistant chat
- ✅ AI-powered customer replies
- ✅ Report generation
- ✅ Smart suggestions
- ✅ Function calling
- ✅ All AI features!

Integration keys only needed when you:
- Want to actually connect Shopify
- Want to send/receive WhatsApp messages
- Want to use Telegram bot
- etc.

---

## 🎉 **Next Steps:**

1. **Give me your Gemini API key**
2. I'll update the `.env` file
3. Restart backend
4. **AI Chat will work!** ✨

For integrations:
- Get keys later when you're ready to connect platforms
- Add them one by one as needed
- Test each integration individually

---

**Ready to add your Gemini key?** 
Just paste it and I'll configure everything! 🚀
