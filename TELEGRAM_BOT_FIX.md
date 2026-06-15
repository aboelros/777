# 🤖 **TELEGRAM BOT TROUBLESHOOTING GUIDE**

## ❌ **COMMON ISSUES & SOLUTIONS:**

### **1. Bot Token Not Configured**
**Problem**: No `TELEGRAM_BOT_TOKEN` in environment variables
**Solution**: 
```bash
# Add to backend/.env file:
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
```

### **2. No Integration in Database**
**Problem**: Bot exists but no integration record in database
**Solution**: Run the test script to auto-create integration
```bash
cd backend
python test_telegram_bot.py
```

### **3. Webhook Not Set**
**Problem**: Telegram doesn't know where to send messages
**Solution**: Webhook URL should be set to:
```
https://ai-sales-bot-api-production-412b.up.railway.app/api/v1/webhooks/telegram/{project_id}
```

### **4. AI Responses Not Working**
**Problem**: No `GEMINI_API_KEY` configured
**Solution**:
```bash
# Add to backend/.env file:
GEMINI_API_KEY=your_gemini_api_key
```

---

## 🔧 **STEP-BY-STEP FIX:**

### **Step 1: Get Telegram Bot Token**
1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow prompts to create your bot
4. Copy the API token provided
5. Add to backend `.env` file:
   ```bash
   TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ
   ```

### **Step 2: Configure Gemini AI (Optional but Recommended)**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create an API key
3. Add to backend `.env` file:
   ```bash
   GEMINI_API_KEY=AIzaSyAqai9GTZ7ebu0k7kl0Jdrh9zADo_lGfxM
   ```

### **Step 3: Deploy Backend Changes**
1. Push changes to Railway
2. Ensure environment variables are set in Railway dashboard
3. Check deployment logs for errors

### **Step 4: Test Bot Setup**
1. Run diagnostic script:
   ```bash
   cd backend
   python test_telegram_bot.py
   ```
2. This will:
   - ✅ Verify bot token
   - ✅ Test bot connection
   - ✅ Create database integration
   - ✅ Set webhook URL

### **Step 5: Test Bot Functionality**
1. Find your bot on Telegram (use username from test script)
2. Send `/start` or any message
3. Bot should respond with AI-generated message

---

## 🐛 **DEBUGGING CHECKLIST:**

### **Backend Issues:**
- [ ] `TELEGRAM_BOT_TOKEN` set in Railway environment
- [ ] `GEMINI_API_KEY` set in Railway environment  
- [ ] Backend deployed successfully
- [ ] Database connection working
- [ ] Webhook endpoint accessible

### **Bot Issues:**
- [ ] Bot created via @BotFather
- [ ] Bot token copied correctly
- [ ] Webhook URL set correctly
- [ ] Integration exists in database

### **Message Flow:**
1. **User sends message** → Telegram servers
2. **Telegram servers** → Your webhook endpoint
3. **Webhook endpoint** → Saves message to database
4. **Background task** → Processes with AI
5. **AI response** → Sent back to user

---

## 🔍 **MANUAL TESTING:**

### **Test Webhook Endpoint Directly:**
```bash
curl -X POST https://ai-sales-bot-api-production-412b.up.railway.app/api/v1/webhooks/telegram/{project_id} \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "message_id": 123,
      "from": {"id": 12345, "first_name": "Test"},
      "chat": {"id": 12345},
      "text": "Hello bot"
    }
  }'
```

### **Check Railway Logs:**
1. Go to Railway dashboard
2. Select your project
3. Check deployment logs for:
   - Telegram webhook errors
   - Database connection issues
   - AI processing errors

---

## 🎯 **EXPECTED BEHAVIOR:**

### **Working Bot Should:**
1. ✅ Respond to `/start` command
2. ✅ Reply to any text message with AI response
3. ✅ Show "Connected" status in frontend settings
4. ✅ Log successful message processing in Railway logs

### **Common Error Messages:**
- `"No connected Telegram integration found"` → Run test script
- `"Failed to send Telegram message"` → Check bot token
- `"Gemini API error"` → Check GEMINI_API_KEY
- `"Database connection failed"` → Check DATABASE_URL

---

## 🚀 **QUICK FIX COMMANDS:**

```bash
# 1. Set environment variables in Railway
TELEGRAM_BOT_TOKEN=your_token_here
GEMINI_API_KEY=your_key_here

# 2. Run test script after deployment
cd backend
python test_telegram_bot.py

# 3. Test bot by messaging it on Telegram
```

**If bot still doesn't work after following this guide, check Railway deployment logs for specific error messages.**
