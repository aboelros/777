# 🚀 Production Deployment Guide

## 📋 **Complete guide to deploy AI Sales Commander to production**

---

## 🎯 **Prerequisites:**

- ✅ Domain name (e.g., `aisalescommander.com`)
- ✅ VPS/Cloud server (AWS, DigitalOcean, Azure, etc.)
- ✅ SSL Certificate (Let's Encrypt recommended)
- ✅ PostgreSQL database (production-ready)
- ✅ Redis server
- ✅ Docker & Docker Compose installed

---

## 📊 **Architecture Overview:**

```
Internet
   ↓
Nginx (SSL/Reverse Proxy)
   ↓
Docker Network
   ├── Frontend (React)
   ├── Backend (FastAPI)
   ├── PostgreSQL (Database)
   ├── Redis (Cache/Queue)
   └── Celery (Background Tasks)
```

---

## 🔒 **Step 1: Database Setup (Production)**

### **Option A: Managed PostgreSQL (Recommended)**

Use managed database services:
- ✅ AWS RDS PostgreSQL
- ✅ Azure Database for PostgreSQL
- ✅ DigitalOcean Managed Databases
- ✅ Heroku Postgres
- ✅ Supabase

**Benefits:**
- Automatic backups
- High availability
- Automatic scaling
- Managed security updates

### **Option B: Self-Hosted PostgreSQL**

```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Create production database
sudo -u postgres psql

CREATE DATABASE aisales_prod;
CREATE USER aisales_prod WITH ENCRYPTED PASSWORD 'YOUR_SECURE_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE aisales_prod TO aisales_prod;
\q
```

### **Configure Database for Production:**

```sql
-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Set up connection pooling
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_io_concurrency = 200;

-- Reload configuration
SELECT pg_reload_conf();
```

---

## 🔐 **Step 2: Environment Variables (Production)**

Create `backend/.env.production`:

```env
# Application
APP_NAME=AI Sales Commander
ENVIRONMENT=production
DEBUG=false
API_VERSION=v1
TESTING_MODE=false

# Server
HOST=0.0.0.0
PORT=8000

# Security - GENERATE NEW KEYS!
SECRET_KEY=your-super-secure-production-jwt-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database - Use production database URL
DATABASE_URL=postgresql+asyncpg://aisales_prod:YOUR_SECURE_PASSWORD@your-db-host:5432/aisales_prod
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10

# Redis - Use production Redis
REDIS_URL=redis://your-redis-host:6379/0
REDIS_PASSWORD=YOUR_REDIS_PASSWORD

# Celery
CELERY_BROKER_URL=redis://your-redis-host:6379/1
CELERY_RESULT_BACKEND=redis://your-redis-host:6379/2

# Gemini AI - Your 44 API Keys
GEMINI_API_KEY=AIzaSyBG5xvEO2APM2UFNgKsmrvECylnRsYnDpg
GEMINI_API_KEY_1=AIzaSyCHgELRACD-xYeI6q_UJNy7OKaZUq52lWM
# ... (add all 44 keys)
GEMINI_API_KEY_43=AIzaSyB7BMizW3evWKF7Aq6nWnfM0n3AQ2Qr3Go
GEMINI_MODEL=gemini-2.0-flash

# CORS - Set your production domain
CORS_ORIGINS=https://aisalescommander.com,https://www.aisalescommander.com,https://app.aisalescommander.com

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100

# Monitoring - Optional: Add Sentry for error tracking
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id

# Storage - Optional: S3 for file uploads
S3_BUCKET_NAME=aisales-uploads
S3_REGION=us-east-1
S3_ACCESS_KEY=YOUR_AWS_ACCESS_KEY
S3_SECRET_KEY=YOUR_AWS_SECRET_KEY

# Email - Optional: For notifications
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@aisalescommander.com

# Integrations - Add your production keys
SHOPIFY_API_KEY=your-production-shopify-key
SHOPIFY_API_SECRET=your-production-shopify-secret
WHATSAPP_BUSINESS_ID=your-whatsapp-business-id
WHATSAPP_ACCESS_TOKEN=your-whatsapp-token
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
FACEBOOK_APP_ID=your-facebook-app-id
FACEBOOK_APP_SECRET=your-facebook-app-secret
```

---

## 🐳 **Step 3: Docker Compose (Production)**

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    ports:
      - "80:80"
      - "443:443"
    environment:
      - REACT_APP_API_URL=https://api.aisalescommander.com
    volumes:
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - backend
    restart: unless-stopped

  backend:
    build: ./backend
    env_file:
      - ./backend/.env.production
    ports:
      - "8000:8000"
    depends_on:
      - redis
    restart: unless-stopped
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

  celery-worker:
    build: ./backend
    env_file:
      - ./backend/.env.production
    command: celery -A app.workers.celery_app worker --loglevel=info --concurrency=4
    depends_on:
      - backend
      - redis
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass YOUR_REDIS_PASSWORD
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

---

## 🔧 **Step 4: Database Migrations**

```bash
# Install Alembic (if not already installed)
pip install alembic

# Initialize Alembic (first time only)
cd backend
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations to production
alembic upgrade head
```

---

## 🌐 **Step 5: Nginx Configuration**

Create `nginx/nginx.conf`:

```nginx
server {
    listen 80;
    server_name aisalescommander.com www.aisalescommander.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name aisalescommander.com www.aisalescommander.com;
    
    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Frontend
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://backend:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # WebSocket support for real-time features
    location /ws/ {
        proxy_pass http://backend:8000/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## 🚀 **Step 6: Deploy to Production**

```bash
# 1. Clone your repository on production server
git clone https://github.com/your-repo/ai-sales-commander.git
cd ai-sales-commander

# 2. Set up environment variables
cp backend/.env.example backend/.env.production
nano backend/.env.production  # Edit with production values

# 3. Build and start services
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# 4. Run database migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# 5. Check logs
docker-compose -f docker-compose.prod.yml logs -f

# 6. Verify services
curl https://aisalescommander.com/health
```

---

## 🔒 **Step 7: Security Checklist**

- [ ] ✅ Generate new `SECRET_KEY` for JWT
- [ ] ✅ Use strong database passwords
- [ ] ✅ Enable firewall (UFW/iptables)
- [ ] ✅ Set up SSL certificates (Let's Encrypt)
- [ ] ✅ Disable DEBUG mode
- [ ] ✅ Set proper CORS origins
- [ ] ✅ Enable rate limiting
- [ ] ✅ Set up database backups
- [ ] ✅ Configure log rotation
- [ ] ✅ Enable monitoring (Sentry, Datadog)
- [ ] ✅ Set up health checks
- [ ] ✅ Use secrets management (AWS Secrets Manager, Vault)

---

## 📊 **Step 8: Monitoring & Maintenance**

### **Health Checks:**
```bash
# Check API health
curl https://aisalescommander.com/api/v1/health

# Check database connection
docker-compose -f docker-compose.prod.yml exec backend python -c "from app.core.database import engine; print('DB OK')"
```

### **Database Backups:**
```bash
# Automated daily backups
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose -f docker-compose.prod.yml exec -T postgres pg_dump -U aisales_prod aisales_prod > "$BACKUP_DIR/backup_$DATE.sql"
# Keep last 30 days
find $BACKUP_DIR -type f -mtime +30 -delete
```

### **Log Monitoring:**
```bash
# View logs
docker-compose -f docker-compose.prod.yml logs -f --tail=100

# Check specific service
docker-compose -f docker-compose.prod.yml logs backend
```

---

## 🔄 **Step 9: Updates & Rollback**

### **Deploy Updates:**
```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

### **Rollback:**
```bash
# Rollback to previous version
git checkout <previous-commit>
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Rollback database migration
docker-compose -f docker-compose.prod.yml exec backend alembic downgrade -1
```

---

## 📱 **Step 10: SSL Certificate (Let's Encrypt)**

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d aisalescommander.com -d www.aisalescommander.com

# Auto-renewal (runs automatically)
sudo certbot renew --dry-run
```

---

## ✅ **Production Checklist:**

- [ ] Database migrated and backed up
- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Domain DNS configured
- [ ] Services running and healthy
- [ ] Monitoring set up
- [ ] Backups automated
- [ ] Security hardened
- [ ] Load testing completed
- [ ] Documentation updated

---

## 🎉 **Your Production URLs:**

```
Frontend:  https://aisalescommander.com
API:       https://api.aisalescommander.com
Docs:      https://api.aisalescommander.com/docs (disable in production!)
Health:    https://api.aisalescommander.com/health
```

---

## 📞 **Support:**

For issues:
1. Check logs: `docker-compose logs -f`
2. Verify environment variables
3. Check database connectivity
4. Review error handlers
5. Monitor Sentry dashboard

**Your AI Sales Commander is now production-ready!** 🚀✨
