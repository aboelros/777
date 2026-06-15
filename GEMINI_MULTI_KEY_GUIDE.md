# 🔑 Gemini Multi-Key System - Complete Guide

## ✅ **FULLY IMPLEMENTED & OPTIMIZED**

Your Gemini AI system now supports **up to 100 API keys** with automatic round-robin load balancing!

---

## 🚀 **How It Works**

### **Automatic Key Rotation:**
```python
# Loads all keys automatically
GEMINI_API_KEY=your_primary_key
GEMINI_API_KEY_1=your_second_key
GEMINI_API_KEY_2=your_third_key
# ... up to GEMINI_API_KEY_100
```

**When you make an AI request:**
1. ✅ Uses Key 1 for first request
2. ✅ Uses Key 2 for second request
3. ✅ Uses Key 3 for third request
4. ✅ Cycles back to Key 1
5. ✅ Automatic round-robin rotation

**Benefits:**
- 📈 **Higher rate limits:** Each key = 60 requests/minute
- 🔄 **Automatic failover:** Switches keys on rate limit
- ⚡ **Better performance:** Distributes load evenly
- 💰 **Cost efficient:** Maximizes free tier usage

---

## 📊 **Rate Limits (Per Key)**

**Free Tier:**
- 60 requests per minute
- 1,500 requests per day
- 1 million tokens per month

**With 10 Keys:**
- 600 requests per minute
- 15,000 requests per day
- 10 million tokens per month

**With 100 Keys:**
- 6,000 requests per minute
- 150,000 requests per day
- 100 million tokens per month

---

## 🎯 **Setup Guide**

### **Option 1: Environment Variables (Local Development)**

Add to your `.env` file:

```env
# Primary key (required)
GEMINI_API_KEY=AIzaSyA...your_first_key

# Additional keys (optional, add as many as you want)
GEMINI_API_KEY_1=AIzaSyB...your_second_key
GEMINI_API_KEY_2=AIzaSyC...your_third_key
GEMINI_API_KEY_3=AIzaSyD...your_fourth_key
GEMINI_API_KEY_4=AIzaSyE...your_fifth_key
# ... continue up to GEMINI_API_KEY_100
```

---

### **Option 2: Render Deployment**

**In Render Dashboard:**

1. Go to your backend service
2. Click **"Environment"** tab
3. Add environment variables:

```
GEMINI_API_KEY: your_primary_key
GEMINI_API_KEY_1: your_second_key
GEMINI_API_KEY_2: your_third_key
GEMINI_API_KEY_3: your_fourth_key
# ... etc
```

**Or use render.yaml** (not recommended for security):
```yaml
envVars:
  - key: GEMINI_API_KEY
    value: your_key_here  # Better: use sync: false
  - key: GEMINI_API_KEY_1
    value: your_second_key
```

---

## 🔐 **How to Get Multiple API Keys**

### **Method 1: Multiple Google Accounts (Easiest)**

1. **Create multiple Google accounts**
   - personal1@gmail.com
   - personal2@gmail.com
   - personal3@gmail.com
   - etc.

2. **For each account:**
   - Go to: https://makersuite.google.com/app/apikey
   - Click "Create API Key"
   - Copy the key
   - Add to your .env file

3. **Result:** 10 accounts = 10 keys = 600 req/min!

---

### **Method 2: Google Cloud Projects (Advanced)**

1. **One Google account, multiple projects:**
   - Go to: https://console.cloud.google.com
   - Create new project: "AI Project 1"
   - Enable Gemini API
   - Create API key
   - Repeat for each project

2. **Limits:** Up to 50 projects per account

---

### **Method 3: Organization Accounts (Enterprise)**

If you have a Google Workspace organization:
- Multiple users
- Each user gets API keys
- Centralized billing
- Higher quotas

---

## 📝 **Quick Setup Script**

### **PowerShell (Windows)**

Create `add_gemini_keys.ps1`:

```powershell
# Add multiple Gemini keys to .env file

$keys = @(
    "AIzaSyA_your_first_key_here",
    "AIzaSyB_your_second_key_here",
    "AIzaSyC_your_third_key_here"
    # Add more keys here
)

# Add to backend/.env
$envFile = "backend\.env"

# Primary key
Add-Content $envFile "`nGEMINI_API_KEY=$($keys[0])"

# Additional keys
for ($i = 1; $i -lt $keys.Length; $i++) {
    Add-Content $envFile "GEMINI_API_KEY_$i=$($keys[$i])"
}

Write-Host "✅ Added $($keys.Length) Gemini API keys to $envFile"
```

Run:
```bash
.\add_gemini_keys.ps1
```

---

### **Bash (Linux/Mac)**

Create `add_gemini_keys.sh`:

```bash
#!/bin/bash

# Add multiple Gemini keys to .env file

keys=(
    "AIzaSyA_your_first_key_here"
    "AIzaSyB_your_second_key_here"
    "AIzaSyC_your_third_key_here"
)

envFile="backend/.env"

# Primary key
echo "GEMINI_API_KEY=${keys[0]}" >> $envFile

# Additional keys
for i in "${!keys[@]}"; do
    if [ $i -gt 0 ]; then
        echo "GEMINI_API_KEY_$i=${keys[$i]}" >> $envFile
    fi
done

echo "✅ Added ${#keys[@]} Gemini API keys to $envFile"
```

Run:
```bash
chmod +x add_gemini_keys.sh
./add_gemini_keys.sh
```

---

## 🧪 **How to Test Multiple Keys Work**

### **Test 1: Check Keys Loaded**

View backend logs after starting:

```
✓ Gemini API configured with 10 API keys
```

This confirms all 10 keys were loaded!

---

### **Test 2: Make Multiple Requests**

Send 10 AI requests quickly:

```python
import httpx
import asyncio

async def test_keys():
    for i in range(10):
        response = await httpx.post(
            "http://localhost:8000/api/v1/assistant/query",
            json={"message": f"Test {i}", "project_id": "..."}
        )
        print(f"Request {i}: {response.status_code}")

asyncio.run(test_keys())
```

**Expected:**
- All 10 requests succeed
- Keys rotate automatically
- No rate limit errors

---

### **Test 3: Monitor Key Rotation**

Enable debug logging in `backend/.env`:

```env
LOG_LEVEL=DEBUG
```

You'll see logs like:
```
DEBUG: Rotated to API key index 0
DEBUG: Rotated to API key index 1
DEBUG: Rotated to API key index 2
...
```

This confirms rotation is working!

---

## 📊 **Usage Tracking with Multiple Keys**

**All keys track usage together:**
```python
# User makes 10 requests using 10 different keys
# Result: User's account shows 10 AI requests total
# Subscription limits apply across ALL keys
```

**Key rotation is transparent:**
- ✅ User sees total usage
- ✅ Subscription limits enforced correctly
- ✅ Overage calculated properly
- ✅ Tokens counted from all keys

---

## 🚨 **Rate Limit Handling**

**What happens on rate limit:**

```python
# Request 1: Key 1 → Success
# Request 2: Key 2 → Success
# Request 3: Key 3 → Success
# ...
# Request 61: Key 1 → Rate limited!
# System: Automatically tries Key 2
# Result: Success (if Key 2 available)
```

**Built-in retry logic:**
1. Tries current key
2. If rate limited → switches to next key
3. If all keys rate limited → returns error
4. Waits and retries automatically

---

## 💡 **Best Practices**

### **Recommended Key Counts:**

**Development:**
- 1-3 keys (sufficient for testing)

**Small Production (<100 users):**
- 5-10 keys (600 req/min)

**Medium Production (100-1000 users):**
- 20-30 keys (1,800 req/min)

**Large Production (1000+ users):**
- 50-100 keys (6,000 req/min)

---

### **Security Tips:**

1. **Never commit keys to Git:**
   ```gitignore
   .env
   *.key
   ```

2. **Use environment variables:**
   - Render dashboard
   - GitHub Secrets
   - AWS Secrets Manager

3. **Rotate keys regularly:**
   - Monthly rotation recommended
   - Deactivate old keys
   - Generate new ones

4. **Monitor usage:**
   - Google Cloud Console
   - Check quotas daily
   - Set up alerts

---

## 📈 **Scaling Strategy**

### **Phase 1: Start Small (1-3 keys)**
```
Users: 1-10
Keys: 1-3
Rate limit: 180 req/min
Cost: Free
```

### **Phase 2: Growth (10-20 keys)**
```
Users: 10-100
Keys: 10-20
Rate limit: 1,200 req/min
Cost: Free (within limits)
```

### **Phase 3: Scale (50-100 keys)**
```
Users: 100-1000+
Keys: 50-100
Rate limit: 6,000 req/min
Cost: Mostly free
```

### **Phase 4: Enterprise (100+ keys)**
```
Users: 1000+
Keys: 100+
Rate limit: 6,000+ req/min
Cost: Consider paid tier
```

---

## 🔧 **Troubleshooting**

### **Problem: Keys not loading**

**Check:**
```bash
# View loaded keys count in logs
docker-compose logs backend | grep "API keys"

# Should see:
# ✓ Gemini API configured with N API keys
```

**Fix:**
- Verify .env syntax (no spaces around =)
- Restart backend
- Check environment variables in Render

---

### **Problem: Still getting rate limited**

**Possible causes:**
1. All keys exhausted (need more keys)
2. Keys not unique (duplicates)
3. High burst traffic

**Solutions:**
- Add more API keys
- Implement request queue
- Add caching layer (already included!)

---

### **Problem: One key invalid**

**System behavior:**
- Skips invalid key automatically
- Uses other valid keys
- Logs warning

**Fix:**
- Check which key is invalid
- Regenerate that key
- Update environment variable

---

## 📋 **Checklist for Production**

Before deploying:

- [ ] Got 5-10 Gemini API keys
- [ ] Added all keys to .env (local)
- [ ] Added all keys to Render (production)
- [ ] Tested multiple keys load
- [ ] Confirmed key rotation works
- [ ] Verified rate limits increased
- [ ] Set up usage monitoring
- [ ] Documented which keys are from which accounts
- [ ] Set calendar reminder to rotate keys monthly
- [ ] Configured alerts for quota limits

---

## 🎉 **Summary**

**What you have now:**
- ✅ Multi-key system (up to 100 keys)
- ✅ Automatic round-robin rotation
- ✅ Rate limit handling with failover
- ✅ Usage tracking across all keys
- ✅ Subscription limits enforced
- ✅ Production-ready implementation

**To maximize performance:**
1. Create 5-10 Google accounts
2. Get API key from each
3. Add to your .env file
4. Deploy to Render
5. Enjoy 10x rate limits!

**Your rate limits with 10 keys:**
- 600 requests per minute
- 15,000 requests per day
- 10 million tokens per month
- **All for FREE!** 🎊

---

## 🔗 **Useful Links**

- **Get API Keys:** https://makersuite.google.com/app/apikey
- **Google Cloud Console:** https://console.cloud.google.com
- **Gemini Docs:** https://ai.google.dev/docs
- **Rate Limits:** https://ai.google.dev/docs/rate_limits
- **Pricing:** https://ai.google.dev/pricing

---

**Your Gemini multi-key system is production-ready!** 🚀

*Last updated: January 2025*
