# 🚀 Railway Deployment Guide - AI Sales Commander

Complete guide to deploy your AI Sales Commander project to Railway.

## 📋 Prerequisites

1. **GitHub Account** - Your code must be on GitHub
2. **Railway Account** - Sign up at [railway.app](https://railway.app)
3. **Environment Variables** - Have your API keys ready

---

## 🎯 Quick Deployment Steps

### **Step 1: Push Code to GitHub**

```bash
# Navigate to project directory
cd "c:\Users\ARKAN STOER\Desktop\bot trial 2"

# Initialize git (if not already done)
git init
git add .
git commit -m "Initial commit for Railway deployment"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/ai-sales-commander.git
git branch -M main
git push -u origin main
```

---

### **Step 2: Deploy Backend to Railway**

1. **Go to [railway.app](https://railway.app)** and sign in
2. **Click "New Project"**
3. **Select "Deploy from GitHub repo"**
4. **Choose your repository**: `ai-sales-commander`
5. **Railway will detect two services:**
   - Backend (Python/FastAPI)
   - Frontend (Node.js/Vite)

#### **Backend Configuration:**

**Service Name:** `backend`

**Root Directory:** `backend`

**Build Command:** (Auto-detected)
```bash
pip install -r requirements.txt
```

**Start Command:** (Auto-detected from Procfile)
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

#### **Environment Variables for Backend:**

Add these in Railway Dashboard → Backend Service → Variables:

```env
# App Configuration
APP_NAME=AI Sales Commander
ENVIRONMENT=production
DEBUG=false
API_VERSION=v1

# Database (Use Railway Postgres)
# Railway will auto-inject DATABASE_URL
AUTH_DATABASE_URL=${{Postgres.DATABASE_URL}}
APP_DATABASE_URL=${{Postgres.DATABASE_URL}}

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS (Add your Railway frontend URL)
CORS_ORIGINS=https://your-frontend.railway.app,http://localhost:3000

# Google Gemini API
GEMINI_API_KEYS=your-gemini-api-key-1,your-gemini-api-key-2

# Optional: Other API Keys
SHOPIFY_API_KEY=your-shopify-key
SHOPIFY_API_SECRET=your-shopify-secret
WHATSAPP_ACCESS_TOKEN=your-whatsapp-token
TELEGRAM_BOT_TOKEN=your-telegram-token
```

---

### **Step 3: Add PostgreSQL Database**

1. In Railway Dashboard, click **"+ New"**
2. Select **"Database" → "PostgreSQL"**
3. Railway will auto-create connection variables
4. Backend will automatically use `${{Postgres.DATABASE_URL}}`

---

### **Step 4: Deploy Frontend to Railway**

#### **Frontend Configuration:**

**Service Name:** `frontend`

**Root Directory:** `frontend`

**Build Command:**
```bash
npm install && npm run build
```

**Start Command:**
```bash
npm run preview
```

#### **Environment Variables for Frontend:**

```env
# Backend API URL (Use your Railway backend URL)
VITE_API_URL=https://your-backend.railway.app/api
```

---

### **Step 5: Update Frontend API Configuration**

**Update `frontend/src/services/api.js`:**

```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
```

---

## 🔧 Alternative: Deploy Each Service Separately

### **Option 1: Backend Only**

1. **Create New Project** → Deploy from GitHub
2. **Select** `backend` folder as root directory
3. **Add** PostgreSQL database
4. **Configure** environment variables
5. **Deploy!**

### **Option 2: Frontend Only (Use Existing Backend URL)**

1. **Create New Project** → Deploy from GitHub
2. **Select** `frontend` folder as root directory
3. **Set** `VITE_API_URL` to your backend URL
4. **Deploy!**

---

## 📊 Post-Deployment Setup

### **1. Initialize Database**

Railway will run migrations automatically, but you can also run them manually:

```bash
# In Railway backend service terminal
alembic upgrade head
```

### **2. Test Your Deployment**

1. **Backend Health Check:**
   ```
   https://your-backend.railway.app/docs
   ```

2. **Frontend:**
   ```
   https://your-frontend.railway.app
   ```

3. **Login with:**
   ```
   Email: test@example.com
   Password: 123
   ```

---

## 🎨 Custom Domain (Optional)

### **Backend Domain:**
1. Go to Backend Service → Settings → Domains
2. Click "Generate Domain" or add custom domain
3. Copy the URL

### **Frontend Domain:**
1. Go to Frontend Service → Settings → Domains
2. Click "Generate Domain" or add custom domain
3. Update `VITE_API_URL` with backend URL

---

## 🔒 Security Checklist

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Set `DEBUG=false` in production
- [ ] Use environment variables for all secrets
- [ ] Update `CORS_ORIGINS` with your actual frontend URL
- [ ] Enable Railway's built-in SSL certificates
- [ ] Set up database backups in Railway

---

## 📈 Scaling & Monitoring

### **View Logs:**
- Railway Dashboard → Service → Logs tab

### **Monitor Resources:**
- Railway Dashboard → Service → Metrics tab

### **Scale Services:**
- Railway Dashboard → Service → Settings → Resources

---

## 🐛 Troubleshooting

### **Issue: Build Failed**

**Solution:**
- Check build logs in Railway
- Verify `requirements.txt` or `package.json`
- Ensure Python version compatibility

### **Issue: Database Connection Failed**

**Solution:**
- Verify PostgreSQL service is running
- Check environment variable references: `${{Postgres.DATABASE_URL}}`
- Ensure database migrations ran successfully

### **Issue: Frontend Can't Connect to Backend**

**Solution:**
- Update `VITE_API_URL` with correct backend URL
- Check CORS settings in backend
- Verify both services are deployed

### **Issue: 502 Bad Gateway**

**Solution:**
- Check if backend is running: Visit `/docs`
- Verify `PORT` environment variable is used
- Check start command in Procfile

---

## 💰 Cost Optimization

### **Railway Free Tier:**
- $5 free credit per month
- Enough for small projects
- Auto-sleeps after inactivity

### **Paid Plans:**
- Hobby: $5/month
- Pro: $20/month
- Team: Custom pricing

---

## 🚀 Quick Commands Reference

### **Push Updates:**
```bash
git add .
git commit -m "Your changes"
git push origin main
# Railway auto-deploys on push!
```

### **View Logs:**
```bash
# In Railway CLI (install: npm i -g @railway/cli)
railway logs
```

### **Run Database Migrations:**
```bash
railway run alembic upgrade head
```

---

## 📞 Need Help?

- **Railway Docs:** https://docs.railway.app
- **Railway Discord:** https://discord.gg/railway
- **Project Issues:** Check your GitHub repository

---

## ✅ Deployment Checklist

### **Before Deployment:**
- [ ] Code pushed to GitHub
- [ ] Environment variables documented
- [ ] API keys ready
- [ ] Database schema finalized

### **During Deployment:**
- [ ] Backend service deployed
- [ ] Frontend service deployed
- [ ] PostgreSQL database added
- [ ] Environment variables configured
- [ ] Custom domains set up (optional)

### **After Deployment:**
- [ ] Test backend health endpoint
- [ ] Test frontend access
- [ ] Verify login functionality
- [ ] Check all API integrations
- [ ] Monitor logs for errors

---

## 🎉 Success!

Your AI Sales Commander is now live on Railway! 🚀

**Next Steps:**
1. Share your live demo URL
2. Set up monitoring and alerts
3. Configure automatic backups
4. Add custom domain (optional)
5. Scale as needed

---

**Made with ❤️ by AI Sales Commander Team**
*Founded October 2025*
