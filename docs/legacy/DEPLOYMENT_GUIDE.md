# 🚀 AI Sales Commander - Unified Deployment Guide

This guide provides the definitive steps for deploying the backend and frontend.

## 📋 Prerequisites
- **Railway Account** (for Backend, Postgres, and Redis)
- **Vercel Account** (for Frontend)
- **Google Gemini API Key(s)**

---

## 1. Backend Deployment (Railway)

### Recommended Services
1.  **PostgreSQL**: Add a Postgres database service.
2.  **Redis**: Add a Redis service for background tasks.

### Environment Variables
Add these in the **Variables** tab of your backend service:

| Variable | Value / Source |
| :--- | :--- |
| **`DATABASE_URL`** | `${{Postgres.DATABASE_URL}}` |
| **`REDIS_URL`** | `${{Redis.REDIS_URL}}` |
| **`SECRET_KEY`** | `generate-a-random-32-char-string` |
| **`GEMINI_API_KEY`** | `your-primary-gemini-key` |
| **`ENVIRONMENT`** | `production` |
| **`CORS_ORIGINS`** | `https://your-frontend.vercel.app` (Add yours) |
| **`DEBUG`** | `false` |
| **`TESTING_MODE`** | `false` |

---

## 2. Frontend Deployment (Vercel)

### Deployment Settings
- **Root Directory**: `frontend`
- **Framework Preset**: `Vite`
- **Build Command**: `npm run build`
- **Output Directory**: `dist`

### Environment Variables
Add these in Vercel **Project Settings > Environment Variables**:

| Variable | Value |
| :--- | :--- |
| **`VITE_API_URL`** | `https://your-backend.up.railway.app/api/v1` |
| **`VITE_WS_URL`** | `wss://your-backend.up.railway.app` |
| **`VITE_ENVIRONMENT`** | `production` |
| **`VITE_TESTING_MODE`**| `false` |

---

## 🔧 Post-Deployment Checklist
1.  **Verify Backend**: Visit `https://your-backend.up.railway.app/` - should show `{"status": "online"}`.
2.  **Check Logs**: If the backend crashes, check logs for `CRITICAL ERROR: DATABASE_URL is EMPTY`.
3.  **CORS**: Ensure your Vercel URL is added to the backend's `CORS_ORIGINS` variable.
4.  **Database**: Migrations run automatically on startup via `start.sh`.

---

> [!TIP]
> **Performance**: Add `GEMINI_API_KEY_1`, `GEMINI_API_KEY_2` etc. to Railway to enable load balancing across multiple keys for higher speed.
