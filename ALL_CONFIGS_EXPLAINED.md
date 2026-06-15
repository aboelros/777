# 📋 Complete Configuration Guide - All Variables & API Keys

## 🎯 **File Created: `COMPLETE_CONFIG.env`**

This file contains **EVERYTHING** - all variables, API keys, credentials, and configurations from your entire project!

---

## 📦 **What's Included:**

### ✅ **1. Core Security (REQUIRED)**
- `SECRET_KEY` - JWT encryption key
- `ALGORITHM` - HS256
- Token expiration settings

### ✅ **2. Application Settings**
- App name, environment, debug mode
- API version, testing mode
- Server host and port

### ✅ **3. Database Configuration (CONFIGURED)**
- ✅ **AUTH_DATABASE_URL** - Supabase Auth DB (users)
- ✅ **APP_DATABASE_URL** - Supabase App DB (data)
- Pool settings and connection config
- Dashboard URLs for both databases

### ✅ **4. Redis Configuration**
- Redis URL (local and production)
- Celery broker and result backend

### ✅ **5. Google Gemini AI (12 KEYS INCLUDED!)**
- **Primary key:** `AIzaSyBG5xvEO2APM2UFNgKsmrvECylnRsYnDpg`
- **11 additional keys** for load balancing
- Support for up to 100 keys total
- Model settings (gemini-1.5-pro-latest)
- **720 requests/minute** with 12 keys!

### ✅ **6. Google Cloud (Optional)**
- GCP project ID
- Service account credentials
- Vertex AI location

### ✅ **7. CORS Configuration**
- Frontend URLs (local and production)
- Comma-separated format

### ✅ **8. Integrations (Optional)**
- Shopify API keys
- WhatsApp credentials
- Telegram bot token
- Facebook app ID/secret
- Twilio SMS settings

### ✅ **9. Email Configuration (Optional)**
- SMTP settings for Gmail
- App password instructions
- Sender email address

### ✅ **10. Stripe Billing (Optional)**
- Secret key
- Webhook secret
- Dashboard link

### ✅ **11. AWS S3 Storage (Optional)**
- Bucket name and region
- Access and secret keys

### ✅ **12. Monitoring**
- Sentry DSN for error tracking
- Rate limiting settings

### ✅ **13. Test Credentials**
- Test account: `test@aisales.local` / `AiSales2024!Demo`
- Test mode credentials

### ✅ **14. Deployment Settings**
- Railway-specific variables
- Render-specific variables
- Environment references

### ✅ **15. Documentation Links**
- All useful dashboards
- API key generation URLs
- Reference documentation

---

## 🚀 **How to Use This File:**

### **For Local Development:**

```bash
# 1. Copy to backend/.env
cp COMPLETE_CONFIG.env backend/.env

# 2. Edit backend/.env:
#    - Generate new SECRET_KEY (keep existing if testing)
#    - Database URLs are already configured (Supabase)
#    - Gemini keys are included (12 keys!)
#    - Set TESTING_MODE=true for easy testing

# 3. Start application
docker-compose up
# OR
run.bat
```

### **For Railway Deployment:**

1. Go to Railway Dashboard
2. Open your backend service
3. Go to Variables tab
4. Copy variables from `COMPLETE_CONFIG.env`
5. Replace local values with Railway syntax:
   - `DATABASE_URL=${{Postgres.DATABASE_URL}}`
   - `REDIS_URL=${{Redis.REDIS_URL}}`
6. Update:
   - `ENVIRONMENT=production`
   - `DEBUG=false`
   - `TESTING_MODE=false`
   - `CORS_ORIGINS=https://your-frontend.railway.app`

### **For Render Deployment:**

Same as Railway but use Render variable syntax:
- `DATABASE_URL=${{DATABASE_URL}}`
- `REDIS_URL=${{REDIS_URL}}`

---

## 🔑 **API Keys Included:**

### **✅ Google Gemini (12 Keys Configured!)**

```
Primary:  AIzaSyBG5xvEO2APM2UFNgKsmrvECylnRsYnDpg
Key #1:   AIzaSyCHgELRACD-xYeI6q_UJNy7OKaZUq52lWM
Key #2:   AIzaSyCph-7MtU2XDeVS6AdmSZ_zot0tY__8Nag
Key #3:   AIzaSyBwwE2E9y4XkzoPqEZI7btEBO9UpM5PCCk
Key #4:   AIzaSyCCmePVW8xWpNJ4up17TKopTY-U3yRs4mc
Key #5:   AIzaSyD2ofs2bp0YijCJKdPld6-qkBxwpaxkBAY
Key #6:   AIzaSyDnqNvIXqjsT9If1x5-DPeJ7oDMzmrF3iE
Key #7:   AIzaSyBIxJ0BOsjRAHRs9mLfvaLfdde3lfjY5w8
Key #8:   AIzaSyATwKEiuLLme0OGyegsKmuupyNiLQNYoqU
Key #9:   AIzaSyAGe4YoIxS2hBCgGvta7SubR2aKqExbNQE
Key #10:  AIzaSyC6hg_lsmnmHt0NvbiyD-TsEq2aEOtdAxw
Key #11:  AIzaSyDcKyWxZwA7cdD1ob5LzsDY3FXgB4IBJXM
```

**Performance:**
- 12 keys × 60 requests/min = **720 requests/minute!**
- 43,200 requests/hour
- 1,036,800 requests/day
- Automatic rotation and failover

**Can add up to 100 keys total!**

---

## 🗄️ **Database Configuration:**

### **✅ Dual Database Architecture (Supabase Cloud)**

**Auth Database (Users & Authentication):**
```
URL: postgresql+asyncpg://postgres:10052008mariem@db.gznafnmgtrgtlxzxxbzy.supabase.co:5432/postgres
Dashboard: https://supabase.com/dashboard/project/gznafnmgtrgtlxzxxbzy
```

**App Database (Projects, Orders, Messages):**
```
URL: postgresql+asyncpg://postgres:10052008mariem@db.vjdbthhdyemeugyhucoq.supabase.co:5432/postgres
Dashboard: https://supabase.com/dashboard/project/vjdbthhdyemeugyhucoq
```

**Both databases are:**
- ✅ Already configured
- ✅ Cloud-hosted (Supabase)
- ✅ Free tier available
- ✅ Accessible from anywhere
- ✅ Production-ready

---

## 🔐 **Test Credentials:**

### **Real Database Login:**
```
Email:    test@aisales.local
Password: AiSales2024!Demo
Role:     Admin
```

**Auto-created on first backend startup.**

### **Test Mode Login (test-login endpoint):**
```
Email:    test@aisales.local OR test@example.com
Password: anything (any password works)
```

**Test mode bypasses database authentication.**

---

## 📊 **Variable Statistics:**

```
Total Variables:           70+
Required for Deployment:   7
Recommended:               12
Optional:                  50+

API Keys Included:         12 Gemini keys
Database URLs:             2 (Auth + App)
Integration Options:       8 services
```

---

## ✅ **Quick Start Checklist:**

### **Local Development:**
- [ ] Copy `COMPLETE_CONFIG.env` to `backend/.env`
- [ ] Verify SECRET_KEY is set
- [ ] Database URLs are configured (Supabase)
- [ ] 12 Gemini API keys are included
- [ ] Set `TESTING_MODE=true` for easy testing
- [ ] Run: `docker-compose up` or `run.bat`
- [ ] Open: http://localhost:3000
- [ ] Login: `test@aisales.local` / any password

### **Railway Deployment:**
- [ ] Add Postgres database in Railway
- [ ] Add Redis database in Railway
- [ ] Copy variables to Railway Dashboard
- [ ] Update: `DATABASE_URL=${{Postgres.DATABASE_URL}}`
- [ ] Update: `REDIS_URL=${{Redis.REDIS_URL}}`
- [ ] Generate new `SECRET_KEY` (40 random chars)
- [ ] Set: `ENVIRONMENT=production`
- [ ] Set: `DEBUG=false`
- [ ] Set: `TESTING_MODE=false`
- [ ] Add all 12 Gemini keys for performance
- [ ] Deploy backend
- [ ] Update `CORS_ORIGINS` with frontend URL

---

## 🎯 **What Each Variable Does:**

### **🔐 Security:**
| Variable | Purpose | Required |
|----------|---------|----------|
| SECRET_KEY | JWT encryption | ✅ Yes |
| ALGORITHM | JWT algorithm (HS256) | ✅ Yes |
| ACCESS_TOKEN_EXPIRE_MINUTES | Token validity | ⚠️ Recommended |
| REFRESH_TOKEN_EXPIRE_DAYS | Refresh token validity | ⚠️ Recommended |

### **💾 Database:**
| Variable | Purpose | Required |
|----------|---------|----------|
| AUTH_DATABASE_URL | User authentication DB | ✅ Yes |
| APP_DATABASE_URL | Application data DB | ✅ Yes |
| DB_POOL_SIZE | Connection pool size | 🟢 Optional |
| DB_MAX_OVERFLOW | Max overflow connections | 🟢 Optional |

### **🤖 AI:**
| Variable | Purpose | Required |
|----------|---------|----------|
| GEMINI_API_KEY | Primary AI key | ✅ Yes |
| GEMINI_API_KEY_1-100 | Additional keys | ⚠️ Recommended |
| GEMINI_MODEL | Model version | 🟢 Optional |
| GEMINI_MAX_TOKENS | Max response length | 🟢 Optional |
| GEMINI_TEMPERATURE | Response creativity | 🟢 Optional |

### **🌐 Application:**
| Variable | Purpose | Required |
|----------|---------|----------|
| ENVIRONMENT | Environment name | ✅ Yes |
| DEBUG | Debug mode | ✅ Yes |
| TESTING_MODE | Skip authentication | 🟢 Optional |
| CORS_ORIGINS | Allowed frontend URLs | ✅ Yes |
| RATE_LIMIT_PER_MINUTE | API rate limiting | 🟢 Optional |

### **🔴 Redis:**
| Variable | Purpose | Required |
|----------|---------|----------|
| REDIS_URL | Cache server | ⚠️ Recommended |
| CELERY_BROKER_URL | Task queue | ⚠️ Recommended |
| CELERY_RESULT_BACKEND | Task results | ⚠️ Recommended |

---

## 🔗 **Important Links:**

### **API Keys & Services:**
- **Gemini API Keys:** https://makersuite.google.com/app/apikey
- **Stripe Dashboard:** https://dashboard.stripe.com/
- **Sentry Error Tracking:** https://sentry.io/
- **Gmail App Passwords:** https://myaccount.google.com/apppasswords
- **AWS Console:** https://console.aws.amazon.com/

### **Databases:**
- **Supabase Auth DB:** https://supabase.com/dashboard/project/gznafnmgtrgtlxzxxbzy
- **Supabase App DB:** https://supabase.com/dashboard/project/vjdbthhdyemeugyhucoq

### **Deployment:**
- **Railway Dashboard:** https://railway.app/
- **Render Dashboard:** https://render.com/

---

## 📚 **Related Documentation:**

| File | Purpose |
|------|---------|
| `COMPLETE_CONFIG.env` | **This file - complete configuration** |
| `ACTUAL_PROJECT_VARIABLES.txt` | Detailed variable explanations |
| `RAILWAY_VARS_FINAL.txt` | Railway deployment guide |
| `COPY_PASTE_VARS.txt` | Quick copy-paste format |
| `RUN_LOCALLY.md` | Local setup guide |
| `LOCAL_SETUP_DETAILED.md` | Detailed local setup |
| `FIX_LOGIN_ERROR.md` | Login troubleshooting |
| `GEMINI_MULTI_KEY_SETUP.md` | Multi-key configuration |
| `SUPABASE_CONFIG.env` | Database configuration |

---

## 🎉 **You're Ready!**

The `COMPLETE_CONFIG.env` file contains:
- ✅ All 70+ environment variables
- ✅ 12 Gemini API keys (720 req/min!)
- ✅ Configured Supabase databases
- ✅ Test credentials
- ✅ All optional integrations
- ✅ Deployment settings
- ✅ Complete documentation

**Everything you need in ONE file!**

---

## 🚀 **Next Steps:**

### **To Run Locally:**
```bash
# 1. Copy configuration
cp COMPLETE_CONFIG.env backend/.env

# 2. Start application
docker-compose up
# OR
run.bat

# 3. Open browser
http://localhost:3000

# 4. Login
Email: test@aisales.local
Password: anything
```

### **To Deploy to Railway:**
1. Open Railway Dashboard
2. Add variables from `COMPLETE_CONFIG.env`
3. Update database URLs to Railway syntax
4. Set ENVIRONMENT=production
5. Deploy!

---

**All configurations extracted from your project and consolidated into one file!** 🎯

**File: `COMPLETE_CONFIG.env`** - Ready to use! 🚀
