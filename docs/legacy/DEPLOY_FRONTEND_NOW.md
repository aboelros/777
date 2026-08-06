# 🎨 Deploy Frontend - Complete Guide

## 🎯 **Two Options: Railway or Vercel**

Both are configured and ready! Choose one:

---

## ✅ **OPTION 1: Railway (Recommended - Same Platform as Backend)**

### **Step 1: Push to GitHub (If Not Done)**

Make sure your code is on GitHub first!

### **Step 2: Create Frontend Service in Railway**

1. Go to: https://railway.app/
2. Open your existing project (where backend is)
3. Click **"+ New"** button
4. Select **"GitHub Repo"**
5. Choose your repository: **"bot trial 2"**
6. Railway will ask: **"Select root directory"**
7. Type: `frontend`
8. Click **"Deploy"**

### **Step 3: Add Environment Variables**

Click on the new frontend service → **"Variables"** tab:

**Add these 2 variables:**

```
VITE_API_URL
```
```
https://your-backend-url.railway.app
```
*(Replace with YOUR actual backend Railway URL)*

---

```
VITE_TESTING_MODE
```
```
false
```

### **Step 4: Get Your Backend URL**

1. Go to your **backend service** in Railway
2. Click **"Settings"** tab
3. Scroll to **"Domains"**
4. Copy the URL (looks like: `https://bot-trial-2-production-xxxx.up.railway.app`)
5. Go back to **frontend Variables**
6. Update `VITE_API_URL` with this URL

### **Step 5: Update Backend CORS**

Go to **backend service** → **"Variables"**:

Find: `CORS_ORIGINS`

Update to include your frontend URL:
```
https://your-frontend-url.railway.app,http://localhost:3000
```

### **Step 6: Railway Auto-Deploys!**

- Frontend will build automatically
- Takes ~2-3 minutes
- You'll get a URL like: `https://frontend-production-xxxx.up.railway.app`

### **Step 7: Test Your App!**

1. Open the frontend URL
2. Login with: `test@aisales.local` / `AiSales2024!Demo`
3. Should connect to backend ✅

---

## ✅ **OPTION 2: Vercel (Faster & Better for React)**

### **Step 1: Go to Vercel**

https://vercel.com/

### **Step 2: Import Project**

1. Click **"Add New..."** → **"Project"**
2. Click **"Import Git Repository"**
3. Find your **"bot trial 2"** repo
4. Click **"Import"**

### **Step 3: Configure Project**

**Framework Preset:** Vite *(auto-detected)*

**Root Directory:** Click **"Edit"** → Type: `frontend`

**Build Command:** `npm run build` *(auto-filled)*

**Output Directory:** `dist` *(auto-filled)*

### **Step 4: Add Environment Variables**

Before clicking "Deploy", scroll down to **"Environment Variables"**:

**Add these:**

| Name | Value |
|------|-------|
| `VITE_API_URL` | `https://your-backend-railway-url.railway.app` |
| `VITE_TESTING_MODE` | `false` |

*(Replace with YOUR actual backend Railway URL)*

### **Step 5: Deploy!**

Click **"Deploy"**

- Vercel builds in ~1-2 minutes
- You get a URL like: `https://bot-trial-2.vercel.app`

### **Step 6: Update Backend CORS**

Go to **Railway** → **Backend Service** → **"Variables"**:

Update `CORS_ORIGINS`:
```
https://bot-trial-2.vercel.app,https://your-vercel-url.vercel.app,http://localhost:3000
```

*(Use YOUR actual Vercel URL)*

### **Step 7: Test!**

1. Open your Vercel URL
2. Login: `test@aisales.local` / `AiSales2024!Demo`
3. Should work! ✅

---

## 📋 **Quick Comparison:**

| Feature | Railway | Vercel |
|---------|---------|--------|
| **Speed** | ~2-3 min | ~1-2 min |
| **Same Platform as Backend** | ✅ Yes | ❌ No |
| **Auto-Deploy on Push** | ✅ Yes | ✅ Yes |
| **Custom Domain** | ✅ Free | ✅ Free |
| **Best For** | Full-stack | Frontend |
| **Ease of Use** | Easy | Easier |

**Recommendation:** Use **Vercel** for frontend (faster, optimized for React)

---

## 🔧 **Environment Variables Explained:**

### **VITE_API_URL**
- **What:** Backend API URL
- **Railway Backend:** `https://your-backend.railway.app`
- **Local:** `http://localhost:8000`
- **Important:** NO trailing slash!

### **VITE_TESTING_MODE**
- **Production:** `false` (requires login)
- **Testing:** `true` (skips login - NOT for production!)

### **VITE_WS_URL** (Optional)
- For WebSocket connections
- Same as VITE_API_URL but with `wss://` instead of `https://`

---

## ✅ **Frontend Variables - Copy/Paste:**

### **For Railway Frontend:**

```
VITE_API_URL
https://your-backend-url.railway.app

VITE_TESTING_MODE
false
```

### **For Vercel Frontend:**

```
VITE_API_URL
https://your-backend-url.railway.app

VITE_TESTING_MODE
false
```

---

## 🚨 **Important: Update Backend CORS!**

After deploying frontend, **update backend** `CORS_ORIGINS`:

**Railway Backend Variables:**

```
CORS_ORIGINS
https://your-frontend-url.railway.app,https://your-frontend.vercel.app,http://localhost:3000
```

Or just:
```
CORS_ORIGINS
*
```
*(Allow all - only for testing, not recommended for production)*

---

## 🧪 **Test Connection:**

After deploying frontend:

1. Open frontend URL in browser
2. Open browser console (F12)
3. Try to login
4. Check console for errors

**If you see CORS errors:**
- Update backend `CORS_ORIGINS` variable
- Include your frontend URL
- Redeploy backend

**If you see "Network Error":**
- Check `VITE_API_URL` is correct
- Backend URL should be https, not http
- No trailing slash in URL

---

## 📖 **Step-by-Step: Railway Frontend**

```
1. Railway Dashboard → Your Project
2. Click "+ New" → GitHub Repo
3. Select "bot trial 2"
4. Root directory: "frontend"
5. Deploy starts automatically
6. Add Variables:
   - VITE_API_URL = [backend URL]
   - VITE_TESTING_MODE = false
7. Wait 2-3 minutes
8. Get frontend URL
9. Update backend CORS_ORIGINS
10. Test frontend URL
11. ✅ Done!
```

---

## 📖 **Step-by-Step: Vercel Frontend**

```
1. vercel.com → New Project
2. Import "bot trial 2" repo
3. Root directory: "frontend"
4. Add Environment Variables:
   - VITE_API_URL = [backend URL]
   - VITE_TESTING_MODE = false
5. Click Deploy
6. Wait 1-2 minutes
7. Get Vercel URL
8. Update backend CORS_ORIGINS
9. Test Vercel URL
10. ✅ Done!
```

---

## 🎯 **What You Need Before Starting:**

✅ Backend deployed on Railway  
✅ Backend URL (from Railway dashboard)  
✅ Code pushed to GitHub  
✅ Railway or Vercel account  

---

## 🐛 **Troubleshooting:**

### **"Failed to fetch" error:**
- Check VITE_API_URL is correct
- Check backend is running
- Check CORS_ORIGINS includes frontend URL

### **Login not working:**
- Check backend database is connected
- Try test account: test@aisales.local / AiSales2024!Demo
- Check browser console for errors

### **Blank page:**
- Check build logs in Railway/Vercel
- Check for JavaScript errors in browser console
- Verify vite.config.js is correct

### **API calls fail:**
- Verify VITE_API_URL is https, not http
- No trailing slash in VITE_API_URL
- Backend must be deployed and running

---

## 🚀 **Recommended Workflow:**

1. ✅ Backend deployed on Railway (DONE)
2. ✅ Backend has environment variables (DONE)
3. ➡️ Deploy frontend on **Vercel** (DO NOW)
4. ➡️ Get Vercel URL
5. ➡️ Update backend CORS_ORIGINS
6. ➡️ Test the app!

---

## 📱 **After Deployment:**

### **Your App URLs:**
- **Backend:** `https://your-backend.railway.app`
- **Frontend:** `https://your-frontend.vercel.app`
- **Admin Login:** test@aisales.local / AiSales2024!Demo

### **Custom Domain (Optional):**
- **Railway:** Settings → Domains → Add custom domain
- **Vercel:** Settings → Domains → Add domain

---

## ✅ **Summary:**

**Choose one:**
- **Railway:** Same platform as backend, easy integration
- **Vercel:** Faster builds, optimized for React ⭐ (Recommended)

**Both are already configured and will work!**

---

**Ready to deploy? Pick Railway or Vercel and follow the steps above!** 🚀
