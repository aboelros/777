# 🚀 AI Sales Commander - Setup Guide

## Prerequisites

Before you begin, ensure you have the following installed:

- **Docker Desktop** (Windows/Mac) or Docker Engine (Linux)
- **Docker Compose** v2.0+
- **Node.js** 20+ (for local development)
- **Python** 3.11+ (for local development)
- **Google Cloud Account** (for Vertex AI / Gemini)

## Quick Start with Docker (Recommended)

### 1. Clone and Setup Environment

```bash
# Navigate to project directory
cd "ai-sales-commander"

# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

### 2. Configure Backend Environment

Edit `backend/.env` and set the following required variables:

```env
# Security (REQUIRED - Generate a strong secret key)
SECRET_KEY=your-super-secret-jwt-key-min-32-characters

# Google Cloud / Vertex AI (REQUIRED)
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# Optional: Integration API Keys
SHOPIFY_API_KEY=your-shopify-api-key
SHOPIFY_API_SECRET=your-shopify-api-secret
WHATSAPP_ACCESS_TOKEN=your-whatsapp-token
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
```

### 3. Setup Google Cloud Credentials

#### Option A: Using Service Account (Recommended for Production)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable **Vertex AI API**
4. Create a Service Account:
   - Go to IAM & Admin > Service Accounts
   - Click "Create Service Account"
   - Grant roles: `Vertex AI User` and `Service Account Token Creator`
5. Create and download JSON key
6. Place the key file in `backend/` directory
7. Update `GOOGLE_APPLICATION_CREDENTIALS` in `.env`

#### Option B: Using API Key (Simpler for Development)

1. Go to Google Cloud Console > APIs & Services > Credentials
2. Click "Create Credentials" > "API Key"
3. Add to `.env`: `GOOGLE_API_KEY=your-api-key`

### 4. Start All Services

```bash
# Start all containers
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### 5. Initialize Database

```bash
# Run database migrations
docker-compose exec backend alembic upgrade head

# (Optional) Create initial admin user
docker-compose exec backend python scripts/create_admin.py
```

### 6. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Flower (Celery Monitor)**: http://localhost:5555

### 7. Create Your First Account

1. Navigate to http://localhost:3000
2. Click "Create one now" on the login page
3. Register with your email and password
4. Login with your credentials
5. Create your first project

## Manual Setup (Without Docker)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup database (ensure PostgreSQL is running)
alembic upgrade head

# Start FastAPI server
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Start Background Workers

```bash
cd backend

# Terminal 1: Celery worker
celery -A app.workers.celery_app worker --loglevel=info

# Terminal 2: Celery beat (scheduler)
celery -A app.workers.celery_app beat --loglevel=info

# Terminal 3: Flower (monitoring)
celery -A app.workers.celery_app flower
```

## Configuration Details

### Database Configuration

By default, the application uses PostgreSQL. Connection settings:

```env
DATABASE_URL=postgresql+asyncpg://aisales:changeme@localhost:5432/aisales
```

For production, use a managed database service:
- **Google Cloud SQL**
- **AWS RDS**
- **Azure Database for PostgreSQL**

### Redis Configuration

Redis is used for caching and as a message broker for Celery:

```env
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
```

### CORS Configuration

Update `CORS_ORIGINS` in `.env` with your frontend domains:

```env
# Development
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Production
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

## Integration Setup

### Shopify Integration

1. Create a Shopify Partner account
2. Create a custom app in your store
3. Get API Key and API Secret
4. Configure webhook URLs:
   - Orders: `https://yourdomain.com/api/v1/webhooks/shopify`
   - Enable HMAC verification

### WhatsApp Business API

1. Set up Meta Business Account
2. Create WhatsApp Business App
3. Get Business Phone Number ID and Access Token
4. Configure webhook for incoming messages

### Telegram Bot

1. Create bot with [@BotFather](https://t.me/BotFather)
2. Get bot token
3. Set webhook: `https://yourdomain.com/api/v1/webhooks/telegram`

## Monitoring & Debugging

### View Application Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f celery-worker
```

### Access Database

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U aisales -d aisales

# Common queries
SELECT * FROM users;
SELECT * FROM projects;
SELECT * FROM orders LIMIT 10;
```

### Monitor Celery Tasks

Access Flower dashboard at http://localhost:5555

- View active tasks
- Monitor queue sizes
- Check worker status
- Retry failed tasks

### API Testing

Use the interactive API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Troubleshooting

### Backend won't start

```bash
# Check if PostgreSQL is ready
docker-compose exec postgres pg_isready

# Rebuild backend container
docker-compose up -d --build backend
```

### Database connection errors

```bash
# Reset database
docker-compose down -v
docker-compose up -d postgres
docker-compose exec backend alembic upgrade head
```

### Frontend build errors

```bash
# Clear node_modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Celery tasks not running

```bash
# Check Redis connection
docker-compose exec redis redis-cli ping

# Restart workers
docker-compose restart celery-worker celery-beat
```

## Production Deployment

### Environment Variables

Set `ENVIRONMENT=production` and ensure:

```env
DEBUG=false
SECRET_KEY=<strong-random-key-min-64-chars>
DATABASE_URL=<production-database-url>
CORS_ORIGINS=https://yourdomain.com
```

### Build Production Images

```bash
# Build optimized images
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

### Security Checklist

- [ ] Change all default passwords
- [ ] Generate strong SECRET_KEY (min 64 characters)
- [ ] Use SSL/TLS certificates (HTTPS)
- [ ] Enable firewall rules
- [ ] Set up backup strategy
- [ ] Configure rate limiting
- [ ] Enable monitoring and alerts
- [ ] Rotate API keys regularly
- [ ] Use secrets manager for credentials

## Support

For issues, questions, or contributions:

- **Documentation**: See README.md
- **GitHub Issues**: [Create an issue]
- **Discord**: [Join our community]

---

**Need help?** Check the [FAQ](./FAQ.md) or reach out to our support team.
