# 🔧 Docker Networking Issue - Solutions

Your Docker containers can't reach the internet to connect to Supabase. This is a common issue on Windows.

---

## 🚨 **The Problem:**

```
Error: [Errno 101] Network is unreachable
```

Docker containers can't resolve or reach: `db.gznafnmgtrgtlxzxxbzy.supabase.co`

---

## ✅ **SOLUTION 1: Create User in Supabase Directly** (FASTEST!)

Since Docker can't reach Supabase, let's create the test user **directly in Supabase**:

### **Step 1: Create User in Auth Database**

1. **Go to Supabase Auth DB:**
   ```
   https://supabase.com/dashboard/project/gznafnmgtrgtlxzxxbzy
   ```

2. **Click "SQL Editor"** (left sidebar)

3. **Copy and paste this SQL:**
   Open the file: `CREATE_USER_SUPABASE.sql`
   
4. **Click "RUN"**

5. **You should see:** ✅ User created successfully!

### **Step 2: Try Login**

Now go to: http://localhost:3000

Login with:
```
Email: test@aisales.local
Password: AiSales2024!Demo
```

**It might still be slow due to Docker networking, but the user exists now!**

---

## ✅ **SOLUTION 2: Run WITHOUT Docker** (RECOMMENDED!)

Bypass Docker completely and run directly on Windows:

### **Step 1: Stop Docker**

```powershell
docker-compose down
```

### **Step 2: Run Backend Directly**

Double-click: `RUN_WITHOUT_DOCKER.bat`

Or manually:
```powershell
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### **Step 3: Run Frontend**

Open new terminal:
```powershell
cd frontend
npm install
npm run dev
```

### **Step 4: Access App**

- Frontend: http://localhost:3000
- Backend: http://localhost:8000

**This will work fast because it's not using Docker networking!**

---

## ✅ **SOLUTION 3: Fix Docker Desktop Settings**

### **Try These:**

**Option A: Restart Docker Desktop**
1. Right-click Docker Desktop tray icon
2. Click "Restart"
3. Wait 2 minutes
4. Run: `docker-compose restart backend`

**Option B: Change Network Settings**
1. Open Docker Desktop
2. Go to **Settings** → **Resources** → **Network**
3. Try these:
   - Uncheck "Use kernel networking for UDP"
   - Change DNS server to 8.8.8.8
   - Enable "Use proxy for containers"

**Option C: Switch to WSL2 Backend**
1. Docker Desktop → Settings → General
2. Enable "Use the WSL 2 based engine"
3. Restart Docker Desktop
4. Run: `docker-compose restart backend`

**Option D: Reset Docker Network**
```powershell
docker network prune
docker-compose down
docker-compose up -d
```

---

## ✅ **SOLUTION 4: Use Local PostgreSQL Instead**

If you want to use Docker, use local PostgreSQL instead of Supabase:

### **Uncomment local postgres in docker-compose.yml:**

Change lines 4-23 from:
```yaml
# postgres:
#   image: postgres:15-alpine
```

To:
```yaml
postgres:
  image: postgres:15-alpine
```

Then update backend environment in docker-compose.yml:
```yaml
environment:
  - AUTH_DATABASE_URL=postgresql+asyncpg://aisales:changeme@postgres:5432/aisales_auth
  - APP_DATABASE_URL=postgresql+asyncpg://aisales:changeme@postgres:5432/aisales_app
```

Then:
```powershell
docker-compose down
docker-compose up -d
```

**This will work because it's all local!**

---

## 🎯 **MY RECOMMENDATION:**

### **For Local Development:**
Use **SOLUTION 2** (Run WITHOUT Docker)
- ✅ Fastest
- ✅ No networking issues  
- ✅ Easy to debug
- ✅ Works with Supabase

### **For Production:**
Deploy to **Railway + Vercel**
- ✅ No Docker networking issues
- ✅ Everything works perfectly
- ✅ Professional hosting
- ✅ Fast and reliable

---

## 📋 **Quick Commands:**

### **Option 1: With Docker (local postgres)**
```powershell
# Edit docker-compose.yml to use local postgres
docker-compose down
docker-compose up -d
```

### **Option 2: Without Docker**
```powershell
# Terminal 1 (Backend)
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload

# Terminal 2 (Frontend)
cd frontend
npm install
npm run dev
```

### **Option 3: Deploy to Cloud**
```powershell
# Push to GitHub
git add .
git commit -m "Ready for deployment"
git push

# Then deploy on Railway + Vercel (no Docker issues!)
```

---

## 🔍 **Diagnose Your Issue:**

Run this to see what's wrong:
```powershell
docker-compose exec backend python check_database.py
```

**Errors you might see:**
- `[Errno -2] Name or service not known` → DNS issue
- `[Errno 101] Network is unreachable` → Network routing issue (your current error)
- `Connection refused` → Firewall issue
- `Timeout` → Network slow or blocked

---

## 💡 **Why This Happens:**

Docker Desktop on Windows uses:
1. **Hyper-V** networking (can have issues)
2. **WSL2** networking (better but can still fail)
3. **NAT** (can block external connections)
4. **VPN** (can interfere with Docker networking)

**Common causes:**
- ❌ VPN is blocking Docker containers
- ❌ Windows Firewall blocking Docker
- ❌ Docker Desktop network config is wrong
- ❌ DNS not configured in Docker
- ❌ Network driver issues

---

## ✅ **What to Do Now:**

1. **First:** Try creating user in Supabase (SOLUTION 1)
2. **Then:** Test login at http://localhost:3000
3. **If slow:** Run without Docker (SOLUTION 2)
4. **Or:** Deploy to Railway + Vercel (works perfectly!)

---

**Choose SOLUTION 2 (Without Docker) for fastest local development!** 🚀
