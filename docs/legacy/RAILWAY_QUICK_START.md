# ⚡ Railway Deployment - Quick Start

## 🚀 5-Minute Deploy Guide

### **Step 1: Push to GitHub** (2 minutes)

```bash
# In project directory
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/ai-sales-commander.git
git push -u origin main
```

Or use the batch file:
```cmd
deploy-to-railway.bat
```

---

### **Step 2: Deploy Backend** (1 minute)

1. Go to **[railway.app](https://railway.app)**
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select **`ai-sales-commander`**
4. Railway auto-detects **backend** service ✅

**That's it! Backend is deploying! 🎉**

---

### **Step 3: Add Database** (30 seconds)

1. In Railway project, click **"+ New"**
2. Select **"Database" → "PostgreSQL"**
3. Done! Database auto-connects ✅

---

### **Step 4: Add Environment Variables** (1 minute)

In Railway Dashboard → Backend Service → Variables, add:

```env
GEMINI_API_KEYS=your-api-key-here
SECRET_KEY=your-random-secret-here
CORS_ORIGINS=*
```

**Deploy complete!** Backend is live! 🚀

---

### **Step 5: Deploy Frontend** (30 seconds)

1. Railway should auto-detect **frontend** service
2. If not, click **"+ New Service"** → Select repo → Set root dir: `frontend`
3. Add variable:
   ```env
   VITE_API_URL=https://your-backend.railway.app/api
   ```

**Done!** Frontend is live! ✨

---

## 🎯 Essential URLs

### **After Deployment:**

1. **Backend API Docs:**
   ```
   https://your-backend-name.railway.app/docs
   ```

2. **Frontend App:**
   ```
   https://your-frontend-name.railway.app
   ```

3. **Health Check:**
   ```
   https://your-backend-name.railway.app/health
   ```

---

## 🔑 Default Login

```
Email: test@example.com
Password: 123
```

---

## ⚙️ Required Environment Variables

### **Backend (Minimum):**
```env
GEMINI_API_KEYS=your-key
SECRET_KEY=random-secret
AUTH_DATABASE_URL=${{Postgres.DATABASE_URL}}
APP_DATABASE_URL=${{Postgres.DATABASE_URL}}
```

### **Frontend:**
```env
VITE_API_URL=https://your-backend.railway.app/api
```

---

## 🐛 Quick Troubleshooting

### **Backend won't start?**
- Check GEMINI_API_KEYS is set
- Verify Postgres database is running
- Check logs in Railway dashboard

### **Frontend can't connect?**
- Update VITE_API_URL with correct backend URL
- Update backend CORS_ORIGINS with frontend URL
- Check both services are deployed

### **502 Error?**
- Wait 2-3 minutes for services to start
- Check backend health: `/docs` endpoint
- Verify PORT environment variable

---

## 💡 Pro Tips

1. **Get your backend URL:**
   - Railway Dashboard → Backend Service → Settings → Domains

2. **Update CORS after frontend deploys:**
   ```env
   CORS_ORIGINS=https://your-frontend.railway.app
   ```

3. **View logs:**
   - Railway Dashboard → Service → Logs tab

4. **Auto-deploy on push:**
   - Every `git push` triggers automatic deployment!

---

## 📚 Full Documentation

For detailed instructions, see: **`RAILWAY_DEPLOYMENT.md`**

---

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Backend service deployed
- [ ] PostgreSQL database added
- [ ] Environment variables configured
- [ ] Frontend service deployed
- [ ] VITE_API_URL set correctly
- [ ] CORS_ORIGINS updated
- [ ] Test login successful

---

## 🎉 You're Live!

**Share your demo:** `https://your-frontend.railway.app`

**Next steps:**
- Add custom domain
- Set up monitoring
- Configure auto-backups
- Scale as needed

---

**Need help?** Check `RAILWAY_DEPLOYMENT.md` for detailed guide!

**Founded October 2025** • Made with ❤️ and raw ambition
