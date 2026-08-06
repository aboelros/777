# 🚂 Railway Deployment Guide - AI Sales Commander

**Complete guide to deploy your AI Sales Bot on Railway**

---

## 🎯 **Quick Start (5 Minutes)**

### **What You'll Deploy:**
- ✅ Backend (FastAPI + PostgreSQL)
- ✅ Frontend (React + Vite)
- ✅ PostgreSQL Database
- ✅ Redis Cache

---

## 📋 **Prerequisites**

Before starting:
- [ ] Railway account (free tier available)
- [ ] GitHub account with your code pushed
- [ ] 5-10 Gemini API keys ([Get them here](https://makersuite.google.com/app/apikey))

---

## 🚀 **Deployment Steps**

### **Step 1: Create New Project on Railway**

1. Go to https://railway.app/
2. Click **"Start a New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repository: `bot-trial-2`

---

### **Step 2: Add PostgreSQL Database**

1. In your Railway project dashboard
2. Click **"+ New"**
3. Select **"Database"** → **"PostgreSQL"**
4. Railway will auto-create the database
5. Note: `DATABASE_URL` is automatically set!

---

### **Step 3: Add Redis Cache**

1. Click **"+ New"**
2. Select **"Database"** → **"Redis"**
3. Railway will auto-create Redis
4. Note: `REDIS_URL` is automatically set!

---

### **Step 4: Deploy Backend Service**

#### **4.1: Add Service**
1. Click **"+ New"**
2. Select **"GitHub Repo"**
3. Choose your repo again
4. Name it: `backend`

#### **4.2: Configure Backend Settings**

Click on the backend service → **"Settings"** tab:

**Root Directory:**
```
backend
```

**Build Command:** (Auto-detected from nixpacks.toml)
```bash
pip install --upgrade pip && pip install -r requirements.txt
```

**Start Command:** (Auto-detected from nixpacks.toml)
```bash
alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2
```

**Health Check Path:**
```
/health
```

#### **4.3: Add Environment Variables**

Go to **"Variables"** tab and add:

**Required:**
```bash
# Python
PYTHON_VERSION=3.11.0

# Security
SECRET_KEY=<generate-random-32-char-string>
ENVIRONMENT=production
TESTING_MODE=false
DEBUG=false

# Database (auto-set by Railway, but verify)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Redis (auto-set by Railway, but verify)
REDIS_URL=${{Redis.REDIS_URL}}

# Gemini API Keys (IMPORTANT!)
GEMINI_API_KEY=your_key_1_here
GEMINI_API_KEY_1=your_key_2_here
GEMINI_API_KEY_2=your_key_3_here
GEMINI_API_KEY_3=your_key_4_here
GEMINI_API_KEY_4=your_key_5_here
# Add more keys as needed (up to 100)

# CORS (update after frontend deployed)
CORS_ORIGINS=https://your-frontend.railway.app

# Features
ENABLE_SUBSCRIPTION_LIMITS=true
ENABLE_OVERAGE_BILLING=true

# Admin (optional, for first user)
FIRST_SUPERUSER_EMAIL=admin@example.com
FIRST_SUPERUSER_PASSWORD=change_me_after_login
```

**Optional but Recommended:**
```bash
# Logging
LOG_LEVEL=INFO
STRUCTURED_LOGGING=true

# Email (if using)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Monitoring (if using Sentry)
SENTRY_DSN=your_sentry_dsn_here
```

#### **4.4: Deploy Backend**

1. Click **"Deploy"**
2. Wait 2-3 minutes for build
3. Check logs for: ✅ "Application startup complete"
4. Note your backend URL: `https://backend-production-xxxx.up.railway.app`

---

### **Step 5: Deploy Frontend Service**

#### **5.1: Add Service**
1. Click **"+ New"**
2. Select **"GitHub Repo"**
3. Choose your repo
4. Name it: `frontend`

#### **5.2: Configure Frontend Settings**

Click on frontend service → **"Settings"** tab:

**Root Directory:**
```
frontend
```

**Build Command:** (Auto-detected)
```bash
npm ci && npm run build
```

**Start Command:** (Auto-detected)
```bash
npm run preview -- --port $PORT --host 0.0.0.0
```

#### **5.3: Add Environment Variables**

Go to **"Variables"** tab:

```bash
# API URL (use your backend URL from Step 4.4)
VITE_API_URL=https://backend-production-xxxx.up.railway.app

# Optional
NODE_ENV=production
```

#### **5.4: Deploy Frontend**

1. Click **"Deploy"**
2. Wait 2-3 minutes for build
3. Check logs for: ✅ "Network: use --host to expose"
4. Note your frontend URL: `https://frontend-production-xxxx.up.railway.app`

---

### **Step 6: Update CORS**

**Important!** After frontend deploys:

1. Go back to **backend service**
2. Update **CORS_ORIGINS** variable:
   ```bash
   CORS_ORIGINS=https://frontend-production-xxxx.up.railway.app
   ```
3. Backend will auto-redeploy

---

### **Step 7: Test Your Deployment**

#### **7.1: Backend Health Check**
```bash
curl https://backend-production-xxxx.up.railway.app/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected"
}
```

#### **7.2: Frontend Access**
1. Open: `https://frontend-production-xxxx.up.railway.app`
2. You should see the login page
3. Try registering a new user

#### **7.3: Test AI Integration**
1. Login to your app
2. Go to Assistant page
3. Send a message: "Hello"
4. Should get AI response ✅

#### **7.4: Check Subscription System**
1. Go to `/subscription` page
2. Should see 7 tiers
3. Go to `/usage` page
4. Should see usage dashboard ✅

---

## 🔍 **Troubleshooting**

### **Issue 1: "pip: not found"**

**Cause:** Python not detected

**Fix:**
1. Check `backend/runtime.txt` exists with: `python-3.11.0`
2. Check `backend/nixpacks.toml` has: `nixPkgs = ["python311"]`
3. Redeploy

---

### **Issue 2: "alembic: command not found"**

**Cause:** Migrations not running

**Fix:**
1. Check `backend/requirements.txt` has `alembic`
2. Verify `backend/nixpacks.toml` build phase has: `alembic upgrade head`
3. Redeploy

---

### **Issue 3: "Database connection failed"**

**Cause:** DATABASE_URL not set correctly

**Fix:**
1. Go to backend variables
2. Verify: `DATABASE_URL=${{Postgres.DATABASE_URL}}`
3. Or manually set: `postgresql://user:pass@host:port/db`
4. Railway auto-converts `postgres://` to `postgresql://` ✅

---

### **Issue 4: "CORS error" in frontend**

**Cause:** CORS_ORIGINS not matching frontend URL

**Fix:**
1. Update backend `CORS_ORIGINS` to match frontend URL
2. Redeploy backend
3. Clear browser cache

---

### **Issue 5: "Gemini API rate limit"**

**Cause:** Only using 1 API key

**Fix:**
1. Add more keys (5-10 recommended):
   ```bash
   GEMINI_API_KEY_1=key2
   GEMINI_API_KEY_2=key3
   GEMINI_API_KEY_3=key4
   ```
2. Redeploy backend
3. Check logs: "Gemini API configured with N API keys"

---

### **Issue 6: Build fails with module errors**

**Cause:** Missing dependencies

**Fix:**
1. Check `requirements.txt` has all packages
2. Verify no duplicate entries
3. Try locally: `pip install -r requirements.txt`
4. Push fix and redeploy

---

## 📊 **Railway Project Structure**

After deployment, you'll have:

```
Railway Project: AI Sales Commander
├── 📦 backend (FastAPI)
│   ├── Root Dir: /backend
│   ├── Port: Auto-assigned
│   └── URL: backend-production-xxxx.up.railway.app
│
├── 📦 frontend (React)
│   ├── Root Dir: /frontend
│   ├── Port: Auto-assigned
│   └── URL: frontend-production-xxxx.up.railway.app
│
├── 🗄️ PostgreSQL
│   ├── DATABASE_URL: Auto-generated
│   └── Internal hostname: postgres.railway.internal
│
└── 🔴 Redis
    ├── REDIS_URL: Auto-generated
    └── Internal hostname: redis.railway.internal
```

---

## 💰 **Railway Pricing**

### **Free Tier (Starter):**
- ✅ $5 free credits/month
- ✅ Up to 500 hours execution time
- ✅ Up to 100 GB bandwidth
- ✅ Up to 8 GB RAM
- ✅ Shared CPU

**Your app usage (estimated):**
- Backend: ~100-200 hours/month
- Frontend: ~100-200 hours/month
- Database: Always on (~730 hours)
- Redis: ~100 hours/month

**Total: ~$3-5/month** (free tier covers it!)

### **If You Need More:**
- Add credit card for usage beyond free tier
- Pay-as-you-go: ~$0.000463/GB-hour

---

## 🔐 **Security Best Practices**

### **1. Environment Variables**
- ✅ Never commit API keys to Git
- ✅ Use Railway's variables dashboard
- ✅ Rotate keys monthly

### **2. Secret Key**
Generate a strong SECRET_KEY:
```bash
# PowerShell
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | % {[char]$_})

# Or online
https://randomkeygen.com/
```

### **3. Database**
- ✅ Railway auto-creates secure passwords
- ✅ Database only accessible within Railway network
- ✅ Enable SSL in production (auto-enabled)

### **4. CORS**
- ✅ Set specific frontend URL (not *)
- ✅ Update after each frontend URL change

---

## 📈 **Monitoring & Logs**

### **View Logs:**
1. Click on service (backend/frontend)
2. Go to **"Deployments"** tab
3. Click on latest deployment
4. View real-time logs

### **Common Log Messages:**

**✅ Success:**
```
Application startup complete
Uvicorn running on 0.0.0.0:$PORT
Gemini API configured with N API keys
```

**⚠️ Warnings:**
```
No GEMINI_API_KEY set - AI features limited
Waiting for database connection...
```

**❌ Errors:**
```
ERROR: Database connection failed
ERROR: ModuleNotFoundError: No module named 'X'
ERROR: CORS error for origin 'https://...'
```

---

## 🚀 **Post-Deployment Tasks**

### **1. Create Admin User**
```bash
# Option A: Use FIRST_SUPERUSER env vars (automatic)
FIRST_SUPERUSER_EMAIL=admin@example.com
FIRST_SUPERUSER_PASSWORD=secure_password

# Option B: Manual API call
curl -X POST https://backend-production-xxxx.up.railway.app/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"secure_pass","full_name":"Admin"}'
```

### **2. Test All Features**
- [ ] User registration/login
- [ ] AI Assistant chat
- [ ] Subscription tiers visible
- [ ] Usage dashboard works
- [ ] Create project
- [ ] Create order
- [ ] Send message
- [ ] Check usage increments

### **3. Configure Integrations** (if needed)
- [ ] Add Shopify API keys
- [ ] Add Twilio credentials
- [ ] Add Telegram bot token
- [ ] Add social media tokens

### **4. Set Up Monitoring**
- [ ] Add Sentry DSN (error tracking)
- [ ] Set up uptime monitoring (UptimeRobot)
- [ ] Configure alerts

---

## 🔄 **Updating Your App**

### **Automatic Deployments:**
Railway auto-deploys when you push to GitHub!

```bash
# Make changes locally
git add .
git commit -m "Update feature X"
git push origin main

# Railway automatically:
# 1. Detects push
# 2. Builds new version
# 3. Runs tests (if configured)
# 4. Deploys
# 5. Switches to new version
```

### **Manual Redeploy:**
1. Go to service
2. Click **"Deployments"**
3. Click **"Redeploy"** on latest deployment

---

## 📋 **Environment Variables Checklist**

### **Backend - Required:**
```bash
✅ PYTHON_VERSION=3.11.0
✅ SECRET_KEY=<random-string>
✅ DATABASE_URL=${{Postgres.DATABASE_URL}}
✅ REDIS_URL=${{Redis.REDIS_URL}}
✅ GEMINI_API_KEY=<your-key>
✅ CORS_ORIGINS=<frontend-url>
✅ ENVIRONMENT=production
✅ TESTING_MODE=false
✅ DEBUG=false
```

### **Backend - Optional:**
```bash
GEMINI_API_KEY_1=<key2>
GEMINI_API_KEY_2=<key3>
ENABLE_SUBSCRIPTION_LIMITS=true
ENABLE_OVERAGE_BILLING=true
LOG_LEVEL=INFO
FIRST_SUPERUSER_EMAIL=admin@example.com
FIRST_SUPERUSER_PASSWORD=change_me
```

### **Frontend - Required:**
```bash
✅ VITE_API_URL=<backend-url>
✅ NODE_ENV=production
```

---

## 🎯 **Performance Optimization**

### **1. Use Multiple Gemini Keys**
Add 5-10 keys for 10x rate limits:
```bash
GEMINI_API_KEY=key1
GEMINI_API_KEY_1=key2
GEMINI_API_KEY_2=key3
GEMINI_API_KEY_3=key4
GEMINI_API_KEY_4=key5
```

Result: **600 req/min** instead of 60!

### **2. Enable Redis Caching**
Redis is already configured! Benefits:
- ✅ Faster API responses
- ✅ Reduced database load
- ✅ Better performance

### **3. Database Optimization**
- ✅ Alembic migrations auto-run
- ✅ Indexes created automatically
- ✅ Connection pooling enabled

### **4. Frontend Optimization**
- ✅ Vite build optimization
- ✅ Code splitting
- ✅ Asset compression

---

## 🆘 **Get Help**

### **Railway Support:**
- Discord: https://discord.gg/railway
- Docs: https://docs.railway.app/
- Status: https://status.railway.app/

### **Check Logs First:**
1. Go to service
2. Click "Deployments"
3. View logs for error messages
4. Search for ERROR or FAILED

### **Common Solutions:**
- **Build fails:** Check requirements.txt
- **Runtime error:** Check environment variables
- **Connection fails:** Check DATABASE_URL and REDIS_URL
- **CORS error:** Update CORS_ORIGINS

---

## ✅ **Deployment Checklist**

### **Pre-Deployment:**
- [ ] Code pushed to GitHub
- [ ] railway.json configured
- [ ] nixpacks.toml updated (backend & frontend)
- [ ] Got 5-10 Gemini API keys
- [ ] Generated SECRET_KEY

### **During Deployment:**
- [ ] Created Railway project
- [ ] Added PostgreSQL database
- [ ] Added Redis cache
- [ ] Deployed backend with all env vars
- [ ] Deployed frontend with VITE_API_URL
- [ ] Updated CORS_ORIGINS

### **Post-Deployment:**
- [ ] Backend health check passes
- [ ] Frontend loads correctly
- [ ] Created admin user
- [ ] Tested AI assistant
- [ ] Verified subscription system
- [ ] Checked usage tracking
- [ ] Set up monitoring

---

## 🎉 **Success!**

**Your app is live at:**
- 🌐 Frontend: `https://frontend-production-xxxx.up.railway.app`
- 🔧 Backend: `https://backend-production-xxxx.up.railway.app`
- 📚 API Docs: `https://backend-production-xxxx.up.railway.app/docs`

**What works:**
- ✅ User authentication
- ✅ AI Assistant (Google Gemini)
- ✅ 7-tier subscription system
- ✅ Usage tracking
- ✅ Limit enforcement
- ✅ Beautiful dashboard
- ✅ All integrations ready

---

## 📝 **Quick Reference**

### **Useful Commands:**
```bash
# View backend logs
railway logs --service backend

# View frontend logs
railway logs --service frontend

# Open backend URL
railway open --service backend

# Open frontend URL
railway open --service frontend

# Restart service
railway restart --service backend
```

### **Useful URLs:**
```
Frontend: https://your-frontend.railway.app
Backend:  https://your-backend.railway.app
API Docs: https://your-backend.railway.app/docs
Health:   https://your-backend.railway.app/health
```

---

**You're live on Railway!** 🚂🎉

*Deploy time: ~10-15 minutes*  
*Cost: Free tier ($5 credits covers it)*  
*Performance: Production-ready*

---

**Need help?** Check the logs first, then Railway Discord!

*Last updated: January 2025*
