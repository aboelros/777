# 🚀 Quick Start - Test Account Ready!

## ⚡ Super Quick Start (3 Steps)

### 1. Run the App
```bash
run.bat
```

### 2. Open Browser
```
http://localhost:3000
```

### 3. Login
```
Email:    1111111@test.com
Password: 1111111
```

**That's it!** 🎉

---

## 🔐 Test Account Details

The app **automatically creates** a test account on first startup.

### Credentials:
- **Email**: `1111111@test.com`
- **Password**: `1111111`
- **Role**: Admin (full access)
- **Status**: Active

### What's Included:
- ✅ Admin account (ready to use)
- ✅ Demo project (pre-configured)
- ✅ All features enabled
- ✅ AI Assistant ready

---

## 📋 What Happens When You Run `run.bat`

```
Step 1: Check Docker ✅
   └── Docker Desktop must be running

Step 2: Create .env files ✅
   └── Copies settings from .env.example

Step 3: Start containers ✅
   ├── PostgreSQL (Database)
   ├── Redis (Cache)
   ├── Backend (FastAPI)
   └── Frontend (React)

Step 4: Initialize database ✅
   ├── Create tables
   └── Seed test account ⬅️ AUTO-CREATES: 1111111@test.com

Step 5: Ready! ✅
   └── Show login credentials
```

---

## 🎯 Expected Output

When you run `run.bat`, you'll see:

```
========================================
 Server is running!
========================================

 Frontend: http://localhost:3000
 Backend:  http://localhost:8000
 API Docs: http://localhost:8000/docs
 Flower:   http://localhost:5555

========================================
 TEST ACCOUNT (Auto-Created)
========================================

 Email:    1111111@test.com
 Password: 1111111

========================================
```

In the backend logs, you'll also see:

```
🌱 Seeding database with test account...
✅ Test account created successfully!
============================================================
✅ DATABASE READY FOR TESTING!
============================================================
📧 Email: 1111111@test.com
🔑 Password: 1111111
============================================================
```

---

## 🌐 Access Points

After running `run.bat`:

### Frontend (User Interface)
```
http://localhost:3000
```
Login here with the test credentials!

### Backend API
```
http://localhost:8000
```
Direct API access

### API Documentation
```
http://localhost:8000/docs
```
Interactive Swagger UI - test API endpoints

### Task Monitor (Celery Flower)
```
http://localhost:5555
```
Monitor background tasks

---

## 🔄 What Happens On Multiple Runs?

### First Time:
```
run.bat → Creates test account → Shows credentials
```

### Second Time & Beyond:
```
run.bat → Account exists, skip creation → Still shows credentials
```

**No duplicates, no errors!** The app is smart enough to check first. ✨

---

## 🛠️ Useful Commands

### Start Everything
```bash
run.bat
```

### Stop Everything
```bash
docker-compose down
```

### Restart Backend Only
```bash
docker-compose restart backend
```

### View Backend Logs
```bash
docker-compose logs -f backend
```

### View All Logs
```bash
docker-compose logs -f
```

### Rebuild Everything
```bash
docker-compose down
docker-compose up -d --build
```

---

## 🐛 Troubleshooting

### "Can't login" / "Invalid credentials"

**Check 1**: Make sure you're using the correct email format:
```
✅ Correct:   1111111@test.com
❌ Wrong:     1111111
```

**Check 2**: Check backend logs to see if account was created:
```bash
docker-compose logs backend | findstr "Test account"
```

Should show: `✅ Test account created successfully!`

**Check 3**: Restart backend:
```bash
docker-compose restart backend
```

### "Database connection failed"

**Check if PostgreSQL is running:**
```bash
docker-compose ps
```

All services should show **"Up"** status.

**If any service is down, restart all:**
```bash
docker-compose down
docker-compose up -d
```

### "Port already in use"

**Check what's using the port:**
```bash
netstat -ano | findstr :3000
netstat -ano | findstr :8000
```

**Stop other services or change ports in docker-compose.yml**

---

## 🎨 What Can You Do After Login?

Once logged in with `1111111@test.com`:

### 1. Dashboard
- View analytics
- Monitor sales
- Check messages

### 2. Projects
- Manage "Test Project" (auto-created)
- Create new projects

### 3. Integrations
- Connect Shopify
- Connect WhatsApp
- Connect Instagram
- Connect Telegram

### 4. Orders
- View orders from platforms
- Track order status
- Manage fulfillment

### 5. Messages
- View all conversations
- AI-powered responses
- Multi-channel messaging

### 6. AI Assistant
- Configure AI behavior
- Train custom models
- Test AI responses

### 7. Reports
- Generate analytics
- Export data
- View insights

---

## 📚 Next Steps

### For Testing:
1. ✅ Login with test account
2. ✅ Explore the dashboard
3. ✅ Test API endpoints at `/docs`
4. ✅ Configure integrations

### For Development:
1. Check `backend/app/` for API code
2. Check `frontend/src/` for UI code
3. Modify and hot-reload automatically
4. Use test account for API testing

### For Production:
⚠️ **Important**: Disable auto-seeding!

In `backend/app/main.py`:
```python
# Comment out or remove this section:
# if settings.is_development:
#     async with AsyncSessionLocal() as db:
#         await seed_database(db)
```

---

## 💡 Pro Tips

### 1. Keep Docker Desktop Running
The app needs Docker to run. Keep Docker Desktop open.

### 2. Use API Docs for Testing
Visit `http://localhost:8000/docs` to test endpoints without writing code.

### 3. Watch Logs in Real-Time
```bash
docker-compose logs -f backend
```
See what's happening as you use the app.

### 4. Hot Reload is Enabled
Change code → Save → App auto-reloads! No restart needed (most of the time).

### 5. Multiple Terminal Windows
- Window 1: `run.bat` (keeps running)
- Window 2: Run other commands

---

## 🎉 You're All Set!

Just run:
```bash
run.bat
```

Then login at `http://localhost:3000` with:
```
Email:    1111111@test.com
Password: 1111111
```

**Everything else is automatic!** 🚀

---

## 📞 Need Help?

1. Check `TEST_CREDENTIALS.md` for detailed login info
2. Check backend logs: `docker-compose logs backend`
3. Visit API docs: `http://localhost:8000/docs`
4. Check `README.md` for full documentation

Happy testing! 🎊
