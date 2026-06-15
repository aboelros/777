# 🚀 Deploy to Render - Complete Guide

## ✅ **Your App is Ready for Deployment!**

All subscription features, AI tracking, and limit enforcement are fully implemented and will work on Render.

---

## 📋 **Prerequisites**

Before deploying:
- ✅ GitHub account
- ✅ Render account (free at https://render.com)
- ✅ Gemini API key
- ✅ This code pushed to GitHub repository

---

## 🎯 **Quick Deploy (Recommended)**

### **Option 1: Blueprint Deploy (Easiest)**

1. **Push to GitHub:**
```bash
cd "C:\Users\gg\Desktop\bot trial 2"
git init
git add .
git commit -m "Initial commit - AI Sales Bot with subscription system"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ai-sales-bot.git
git push -u origin main
```

2. **Deploy on Render:**
   - Go to https://dashboard.render.com
   - Click **"New" → "Blueprint"**
   - Connect your GitHub repository
   - Render will automatically detect `render.yaml`
   - Click **"Apply"**
   - Done! 🎉

**What Gets Created:**
- ✅ Backend API (`ai-sales-bot-api.onrender.com`)
- ✅ Frontend App (`ai-sales-bot.onrender.com`)
- ✅ PostgreSQL Database (automatic)
- ✅ Redis Cache (automatic)

---

## 🔧 **Option 2: Manual Setup**

### **Step 1: Create PostgreSQL Database**

1. Go to https://dashboard.render.com
2. Click **"New" → "PostgreSQL"**
3. Settings:
   - **Name:** `ai-sales-bot-db`
   - **Database:** `ai_sales_bot`
   - **User:** `ai_sales_bot_user`
   - **Region:** Oregon (or closest to you)
   - **Plan:** Starter (Free)
4. Click **"Create Database"**
5. Copy the **Internal Database URL** (you'll need this)

### **Step 2: Create Redis Instance**

1. Click **"New" → "Redis"**
2. Settings:
   - **Name:** `ai-sales-bot-redis`
   - **Region:** Oregon (same as database)
   - **Plan:** Starter (Free)
   - **Max Memory Policy:** allkeys-lru
3. Click **"Create Redis"**
4. Copy the **Internal Redis URL**

### **Step 3: Deploy Backend API**

1. Click **"New" → "Web Service"**
2. Connect your GitHub repository
3. Settings:
   - **Name:** `ai-sales-bot-api`
   - **Region:** Oregon
   - **Branch:** main
   - **Root Directory:** `backend`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt && chmod +x build.sh && ./build.sh`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Starter (Free)

4. **Environment Variables** (click "Add Environment Variable"):

```env
# Required
DATABASE_URL=<paste-internal-database-url>
REDIS_URL=<paste-internal-redis-url>
SECRET_KEY=<generate-random-64-char-string>
GEMINI_API_KEY=<your-gemini-api-key>

# App Settings
ENVIRONMENT=production
APP_NAME=AI Sales Bot
API_VERSION=v1

# CORS (update after frontend deployed)
CORS_ORIGINS=https://ai-sales-bot.onrender.com

# JWT
JWT_SECRET_KEY=<generate-random-64-char-string>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Optional - Add more Gemini keys for higher rate limits
GEMINI_API_KEY_1=<additional-key>
GEMINI_API_KEY_2=<additional-key>

# Features
ENABLE_SUBSCRIPTION_LIMITS=true
ENABLE_OVERAGE_BILLING=true
ENABLE_AI_CACHING=true
```

5. Click **"Create Web Service"**
6. Wait for deployment (5-10 minutes)
7. Copy your backend URL: `https://ai-sales-bot-api.onrender.com`

### **Step 4: Deploy Frontend**

1. Click **"New" → "Static Site"**
2. Connect your GitHub repository
3. Settings:
   - **Name:** `ai-sales-bot`
   - **Region:** Oregon
   - **Branch:** main
   - **Root Directory:** `frontend`
   - **Build Command:** `npm install && npm run build`
   - **Publish Directory:** `dist`

4. **Environment Variables:**

```env
VITE_API_URL=https://ai-sales-bot-api.onrender.com
VITE_TESTING_MODE=false
```

5. Click **"Create Static Site"**
6. Wait for deployment (3-5 minutes)
7. Your frontend will be at: `https://ai-sales-bot.onrender.com`

### **Step 5: Update Backend CORS**

1. Go to backend service settings
2. Update `CORS_ORIGINS` environment variable:
```env
CORS_ORIGINS=https://ai-sales-bot.onrender.com
```
3. Save changes (will auto-redeploy)

---

## 🔐 **Environment Variables Guide**

### **Required Variables:**

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | From Render database |
| `SECRET_KEY` | App secret key (64 chars) | Generate with `openssl rand -hex 32` |
| `GEMINI_API_KEY` | Google Gemini API key | From Google AI Studio |

### **Recommended Variables:**

| Variable | Description | Default |
|----------|-------------|---------|
| `REDIS_URL` | Redis connection string | From Render Redis |
| `CORS_ORIGINS` | Allowed frontend URLs | Your frontend URL |
| `ENVIRONMENT` | Deployment environment | production |
| `ENABLE_SUBSCRIPTION_LIMITS` | Enable limit enforcement | true |
| `ENABLE_OVERAGE_BILLING` | Enable overage charges | true |

### **Optional - Multiple AI Keys (For Higher Limits):**

```env
GEMINI_API_KEY_1=your_second_key
GEMINI_API_KEY_2=your_third_key
GEMINI_API_KEY_3=your_fourth_key
# ... up to GEMINI_API_KEY_100
```

This enables automatic key rotation when rate limits are hit!

---

## 🗄️ **Database Migration**

Migrations run automatically during deployment via `build.sh`.

**Manual migration (if needed):**

1. Open Render Shell for backend service
2. Run:
```bash
alembic upgrade head
```

**Create new migration:**
```bash
alembic revision --autogenerate -m "description"
```

---

## 🧪 **Testing Your Deployment**

### **1. Test Backend Health:**

```bash
curl https://ai-sales-bot-api.onrender.com/health
```

Should return:
```json
{
  "status": "healthy",
  "version": "v1"
}
```

### **2. Test API Endpoints:**

```bash
# Get subscription plans
curl https://ai-sales-bot-api.onrender.com/api/v1/subscriptions/plans

# Should return all 7 tiers
```

### **3. Test Frontend:**

Open: https://ai-sales-bot.onrender.com

Should see:
- ✅ Login page
- ✅ Dashboard after login
- ✅ Subscription page at `/subscription`
- ✅ Usage page at `/usage`

---

## ⚙️ **Post-Deployment Setup**

### **1. Create Admin User:**

Go to backend Render shell and run:

```python
python << END
import asyncio
from app.core.database import get_async_session
from app.db.models import User, SubscriptionTier, SubscriptionStatus
from app.core.security import get_password_hash
from sqlalchemy import select

async def create_admin():
    async for db in get_async_session():
        # Check if admin exists
        result = await db.execute(select(User).where(User.email == "admin@example.com"))
        if result.scalar_one_or_none():
            print("Admin already exists")
            return
        
        # Create admin
        admin = User(
            email="admin@example.com",
            username="admin",
            hashed_password=get_password_hash("changeme123"),
            full_name="Admin User",
            subscription_tier=SubscriptionTier.ENTERPRISE,
            subscription_status=SubscriptionStatus.ACTIVE
        )
        db.add(admin)
        await db.commit()
        print("Admin created! Email: admin@example.com, Password: changeme123")
        print("⚠️ CHANGE THIS PASSWORD IMMEDIATELY!")
        break

asyncio.run(create_admin())
END
```

### **2. Set Up Monthly Overage Calculation:**

**Option A: Render Cron Job (Recommended)**

1. Go to backend service
2. Add **Cron Job**:
   - **Command:** `python -m app.tasks.overage_calculator`
   - **Schedule:** `0 0 1 * *` (1st of every month at midnight)

**Option B: External Cron Service**

Use services like:
- cron-job.org
- EasyCron
- UptimeRobot

Call endpoint monthly:
```bash
curl -X POST https://ai-sales-bot-api.onrender.com/api/v1/admin/calculate-overages
```

### **3. Configure Monitoring:**

Add to backend env vars:
```env
SENTRY_DSN=<your-sentry-dsn>
```

---

## 🎨 **Custom Domain (Optional)**

### **For Frontend:**

1. Go to frontend service settings
2. Click **"Custom Domains"**
3. Add your domain: `yourdomain.com`
4. Follow DNS instructions
5. Update backend `CORS_ORIGINS`:
```env
CORS_ORIGINS=https://yourdomain.com,https://ai-sales-bot.onrender.com
```

### **For Backend API:**

1. Add custom domain: `api.yourdomain.com`
2. Update frontend `VITE_API_URL`:
```env
VITE_API_URL=https://api.yourdomain.com
```

---

## 📊 **Resource Usage (Free Tier)**

Render Free Tier includes:
- ✅ 750 hours/month (enough for 1 service 24/7)
- ✅ PostgreSQL database (90 days)
- ✅ Redis cache (30 days)
- ✅ Auto-sleep after 15 min inactivity
- ✅ Free SSL certificates

**For Production:**
- **Starter Plan ($7/month):** No sleep, always on
- **Standard Plan ($25/month):** More resources
- **Pro Plan ($85/month):** High performance

---

## 🔄 **Auto-Deploy on Push**

Once connected, Render automatically deploys when you push to GitHub:

```bash
git add .
git commit -m "Updated subscription features"
git push origin main
# Render auto-deploys! 🚀
```

**Check deploy logs:**
- Go to service dashboard
- Click **"Logs"**
- Watch real-time deployment

---

## 🐛 **Troubleshooting**

### **Build Failed:**

**Check logs for errors:**
1. Go to service
2. Click "Logs"
3. Look for red errors

**Common fixes:**
- Missing environment variables
- Database not ready (increase wait time in build.sh)
- Python version mismatch (ensure Python 3.11)

### **Database Connection Error:**

```env
# Make sure DATABASE_URL uses postgresql:// not postgres://
# Render provides postgres:// but SQLAlchemy needs postgresql://
```

Add to your backend code if needed:
```python
database_url = os.getenv("DATABASE_URL", "")
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
```

### **CORS Errors:**

Update `CORS_ORIGINS` to include your frontend URL:
```env
CORS_ORIGINS=https://ai-sales-bot.onrender.com,https://yourdomain.com
```

### **Service Sleeping (Free Tier):**

Free services sleep after 15 min of inactivity.

**Solutions:**
1. Upgrade to Starter plan ($7/mo)
2. Use external monitor (UptimeRobot) to ping every 5 min
3. Accept cold starts (~30 seconds)

---

## 💰 **Cost Estimate**

### **Free Tier (Testing):**
- Backend: Free (sleeps after 15 min)
- Frontend: Free (always on)
- Database: Free (90 days)
- Redis: Free (30 days)
- **Total: $0/month**

### **Production (Starter):**
- Backend: $7/month (always on)
- Frontend: Free (static)
- Database: $7/month (persistent)
- Redis: $10/month (persistent)
- **Total: $24/month**

### **Professional:**
- Backend: $25/month (2GB RAM)
- Frontend: Free
- Database: $20/month (more storage)
- Redis: $10/month
- **Total: $55/month**

---

## ✅ **Deployment Checklist**

Before going live:

**Backend:**
- [ ] All environment variables set
- [ ] Database migrations run successfully
- [ ] Health endpoint responds
- [ ] API endpoints working
- [ ] Subscription features tested
- [ ] AI tracking verified
- [ ] CORS configured

**Frontend:**
- [ ] Build successful
- [ ] API URL configured
- [ ] Pages loading
- [ ] Subscription page shows all tiers
- [ ] Usage page displays data
- [ ] Login working

**Database:**
- [ ] Migrations applied
- [ ] Admin user created
- [ ] Test data added (optional)

**Monitoring:**
- [ ] Sentry configured (optional)
- [ ] Cron job for overages set up
- [ ] Uptime monitoring (optional)

---

## 🎉 **You're Live!**

Your app is now deployed with:
- ✅ All 7 subscription tiers
- ✅ Automatic limit enforcement
- ✅ AI usage tracking
- ✅ Overage calculation
- ✅ Real-time usage monitoring
- ✅ Beautiful frontend dashboard

**URLs:**
- 🌐 Frontend: `https://ai-sales-bot.onrender.com`
- 🔌 API: `https://ai-sales-bot-api.onrender.com`
- 📊 Docs: `https://ai-sales-bot-api.onrender.com/docs`

---

## 📚 **Next Steps**

1. **Test all features** on live site
2. **Create your first project** and integrate
3. **Set up Stripe** for real payments (optional)
4. **Monitor usage** and performance
5. **Scale as needed** with paid plans

---

## 💡 **Pro Tips**

1. **Use render.yaml** for fastest deployment
2. **Enable auto-deploy** from main branch
3. **Set up staging** environment on separate branch
4. **Monitor logs** regularly
5. **Backup database** weekly (Render does this automatically on paid plans)

---

**Need help?**
- Render Docs: https://render.com/docs
- Render Community: https://community.render.com
- Your implementation is production-ready! 🚀

---

*Deployment guide complete - Ready to launch!*
*Last updated: January 2025*
