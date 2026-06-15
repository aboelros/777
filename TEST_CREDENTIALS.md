# 🔐 Test Account Credentials

## Localhost Testing Account

The application automatically creates a test account when you run it for the first time.

### Login Credentials:

```
📧 Email: 1111111@test.com
🔑 Password: 1111111
```

### Account Details:

- **Role**: Admin (full access to all features)
- **Project**: Automatically creates "Test Project" for you
- **Status**: Active and ready to use

---

## How to Login

1. **Start the application**:
   ```bash
   run.bat
   ```

2. **Open browser**:
   ```
   http://localhost:3000
   ```

3. **Login with**:
   - Email: `1111111@test.com`
   - Password: `1111111`

4. **You're in!** 🎉

---

## First Time Setup

When you run `run.bat`, the backend will:

1. ✅ Create database tables
2. ✅ Create test account automatically
3. ✅ Create demo project
4. ✅ Show credentials in logs

You'll see this in the backend logs:

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

## Important Notes

### For Development:
- ✅ This account is **automatically created** on first run
- ✅ You don't need to manually create any accounts
- ✅ Safe for localhost testing

### For Production:
- ⚠️ **DISABLE auto-seeding in production!**
- ⚠️ Change the password immediately
- ⚠️ Use strong, unique credentials

---

## Troubleshooting

### "Account not found" or "Invalid credentials"

**Solution 1**: Restart the backend
```bash
docker-compose restart backend
```

**Solution 2**: Rebuild everything
```bash
docker-compose down
docker-compose up -d --build
```

**Solution 3**: Check backend logs
```bash
docker-compose logs backend | findstr "Test account"
```

You should see: `✅ Test account created successfully!`

### "Database connection error"

Make sure PostgreSQL is running:
```bash
docker-compose ps
```

All services should show "Up" status.

---

## What Happens On Startup

```
Startup Flow:
├── 1. Start PostgreSQL ✅
├── 2. Start Redis ✅
├── 3. Start Backend
│   ├── Connect to database ✅
│   ├── Create tables ✅
│   ├── Check for test account
│   │   ├── Not found? Create it! ✅
│   │   └── Found? Skip creation ✅
│   └── Create demo project ✅
└── 4. Start Frontend ✅
```

---

## Multiple Runs

Don't worry about running `run.bat` multiple times!

The app checks if the test account exists:
- **First run**: Creates account
- **Subsequent runs**: Skips creation (already exists)

No duplicates, no errors! ✨

---

## Default Project

The test account comes with a pre-configured project:

**Project Name**: Test Project
**Features**:
- ✅ AI Assistant enabled
- ✅ Auto-responses enabled
- ✅ Language: English
- ✅ Timezone: UTC

Ready to use immediately!

---

## Quick Login Test

After running `run.bat`, test the login:

```bash
# Test login endpoint
curl -X POST http://localhost:8000/api/v1/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"1111111@test.com\",\"password\":\"1111111\"}"
```

Should return:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

---

## 🚀 Ready to Go!

That's it! Just run `run.bat` and login with:

```
Email: 1111111@test.com
Password: 1111111
```

**Everything is automatic!** 🎉
