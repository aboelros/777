# 🚀 Render Deployment Guide

Your app is now fully configured for Render. Follow these steps to deploy.

---

## Step 1: Push your code to GitHub

Make sure your project is pushed to a GitHub repository. If it's not already, run:
```bash
git add .
git commit -m "Configure for Render deployment"
git push origin main
```

---

## Step 2: Create a Render account

Go to [render.com](https://render.com/) and sign up for a free account. Connect it to your GitHub account.

---

## Step 3: Deploy using render.yaml (Blueprint)

1. On the Render dashboard, click **"New +"** → **"Blueprint"**
2. Connect your GitHub repository
3. Render will automatically detect your `render.yaml` file and show you **5 services** to create:
   - `ai-sales-bot-api` (Backend API)
   - `ai-sales-bot-celery-worker` (Background tasks)
   - `ai-sales-bot-celery-beat` (Scheduler)
   - `ai-sales-bot` (Frontend)
   - `ai-sales-bot-redis` (Redis cache)
4. Click **"Apply"** to create all services at once.

---

## Step 4: Set Required Environment Variables

Some variables are marked `sync: false` — meaning Render will ask you to fill them in manually (for security). You must set these in the Render dashboard for each service.

### For `ai-sales-bot-api` AND `ai-sales-bot-celery-worker`:

Go to: **Dashboard → ai-sales-bot-api → Environment → Add Environment Variable**

| Variable | Value |
|---|---|
| `AUTH_DATABASE_URL` | Your Supabase Auth DB URL (from `backend/.env`) |
| `APP_DATABASE_URL` | Your Supabase App DB URL (from `backend/.env`) |
| `GEMINI_API_KEY` | Your Google Gemini API key |
| `GROQ_API_KEY` | Your Groq API key (if using) |
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token (if using) |
| `WA_GATEWAY_BASE_URL` | Your WhatsApp Gateway URL (if using) |
| `WA_GATEWAY_API_KEY` | Your WhatsApp Gateway API key (if using) |

> ⚠️ **Important:** Copy the same `AUTH_DATABASE_URL` and `APP_DATABASE_URL` values to the `ai-sales-bot-celery-worker` service too. The Celery worker needs database access.

### For `ai-sales-bot-celery-beat` AND `ai-sales-bot-celery-worker`:

Copy the `SECRET_KEY` that Render auto-generated for the API service into these worker services as well (so they share the same JWT secret).

---

## Step 5: Update CORS after deployment

Once all services are deployed, Render will give you the live URLs. Copy the **Frontend URL** (e.g. `https://ai-sales-bot.onrender.com`) and update the backend's `CORS_ORIGINS` environment variable.

Also update the frontend's `VITE_API_URL` to match your actual backend URL if it differs from `https://ai-sales-bot-api.onrender.com`.

---

## Step 6: Verify the deployment

1. Open `https://ai-sales-bot-api.onrender.com/health` — you should see:
   ```json
   {"status": "healthy", "database": "connected"}
   ```
2. Open `https://ai-sales-bot.onrender.com` — your React frontend should load.

---

## ✅ Final Checklist

- [ ] Code pushed to GitHub
- [ ] Blueprint deployed on Render (5 services created)
- [ ] `AUTH_DATABASE_URL` set for API + Celery worker
- [ ] `APP_DATABASE_URL` set for API + Celery worker
- [ ] `GEMINI_API_KEY` set
- [ ] `SECRET_KEY` synced to celery worker and beat
- [ ] Frontend loads at `https://ai-sales-bot.onrender.com`
- [ ] `/health` endpoint returns OK

---

## 🆓 Free Tier Limits (Important)

- On the free plan, Render **spins down** your web services after **15 minutes of inactivity**. The first request after idle takes ~30 seconds.
- The Redis free plan has a **25MB limit** on data storage.
- Workers (Celery) run continuously and **do not spin down**.

To avoid the spin-down behavior, upgrade the API and frontend services to the **$7/month Starter plan**.
