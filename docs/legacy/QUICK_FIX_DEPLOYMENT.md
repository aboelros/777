# 🔧 Quick Fix for Deployment Error

## ✅ **Files Updated**

Fixed the "pip not found" error by:
1. ✅ Updated `render.yaml` to use Docker runtime
2. ✅ Updated `backend/Dockerfile` to handle PORT env var
3. ✅ Added `backend/runtime.txt` for Python version

---

## 🚀 **Deploy Again (2 Steps)**

### **Step 1: Commit and Push**

**In GitHub Desktop:**
1. You'll see 3 changed files:
   - `render.yaml`
   - `backend/Dockerfile`
   - `backend/runtime.txt`
2. Select all ☑
3. Commit message: `Fix Render deployment - use Docker`
4. Click **"Push origin"**

---

### **Step 2: Delete Old Service & Redeploy**

**On Render Dashboard:**

1. **Delete the broken service:**
   - Go to your service
   - Settings → Delete Service

2. **Deploy with Blueprint:**
   - Click **"New" → "Blueprint"** (important!)
   - Connect your GitHub repo
   - Select branch: `main` or `master`
   - Add environment variables:
     ```
     GEMINI_API_KEY=your_api_key_here
     ```
   - Click **"Apply"**

3. **Wait 10-15 minutes**
   - Docker will build
   - Database will provision
   - Migrations will run

---

## 🎯 **Why This Fix Works**

**Before (Broken):**
```yaml
runtime: python          # ❌ Render couldn't find Python
buildCommand: pip...     # ❌ pip not in PATH
```

**After (Fixed):**
```yaml
runtime: docker          # ✅ Uses your Dockerfile
dockerfilePath: ...      # ✅ Python 3.11 included
```

---

## 🔍 **Verify Deployment**

Once deployed, test:

```bash
# 1. Check health
curl https://ai-sales-bot-api.onrender.com/health

# 2. Check API docs
https://ai-sales-bot-api.onrender.com/docs

# 3. Check frontend
https://ai-sales-bot.onrender.com
```

---

## ⚠️ **Important: Use Blueprint Deploy**

**Don't use:** "New Web Service" (manual)  
**DO use:** "New Blueprint" (automatic)

Blueprint reads `render.yaml` and sets everything up correctly!

---

## 📋 **If Still Having Issues**

### **Error: Can't find Dockerfile**
- Make sure you pushed to GitHub
- Dockerfile must be in `backend/` folder

### **Error: Database connection**
- Wait 2-3 minutes for database to be ready
- Check DATABASE_URL env var is set

### **Error: Module not found**
- Check all Python files are pushed to GitHub
- Verify `requirements.txt` is complete

---

## ✅ **Success Looks Like:**

```
✓ Building Docker image
✓ Installing dependencies  
✓ Running migrations
✓ Starting server
✓ Live at: https://ai-sales-bot-api.onrender.com
```

---

**Now commit these 3 files and redeploy!** 🚀
