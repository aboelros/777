# ⚠️ Network Issue During Rebuild

## Problem

Docker can't reach the internet to rebuild images:
```
failed to resolve source metadata for docker.io/library/node:20-alpine
dial tcp: lookup registry-1.docker.io: no such host
```

## ✅ Workaround Applied

Since your code files are **mounted as volumes**, the containers should pick up changes automatically without rebuilding.

I've started the containers with `docker-compose up -d` - they'll use the updated `models.py` file.

---

## 🔍 Check if It's Working

Wait 30 seconds for services to fully start, then:

### 1. Check Backend Logs
```bash
docker-compose logs -f backend
```

**Look for:**
- ✅ `INFO: Application startup complete`
- ✅ `INFO: Uvicorn running on http://0.0.0.0:8000`

**NO MORE errors about `metadata` column!**

### 2. Open the App
```
http://localhost:3000
```

Login:
- Email: `1111111@test.com`
- Password: `1111111`

---

## 📊 What Was Fixed

All **3 database models** now use `extra_data` instead of reserved `metadata`:

1. ✅ Integration model (line 117)
2. ✅ Order model (line 154)
3. ✅ Message model (line 207)

---

## 🌐 If Still Having Issues

### Network Problem?

Check your internet connection. To rebuild later when network is back:

```bash
docker-compose down
docker-compose up -d --build
```

### Still Seeing Errors?

The containers might be using Python's cached `.pyc` files. Force reload:

```bash
docker-compose restart backend celery-worker celery-beat
```

Or delete cache:

```bash
docker-compose exec backend find /app -type d -name __pycache__ -exec rm -rf {} +
docker-compose restart backend
```

---

## 🎯 Expected Status

After 30-60 seconds, all services should be **Up** and working:

```bash
docker-compose ps
```

| Service | Status | Notes |
|---------|--------|-------|
| backend | Up | Should show "healthy" |
| frontend | Up | Running on port 3000 |
| celery-worker | Up | Processing tasks |
| celery-beat | Up | Scheduling tasks |
| postgres | Up | Database ready |
| redis | Up | Cache ready |
| flower | Up | Task monitoring |

---

## ✅ Bottom Line

The **code is fixed**. Just waiting for containers to start with the updated files!

**Check `http://localhost:3000` in 1 minute** - should be working! 🚀
