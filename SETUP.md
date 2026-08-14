# Setup & Deployment Guide

Welcome to the comprehensive setup and deployment documentation for the AI Sales Commander project. This guide consolidates all legacy documentation, providing a single source of truth for local development, multi-platform deployment (Railway, Render, Vercel), database configuration, and environment variable management.

This document serves as the absolute baseline for all developers onboarding onto the AI Sales Commander ecosystem. We strongly advise reading this document in its entirety before running any commands. The architecture relies heavily on separate microservices, background job workers, and specialized database paradigms (Supabase dual-DB architecture), which require strict adherence to environment configurations.

---

## 1. Prerequisites

Before starting, ensure your local development environment meets the following requirements. If you are missing any of these dependencies, please install them globally on your system.

### Core Dependencies

- **Python**: Version 3.10 or higher. The backend FastAPI architecture heavily leverages Python 3.10+ typing features and asynchronous constructs (`asyncio`).
- **Node.js**: Version 18.x or higher. Required for the frontend React application powered by Vite.
- **npm / yarn / pnpm**: Package managers for Node.js. `npm` is used by default in this guide.
- **Git**: Essential for version control, cloning the repository, and triggering CI/CD pipelines via GitHub.

### Containerization & Services

- **Docker**: Latest version (for running containerized services locally).
- **Docker Compose**: Version 2.0 or higher.
- **Redis**: Version 7.x. If you do not wish to run Redis via Docker, you must install it natively on your local machine. Redis is strictly required for caching LLM responses and acting as the Celery message broker.
- **PostgreSQL**: Version 15+ (Required only if you choose to eject from the Supabase Cloud database infrastructure and host locally).

### Verifying Prerequisites

Run the following commands in your terminal to verify your installations and ensure version compatibility:

```bash
# Check Python version
python --version
# Expected Output: Python 3.10.x or higher

# Check Node.js version
node --version
# Expected Output: v18.x.x or higher

# Check Docker version
docker --version
# Expected Output: Docker version 24.x.x, build ...

# Check Docker Compose version
docker-compose --version
# Expected Output: Docker Compose version v2.x.x
```

If any command returns a "command not found" error or shows a version lower than required, please update the respective software before proceeding.

---

## 2. Local Development Setup

Follow these step-by-step instructions to get the AI Sales Commander running on your local machine natively (without Docker).

### Step 2.1: Clone the Repository

Begin by securely cloning the repository to your local workspace. Ensure you are using the correct branch (usually `main` or `develop`).

```bash
git clone https://github.com/your-username/ai-sales-commander.git
cd ai-sales-commander
```

### Step 2.2: Configure Environment Variables

The project uses extensive environment variables for configuration. The environment variables are split into frontend and backend logic.

Start by copying the provided templates:

```bash
# Copy the COMPLETE_CONFIG.env to your backend directory
cp COMPLETE_CONFIG.env backend/.env

# Navigate to the frontend directory and copy the local env
cd frontend
cp .env.example .env.local
cd ..
```

*Important Note: You MUST edit `backend/.env` and replace `SECRET_KEY` with a securely generated string. Never use the default placeholder secret in production.*

### Step 2.3: Backend Setup

If you prefer to run the backend natively for easier debugging (setting breakpoints in VSCode/PyCharm), follow these steps:

```bash
cd backend

# Create an isolated virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows PowerShell:
venv\Scripts\Activate.ps1
# On Windows CMD:
venv\Scripts\activate.bat
# On macOS / Linux Bash or Zsh:
source venv/bin/activate

# Install the Python dependencies
pip install -r requirements.txt

# Run database migrations to construct the schema
alembic upgrade head

# Start the FastAPI development server with hot-reloading
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

You should see logs indicating the FastAPI server is running on `http://127.0.0.1:8000`.

### Step 2.4: Celery Worker & Beat (Local)

The backend relies on Celery for asynchronous operations like AI bulk processing and email sending. Celery requires two separate processes: a worker and a scheduler (beat).

Open two new terminal windows (ensure your virtual environment is activated in both).

**Terminal A: Start the Celery Worker**
```bash
cd backend
source venv/bin/activate
celery -A app.workers.celery_app worker --loglevel=info
```

**Terminal B: Start the Celery Beat Scheduler**
```bash
cd backend
source venv/bin/activate
celery -A app.workers.celery_app beat --loglevel=info
```

### Step 2.5: Frontend Setup

Finally, initialize the Vite-based React frontend.

```bash
# Open a new terminal window
cd frontend

# Install all Node modules
npm install

# Start the Vite development server
npm run dev
```

The frontend should now be accessible at `http://localhost:3000` or `http://localhost:5173`. Any changes made to the React code will instantly hot-reload.

---

## 3. Environment Variables Reference

Below is the complete list of environment variables required and optional for the AI Sales Commander, aggregated from all configurations (`.env.example`, `COMPLETE_CONFIG.env`, `railway.env.example`). 

This matrix is the definitive source for configuring your deployments.

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| **Core Security Settings** | | | |
| `SECRET_KEY` | Yes | - | Random 40+ character string for JWT signing. Generate using `openssl rand -hex 32`. |
| `ALGORITHM` | No | `HS256` | JWT encoding algorithm. Do not change unless migrating to RS256. |
| `ACCESS_TOKEN_EXPIRE_MINUTES`| No | `1440` | JWT token validity duration in minutes. 1440 = 24 hours. |
| `REFRESH_TOKEN_EXPIRE_DAYS` | No | `7` | Refresh token validity in days. Users must re-login after this. |
| **Application Settings** | | | |
| `APP_NAME` | No | `AI Sales Commander` | Name of the application used in automated emails and UI text. |
| `ENVIRONMENT` | Yes | `development` | Set to `production` during deployments to enable optimizations. |
| `DEBUG` | No | `true` | Enable extensive debug logging. Must be `false` in production. |
| `API_VERSION` | No | `v1` | Global API route prefix (`/api/v1`). |
| `TESTING_MODE` | No | `false` | Extremely dangerous. Bypasses auth for testing routes. Keep `false`. |
| `HOST` | No | `0.0.0.0` | Server binding address. Required for Docker container networking. |
| `PORT` | No | `8000` | Server port binding. |
| **Database Configuration** | | | |
| `AUTH_DATABASE_URL` | Yes | - | Supabase Postgres connection string for authentication & users DB. |
| `APP_DATABASE_URL` | Yes | - | Supabase Postgres connection string for business logic data DB. |
| `DB_POOL_SIZE` | No | `20` | Max active database connections in the SQLAlchemy pool. |
| `DB_MAX_OVERFLOW` | No | `0` | Max connections to create above pool size during traffic spikes. |
| `DB_ECHO` | No | `false` | Enable verbose SQLAlchemy SQL query logging to console. |
| **Redis Configuration** | | | |
| `REDIS_URL` | Yes | `redis://localhost:6379/0` | Primary Redis connection string. |
| `REDIS_PASSWORD` | No | - | Redis authentication password, required if using a managed Redis service. |
| `CELERY_BROKER_URL` | Yes | `redis://localhost:6379/1`| Message broker URL for Celery job distribution. |
| `CELERY_RESULT_BACKEND` | Yes | `redis://localhost:6379/2`| Result backend URL for Celery task statuses. |
| **AI / LLM Settings** | | | |
| `AI_PROVIDER` | No | `gemini` | Choose between `gemini`, `openai`, `anthropic`. |
| `GEMINI_API_KEY` | Yes | - | Primary Google Gemini API Key. |
| `GEMINI_API_KEY_1` - `_100` | No | - | Additional keys for rate-limit rotation (See Section 8). |
| `OPENAI_API_KEY` | No | - | OpenAI API key (if used as fallback). |
| `ANTHROPIC_API_KEY` | No | - | Anthropic API key (if used as fallback). |
| `GROQ_API_KEY` | No | - | Groq API key for high-speed inference operations. |
| `GEMINI_MODEL` | No | `gemini-1.5-pro` | The default Gemini model version string. |
| `GEMINI_MAX_TOKENS` | No | `8192` | Max token limit per generation. Adjust to control costs. |
| `GEMINI_TEMPERATURE` | No | `0.7` | Temperature (0.0 to 1.0) dictating AI creativity. |
| **CORS Configuration** | | | |
| `CORS_ORIGINS` | Yes | `http://localhost:3000` | Comma-separated allowed frontend URLs to prevent CORS errors. |
| **Integrations** | | | |
| `STRIPE_SECRET_KEY` | No | - | Stripe API Secret for backend subscription handling. |
| `STRIPE_WEBHOOK_SECRET` | No | - | Stripe Webhook Secret for payload validation. |
| `WHATSAPP_API_URL` | No | - | Evolution API or Official WhatsApp endpoint URL. |
| `WHATSAPP_ACCESS_TOKEN` | No | - | API Access token for WhatsApp Business integration. |
| `WHATSAPP_BUSINESS_ID` | No | - | Meta WhatsApp Business ID. |
| `TELEGRAM_BOT_TOKEN` | No | - | Bot Token from BotFather for Telegram integration. |
| `SHOPIFY_API_KEY` | No | - | Shopify Integration API Key. |
| `SHOPIFY_API_SECRET` | No | - | Shopify Integration Secret Key. |
| `TWILIO_ACCOUNT_SID` | No | - | Twilio Account SID for SMS Fallbacks. |
| `TWILIO_AUTH_TOKEN` | No | - | Twilio Auth Token. |
| `TWILIO_PHONE_NUMBER` | No | - | Provisioned Twilio Phone Number. |
| **AWS & Storage** | | | |
| `AWS_ACCESS_KEY_ID` | No | - | AWS credentials for S3 uploads (attachments/receipts). |
| `AWS_SECRET_ACCESS_KEY` | No | - | AWS credentials for S3 uploads. |
| `AWS_REGION` | No | `us-east-1` | S3 bucket region. |
| `AWS_BUCKET_NAME` | No | - | S3 bucket name where files are stored. |
| **Monitoring & Logging** | | | |
| `SENTRY_DSN` | No | - | Sentry project DSN for error tracking and APM. |
| `RATE_LIMIT_PER_MINUTE` | No | `60` | API rate limiter max requests per IP address. |
| `LOG_LEVEL` | No | `INFO` | Logger verbosity: DEBUG, INFO, WARNING, ERROR. |
| **Advanced Settings** | | | |
| `ENABLE_SUBSCRIPTION_LIMITS`| No | `true` | Enforces plan limits. Disabling grants all accounts max tier. |
| `ENABLE_OVERAGE_BILLING` | No | `true` | Allows usage over plan limits, generating invoices dynamically. |

---

## 4. Database Setup

This project utilizes a **Dual Database Architecture**. To ensure the highest level of security and scalability, we separate high-security authentication data from heavy-load application data. We strongly recommend using **Supabase** for database hosting.

### 4.1 Supabase Dual DB Setup

You will need two separate Supabase projects (or one project with logically separated schemas, though physical separation is strictly preferred in production).

**Auth Database (Project 1)**
- Tracks users, auth sessions, JWT blocklists, and security-critical elements.
- Connection string format: `postgresql+asyncpg://postgres:[password]@db.gznafnmgtrgtlxzxxbzy.supabase.co:5432/postgres`

**App Database (Project 2)**
- Tracks projects, AI chat logs, chatbot memory, analytics, and billing records.
- Connection string format: `postgresql+asyncpg://postgres:[password]@db.vjdbthhdyemeugyhucoq.supabase.co:5432/postgres`

*(Note: Replace `[password]` with your actual Supabase database passwords. Ensure you are using the `+asyncpg` dialect for asynchronous SQLAlchemy support).*

### 4.2 Running Migrations

Database structures are managed using Alembic. You must run migrations against BOTH databases. The Alembic configuration in this project is explicitly designed to handle dual-database routing automatically based on your `env` setup.

Ensure your `.env` is configured correctly, then run:

```bash
# This automatically handles both databases based on your configuration in env
alembic upgrade head
```

If you ever need to generate a new migration after making structural changes to `models.py`:
```bash
# Autogenerate the migration file
alembic revision --autogenerate -m "Description of changes"

# Apply the new migration to the databases
alembic upgrade head
```

If you encounter a dual-DB metadata error during migrations, you can manually target a specific database stream using Alembic branches (refer to the `alembic.ini` configuration).

---

## 5. Deploy to Railway

Railway is an excellent platform for deploying the backend services (FastAPI + Celery + Redis). It allows seamless orchestration of multi-container architectures.

### Step-by-Step Backend Deployment

1. **Create a Railway Project**
   - Log into Railway and create a new project.
   - Select "Deploy from GitHub repo" and choose the `ai-sales-commander` repository.

2. **Add Redis Database**
   - Click "New" -> "Database" -> "Add Redis".
   - This will provision a Redis instance and automatically expose a `REDIS_URL` internal variable accessible to all services within the Railway project environment.

3. **Configure Environment Variables**
   - Go to your newly deployed backend service -> Variables.
   - Click "Raw Editor" and paste the contents from `railway.env.example`.
   - Update the variables dynamically:
     - `REDIS_URL=${{Redis.REDIS_URL}}`
     - `CELERY_BROKER_URL=${{Redis.REDIS_URL}}`
     - `CELERY_RESULT_BACKEND=${{Redis.REDIS_URL}}`
   - Set `ENVIRONMENT=production`.
   - Set your `GEMINI_API_KEY` and securely generated `SECRET_KEY`.

4. **Network & Domains**
   - Go to Settings -> Networking.
   - Click "Generate Domain" to get a public URL for your backend API (e.g., `ai-sales-commander-production.up.railway.app`).
   - **Important**: Note this URL, as you will need it for the frontend deployment.

5. **Deploy Background Workers (Optional but Recommended)**
   - Create a new service from the same repo.
   - Override the Custom Start Command to: `celery -A app.workers.celery_app worker --loglevel=info`.
   - Ensure the worker service has the exact same Environment Variables as the main web service.

---

## 6. Deploy to Render

Render is an alternative platform. Note that Render's Free Plan has strict limitations on background workers, so Celery must run inside the web dyno using our custom startup script.

### Step-by-Step Render Deployment

1. **Connect GitHub to Render**
   - In the Render Dashboard, click "New" -> "Web Service".
   - Select your GitHub repository.

2. **Configure Web Service**
   - **Name**: `ai-sales-bot-api`
   - **Environment**: Docker
   - **Region**: Oregon (or your preferred region)
   - **Branch**: `main`
   - **Root Directory**: Leave blank (we specify the Dockerfile context in `render.yaml`).
   
3. **Use the render.yaml (Blueprints)**
   - The repository includes a `render.yaml` Blueprint file for Infrastructure-as-Code.
   - Go to the "Blueprints" tab in the Render Dashboard.
   - Connect the repo, and Render will automatically provision:
     - The Redis cache (`ai-sales-bot-redis`).
     - The backend Web Service running `bash render_start.sh`.
   - The `render_start.sh` script spins up the FastAPI server, Celery worker, and Celery beat concurrently inside the single Docker container to bypass the free-tier limitations.

4. **Environment Variables on Render**
   - Even with Blueprints, you must manually supply secrets that are deliberately not synced in the YAML:
     - `AUTH_DATABASE_URL`
     - `APP_DATABASE_URL`
     - `GEMINI_API_KEY`
   - Set `CORS_ORIGINS` to your Vercel frontend URL once generated.

---

## 7. Deploy Frontend to Vercel

Vercel is the strongly recommended host for our Vite/React frontend due to its edge-caching and instantaneous CI/CD pipeline.

### Step-by-Step Frontend Deployment

1. **Create Vercel Project**
   - Go to the Vercel dashboard and click "Add New..." -> "Project".
   - Import your GitHub repository.

2. **Configure Project**
   - **Framework Preset**: Vite
   - **Root Directory**: Select `frontend` from the dropdown menu. This is critical, otherwise Vercel will attempt to build the Python backend.

3. **Environment Variables**
   - Add the following variable in the Deployment Settings:
     - **Name**: `VITE_API_URL`
     - **Value**: The exact URL generated from Railway or Render (e.g., `https://ai-sales-bot-api.onrender.com`). Do not append trailing slashes.

4. **Deploy**
   - Click "Deploy" and wait for the Vite build step to complete.
   - Once successfully deployed, copy the new Vercel domain (e.g., `https://frontend-beryl.vercel.app`).
   
5. **Update Backend CORS**
   - Return to Railway or Render dashboards.
   - Update the `CORS_ORIGINS` variable in your backend service to include the new Vercel domain.
   - Restart the backend service for the CORS middleware to register the new origin.

---

## 8. Gemini API Key Rotation

Google Gemini API endpoints have strict rate limits (typically 60 RPM per key for free/standard tiers). To handle high-volume sales chats natively without external rate-limiting proxies, this system implements an intelligent, in-memory **API Key Rotation Load Balancer**.

### How it Works
The application intercepts outgoing LLM requests and cycles through a pool of available keys. If a key returns a `429 Too Many Requests` error, the application automatically flags it as cooled-down and immediately retries with the next available key, effectively multiplying your rate limit capacity.

### Configuration
In your environment file (e.g., `COMPLETE_CONFIG.env` or Railway Variables), you can define up to 100 API keys using the following precise naming convention:

```env
# Primary Key (Required as fallback)
GEMINI_API_KEY=AIzaSyBG5xvEO...

# Additional Rotation Keys (Optional but heavily recommended for scale)
GEMINI_API_KEY_1=AIzaSyCHgELRAC...
GEMINI_API_KEY_2=AIzaSyCph-7MtU...
GEMINI_API_KEY_3=AIzaSyBwwE2E9y...
# ... continue incrementally up to ...
GEMINI_API_KEY_100=AIzaSyXXXXXX...
```

**Capacity Result Example**: 12 configured keys = 720 requests/minute capacity limit. This is generally sufficient to support a SaaS platform with ~50 active concurrent chatbots.

---

## 9. Docker Compose

For the absolute easiest local development experience without cluttering your host machine with Python virtual environments and Redis installations, the project includes a highly optimized multi-container `docker-compose.yml`.

### Docker Architecture Breakdown
The compose file orchestrates the following microservices:
1. `redis`: Core Cache & Celery Broker mechanism (Alpine image).
2. `backend`: FastAPI Web Server executing `uvicorn` (Hot-reloaded).
3. `celery-worker`: Background Job execution engine.
4. `celery-beat`: Scheduled Job execution engine.
5. `frontend`: React/Vite Dev Server (Port 3000).
6. `proxy`: Nginx reverse proxy routing traffic seamlessly between frontend and backend.

### Using Docker Compose

Ensure your `.env` files are fully populated in both the root/backend and frontend directories.

```bash
# Build the containers and start all services in the background
docker-compose up -d --build

# View real-time logs for a specific service (e.g., the backend API)
docker-compose logs -f backend

# View logs for the Celery worker
docker-compose logs -f celery-worker

# Stop all services safely
docker-compose down
```

*Note: The `docker-compose.yml` purposefully comments out the local `postgres` container because the architecture heavily relies on Supabase for the Dual-DB schema. Ensure your `AUTH_DATABASE_URL` and `APP_DATABASE_URL` in your `.env` point directly to your remote Supabase instances.*

---

## 10. Pre-Deployment Checklist

Before going live to production and allowing actual customer traffic, rigorously verify the following checks. Failure to complete this checklist may result in severe security vulnerabilities, data leaks, or unstable connections.

- [ ] **Secret Keys Changed**: `SECRET_KEY` must be updated from the default to a cryptographically secure 40+ character hash.
- [ ] **Dual DB Connectivity Confirmed**: Both `AUTH_DATABASE_URL` and `APP_DATABASE_URL` are reachable, populated, and migrated exactly to `head`.
- [ ] **Testing Mode Disabled**: Ensure `TESTING_MODE=false`. Leaving this as `true` bypasses all JWT authentication checks globally!
- [ ] **Debug Mode Disabled**: Ensure `DEBUG=false` so verbose tracebacks and internal stack information are hidden from end users.
- [ ] **Environment Set Correctly**: Ensure `ENVIRONMENT=production` to enable production-level optimizations.
- [ ] **CORS Origins Restricted**: `CORS_ORIGINS` should exclusively contain your explicit production frontend URLs (e.g., Vercel and admin panel domains). Ensure `*` is completely removed.
- [ ] **API Keys Validated**: Verify your primary `GEMINI_API_KEY` (and any configured rotation keys) are active, billable, and not expired in Google Cloud Console.
- [ ] **Celery Dependencies Live**: If deploying on Railway, ensure separate Celery Worker services are actively running. If on Render, verify `render_start.sh` executes correctly to launch the background threads.
- [ ] **Default Admin Credentials Reset**: Change the password for the default test account `test@aisales.local` immediately upon the first startup in production.

---

## 11. Troubleshooting

### 11.1 Authentication Errors
If you are seeing "401 Unauthorized" errors right after setup:
- Make sure `SECRET_KEY` is completely identical in the environment config and hasn't changed. If it changes, all JWT tokens are invalidated.
- Verify `TESTING_MODE=false`.

### 11.2 Database Migration Failures
If `alembic upgrade head` fails:
- Double check that `asyncpg` is included in the connection string (`postgresql+asyncpg://...`).
- Ensure both databases in Supabase are active and not paused.
- Delete the `alembic_version` table natively via SQL if you need to perform a hard reset, though this deletes migration history.

### 11.3 Celery Worker Not Receiving Tasks
- Ensure `REDIS_URL` matches exactly between the backend API and the Celery worker environments.
- Verify Redis is running and accepting connections by running `redis-cli ping`.

## 12. Security Notice
**Do not under any circumstances commit your `.env` files to version control.** Always double-check `.gitignore` to verify that `.env`, `COMPLETE_CONFIG.env`, and `.env.local` are explicitly ignored.

---
**End of SETUP.md**

---

## 13. Architectural Overview

The AI Sales Commander is designed around a decoupled, microservices-oriented architecture:

- **Frontend Application (Vite + React)**
  - Fast, modular user interface.
  - Deployed exclusively on edge networks (Vercel) for minimal latency.
  - State management handled by React hooks and context.

- **Backend API (FastAPI)**
  - High-performance, asynchronous web framework for Python.
  - Handles HTTP requests, JWT validation, and business logic routing.
  - Exposes the /api/v1 namespace for frontend consumption.

- **Background Workers (Celery + Redis)**
  - Offloads heavy computational tasks (e.g., massive LLM iterations, bulk email dispatch).
  - Uses Redis as the broker for reliable message queuing.

- **Dual Database Pattern (Supabase/PostgreSQL)**
  - Isolates authentication/PII from standard application telemetry.
  - Reduces the blast radius in the event of a security compromise.

## 14. Support & Contacts

For any critical issues during deployment, please refer to the core team:

1. Devops Lead: devops@aisalescommander.local
2. Security Operations: secops@aisalescommander.local
3. Database Administrator: dba@aisalescommander.local

Ensure you provide your exact ENVIRONMENT variables (excluding sensitive values like SECRET_KEY and passwords) when opening support tickets.

## 15. Change Log

- **v1.0.0**: Initial aggregation of legacy documentation.
- **v1.0.1**: Added Render and Vercel specifics.
- **v1.0.2**: Added Gemini multi-key rotation specifications.

