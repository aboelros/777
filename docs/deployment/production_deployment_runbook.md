# Automind — Production Deployment Runbook & Operational Launch Guide

**Date:** October 19, 2026  
**Repository:** `C:\Users\ARKAN STOER\Desktop\777`  
**Target Environments:** Staging (`uwxijxxkcraazrkpalyg`), Production (`ccejhzadokkjssjiwmxt`)  
**Deployment Infrastructure:** Render (Backend API + WhatsApp Gateway + Redis), Vercel (Frontend SPA), Supabase (PostgreSQL Databases)  
**Current Alembic Canonical Head:** `d8f3a1e5c2b4` (27 total migrations)  

---

## 1. System Architecture & Topology

```mermaid
flowchart TD
    Client[End User Browser] -->|HTTPS| Vercel[Vercel Frontend SPA]
    Vercel -->|REST / JSON| RenderAPI[Render Backend Web Service]
    
    RenderAPI -->|PostgreSQL AsyncPG| SupabaseProd[(Supabase Production DB)]
    RenderAPI -->|PostgreSQL AsyncPG| ImgStorage[(Dedicated Media DB / product_images)]
    RenderAPI -->|Cache / Deduplication| Redis[Render Redis Service]
    
    RenderAPI <-->|Internal HTTP| Baileys[Render WhatsApp Gateway]
    
    Meta[Meta Cloud API / WhatsApp] -->|Webhooks / HMAC-SHA256| RenderAPI
    Stripe[Stripe Billing] -->|Webhooks / stripe-signature| RenderAPI
    Gemini[Google Gemini AI] <-->|REST API Keys| RenderAPI
```

---

## 2. Step 1: Staging Database Credential Rotation

> [!WARNING]
> Because staging connection parameters were previously referenced during preflight diagnostics, the database password for Supabase project `uwxijxxkcraazrkpalyg` must be rotated before promoting changes to production.

### Operator Actions:
1. Open the [Supabase Management Console](https://supabase.com/dashboard).
2. Select staging project: **`uwxijxxkcraazrkpalyg`** (Region: `aws-0-eu-west-1`).
3. Navigate to **Project Settings** -> **Database**.
4. Scroll to **Database Password** and click **Reset Password**.
5. Generate a new strong password (minimum 24 characters).
6. Update your local/staging environment file:
   ```bash
   STAGING_DATABASE_URL="postgresql+asyncpg://postgres.uwxijxxkcraazrkpalyg:[NEW-PASSWORD]@aws-0-eu-west-1.pooler.supabase.com:5432/postgres"
   ```
7. Verify read-only connectivity using the preflight tool:
   ```powershell
   $env:STAGING_DATABASE_URL="postgresql+asyncpg://postgres.uwxijxxkcraazrkpalyg:[NEW-PASSWORD]@aws-0-eu-west-1.pooler.supabase.com:5432/postgres"
   $env:ENVIRONMENT="staging"
   $env:CONFIRM_READONLY_STAGING_PREFLIGHT="true"
   $env:PYTHONPATH="."
   python -m app.core.staging_preflight
   ```

---

## 3. Step 2: Production Database Migration Protocol

> [!CAUTION]
> Never connect test suites or unvalidated tools to the production database `ccejhzadokkjssjiwmxt`. Only apply migrations using the canonical Alembic chain after backing up the database.

### 2.1 Backup & Safety Verification
1. Open Supabase Dashboard for production project `ccejhzadokkjssjiwmxt`.
2. Under **Database** -> **Backups**, create a manual point-in-time backup snapshot.

### 2.2 Execute Canonical Migrations
From an authorized deployment workstation with production database credentials set:
```bash
# Set production target URL (asyncpg format)
export DATABASE_URL="postgresql+asyncpg://postgres.ccejhzadokkjssjiwmxt:[PROD-PASSWORD]@aws-1-eu-north-1.pooler.supabase.com:5432/postgres"
export APP_DATABASE_URL="$DATABASE_URL"
export AUTH_DATABASE_URL="$DATABASE_URL"
export IMAGE_STORAGE_DATABASE_URL="$DATABASE_URL"
export ENVIRONMENT="production"
export PYTHONPATH="."

# Run canonical Alembic migration chain
python -m alembic upgrade head
```
Verify the output finishes with:
```
INFO  [alembic.runtime.migration] Running upgrade b7d41f09e2a1 -> d8f3a1e5c2b4, create product_images table
```

---

## 4. Step 3: Production Secrets & Environment Variables

Configure the following variables in the **Render Dashboard** (for Web Service and Celery Worker):

| Variable Name | Required | Validation / Constraint | Description / Example |
|---|---|---|---|
| `ENVIRONMENT` | Yes | Must be `production` | Enables fail-closed security and production key enforcement. |
| `DATABASE_URL` | Yes | `postgresql+asyncpg://...` | Application database connection string. |
| `APP_DATABASE_URL` | Yes | `postgresql+asyncpg://...` | Mirrors `DATABASE_URL` for modular service compatibility. |
| `AUTH_DATABASE_URL` | Yes | `postgresql+asyncpg://...` | User & authentication database connection. |
| `IMAGE_STORAGE_DATABASE_URL` | Optional | `postgresql+asyncpg://...` | Dedicated media storage database. Defaults to `APP_DATABASE_URL` if omitted. |
| `SECRET_KEY` | Yes | Minimum 32 characters | Cryptographic key for JWT HS256 token signing. |
| `ENCRYPTION_KEY` | Yes | Valid Fernet 32-byte Base64 key | Used for encrypting customer integration tokens. |
| `GEMINI_API_KEY` | Yes | Google AI Studio Key | Primary LLM key for AI Sales Assistant. |
| `GEMINI_API_KEY_1`..`10` | Optional | Secondary keys | Multi-key rotation pool for rate limit resilience. |
| `WHATSAPP_VERIFY_TOKEN` | Yes | Custom string (e.g. `automind_wa_secret_2026`) | Verification handshake token for Meta Webhook setup. |
| `FACEBOOK_APP_SECRET` | Yes | Hex string from Meta Developer Portal | Used for HMAC-SHA256 signature verification of Meta webhooks. |
| `STRIPE_SECRET_KEY` | Optional | `sk_live_...` or `sk_test_...` | Live Stripe API key for credit card checkout sessions. Falls back to mock links if unset. |
| `STRIPE_WEBHOOK_SECRET` | Optional | `whsec_...` | Stripe webhook signing secret for reconciling payments. |
| `REDIS_URL` | Yes | `redis://...` | Caching, webhook deduplication, and Celery broker. |
| `CORS_ORIGINS` | Yes | Comma-separated HTTPS URLs | e.g. `https://app.automind.com,https://frontend-beryl-eta-37.vercel.app` |

---

## 5. Step 4: Hosting Deployment (Render & Vercel)

### 5.1 Render Deployment (Backend & WhatsApp Gateway)
1. In Render, link the repository `C:\Users\ARKAN STOER\Desktop\777` to a new Blueprint or Web Service.
2. The root [render.yaml](file:///c:/Users/ARKAN%20STOER/Desktop/777/render.yaml) automatically scaffolds:
   - `ai-sales-commander-api`: FastAPI backend running via `render_start.sh`.
   - `ai-sales-bot-whatsapp`: Baileys Node.js gateway on port 3000.
   - `ai-sales-redis`: Redis cache and broker.
3. Set the Environment Variables defined in Section 4 above in the Render Environment tab.
4. Deploy the services.

### 5.2 Vercel Deployment (Frontend SPA)
1. Import the `frontend` subfolder to Vercel.
2. Build Settings:
   - Framework Preset: **Vite**
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`
3. Environment Variables in Vercel:
   - `VITE_API_URL`: `https://[your-render-backend-service].onrender.com`

---

## 6. Step 5: Post-Deployment Smoke-Test Verification

After deployment, perform these verification checks:

### 6.1 Backend Health Check
```bash
curl -i https://[your-api].onrender.com/health
```
**Expected Response:** HTTP 200 `{"status": "healthy", "database": "connected"}`.

### 6.2 Meta Webhook Handshake Verification
```bash
curl -i "https://[your-api].onrender.com/api/v1/webhooks/inbound?hub.mode=subscribe&hub.verify_token=automind_wa_secret_2026&hub.challenge=test_handshake_123"
```
**Expected Response:** HTTP 200 with raw text body `test_handshake_123`.

### 6.3 Stripe Webhook Signature Check
```bash
curl -i -X POST https://[your-api].onrender.com/api/v1/payments/webhooks/stripe \
     -H "Content-Type: application/json" \
     -d '{"type": "ping"}'
```
**Expected Response:** HTTP 400 Bad Request (`{"detail": "Invalid signature"}`) confirming that unauthenticated/tampered webhook payloads are rejected.

### 6.4 Admin Login & Token Rotation
1. Log in via frontend UI at `/login` or via `POST /api/v1/auth/login`.
2. Confirm receipt of `access_token` and HTTP-only `refresh_token` cookie.
3. Test a protected endpoint (e.g. `GET /api/v1/projects`).
