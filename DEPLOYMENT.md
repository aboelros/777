# 🚀 Production Deployment Guide

Complete guide for deploying AI Sales Commander to production environments.

## Table of Contents
1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Google Cloud Platform Deployment](#google-cloud-platform)
3. [AWS Deployment](#aws-deployment)
4. [Azure Deployment](#azure-deployment)
5. [Self-Hosted Deployment](#self-hosted)
6. [Post-Deployment](#post-deployment)

---

## Pre-Deployment Checklist

### Security
- [ ] Generate strong `SECRET_KEY` (64+ characters)
- [ ] Configure Google Cloud service account
- [ ] Set up SSL/TLS certificates
- [ ] Configure firewall rules
- [ ] Set up secrets manager
- [ ] Enable security headers
- [ ] Configure CORS for production domain
- [ ] Review and update all API keys
- [ ] Set up rate limiting
- [ ] Configure backup strategy

### Environment
- [ ] Set `ENVIRONMENT=production`
- [ ] Set `DEBUG=false`
- [ ] Configure production database
- [ ] Configure production Redis
- [ ] Set up CDN for static assets
- [ ] Configure email service
- [ ] Set up monitoring and alerting
- [ ] Configure log aggregation

### Performance
- [ ] Enable database connection pooling
- [ ] Configure Redis cache TTL
- [ ] Set up load balancer
- [ ] Configure auto-scaling
- [ ] Optimize Docker images
- [ ] Enable compression (gzip)

---

## Google Cloud Platform

### Architecture Overview
```
Cloud Load Balancer
       ↓
Cloud Run (Backend + Frontend)
       ↓
Cloud SQL (PostgreSQL) + Memorystore (Redis)
       ↓
Vertex AI (Gemini)
```

### Step 1: Set Up GCP Project

```bash
# Set project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  redis.googleapis.com \
  aiplatform.googleapis.com \
  secretmanager.googleapis.com
```

### Step 2: Create Cloud SQL Instance

```bash
# Create PostgreSQL instance
gcloud sql instances create aisales-db \
  --database-version=POSTGRES_15 \
  --tier=db-g1-small \
  --region=us-central1 \
  --backup-start-time=03:00

# Create database
gcloud sql databases create aisales --instance=aisales-db

# Create user
gcloud sql users create aisales \
  --instance=aisales-db \
  --password=STRONG_PASSWORD
```

### Step 3: Create Redis Instance

```bash
# Create Memorystore Redis instance
gcloud redis instances create aisales-redis \
  --size=1 \
  --region=us-central1 \
  --redis-version=redis_7_0
```

### Step 4: Set Up Secrets

```bash
# Create secrets
echo -n "your-secret-key" | gcloud secrets create SECRET_KEY --data-file=-
echo -n "your-db-password" | gcloud secrets create DB_PASSWORD --data-file=-

# Grant access to Cloud Run
gcloud secrets add-iam-policy-binding SECRET_KEY \
  --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### Step 5: Build and Push Images

```bash
# Build backend
docker build -t gcr.io/YOUR_PROJECT_ID/aisales-backend:latest \
  --target production ./backend

# Build frontend
docker build -t gcr.io/YOUR_PROJECT_ID/aisales-frontend:latest ./frontend

# Push to Container Registry
docker push gcr.io/YOUR_PROJECT_ID/aisales-backend:latest
docker push gcr.io/YOUR_PROJECT_ID/aisales-frontend:latest
```

### Step 6: Deploy to Cloud Run

```bash
# Deploy backend
gcloud run deploy aisales-backend \
  --image=gcr.io/YOUR_PROJECT_ID/aisales-backend:latest \
  --platform=managed \
  --region=us-central1 \
  --allow-unauthenticated \
  --set-env-vars="ENVIRONMENT=production" \
  --set-secrets="SECRET_KEY=SECRET_KEY:latest,DB_PASSWORD=DB_PASSWORD:latest" \
  --add-cloudsql-instances=YOUR_PROJECT_ID:us-central1:aisales-db \
  --min-instances=1 \
  --max-instances=10 \
  --memory=2Gi

# Deploy frontend
gcloud run deploy aisales-frontend \
  --image=gcr.io/YOUR_PROJECT_ID/aisales-frontend:latest \
  --platform=managed \
  --region=us-central1 \
  --allow-unauthenticated
```

### Step 7: Configure Custom Domain

```bash
# Map domain to Cloud Run service
gcloud run domain-mappings create \
  --service=aisales-frontend \
  --domain=yourdomain.com \
  --region=us-central1
```

### Cost Estimation (Monthly)
- Cloud Run (Backend): $20-100
- Cloud Run (Frontend): $10-30
- Cloud SQL: $25-200
- Memorystore Redis: $40-100
- Vertex AI (Gemini): Variable by usage
- **Total**: $95-430/month (small-medium scale)

---

## AWS Deployment

### Architecture Overview
```
Application Load Balancer
       ↓
ECS Fargate (Backend + Frontend)
       ↓
RDS (PostgreSQL) + ElastiCache (Redis)
       ↓
Bedrock (Claude) or External Gemini API
```

### Step 1: Set Up VPC and Networking

```bash
# Create VPC
aws ec2 create-vpc --cidr-block 10.0.0.0/16

# Create subnets
aws ec2 create-subnet --vpc-id vpc-xxx --cidr-block 10.0.1.0/24
aws ec2 create-subnet --vpc-id vpc-xxx --cidr-block 10.0.2.0/24

# Create security groups
aws ec2 create-security-group \
  --group-name aisales-backend \
  --description "AI Sales Commander Backend"
```

### Step 2: Create RDS PostgreSQL

```bash
aws rds create-db-instance \
  --db-instance-identifier aisales-db \
  --db-instance-class db.t3.small \
  --engine postgres \
  --engine-version 15.4 \
  --master-username aisales \
  --master-user-password STRONG_PASSWORD \
  --allocated-storage 20 \
  --vpc-security-group-ids sg-xxx
```

### Step 3: Create ElastiCache Redis

```bash
aws elasticache create-cache-cluster \
  --cache-cluster-id aisales-redis \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --num-cache-nodes 1
```

### Step 4: Push Images to ECR

```bash
# Create repositories
aws ecr create-repository --repository-name aisales-backend
aws ecr create-repository --repository-name aisales-frontend

# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Build and push
docker build -t aisales-backend --target production ./backend
docker tag aisales-backend YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/aisales-backend:latest
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/aisales-backend:latest
```

### Step 5: Deploy to ECS Fargate

```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name aisales-cluster

# Create task definition (see task-definition.json)
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create service
aws ecs create-service \
  --cluster aisales-cluster \
  --service-name aisales-backend \
  --task-definition aisales-backend:1 \
  --desired-count 2 \
  --launch-type FARGATE
```

### Cost Estimation (Monthly)
- ECS Fargate: $30-150
- RDS: $30-200
- ElastiCache: $15-100
- ALB: $20-50
- NAT Gateway: $30-100
- **Total**: $125-600/month

---

## Azure Deployment

### Architecture Overview
```
Azure Front Door
       ↓
Container Apps (Backend + Frontend)
       ↓
Azure Database for PostgreSQL + Azure Cache for Redis
```

### Step 1: Create Resource Group

```bash
az group create \
  --name aisales-rg \
  --location eastus
```

### Step 2: Create Database

```bash
az postgres flexible-server create \
  --resource-group aisales-rg \
  --name aisales-db \
  --location eastus \
  --admin-user aisales \
  --admin-password STRONG_PASSWORD \
  --sku-name Standard_B1ms \
  --version 15
```

### Step 3: Create Redis Cache

```bash
az redis create \
  --resource-group aisales-rg \
  --name aisales-redis \
  --location eastus \
  --sku Basic \
  --vm-size c0
```

### Step 4: Deploy to Container Apps

```bash
# Create Container Apps environment
az containerapp env create \
  --name aisales-env \
  --resource-group aisales-rg \
  --location eastus

# Deploy backend
az containerapp create \
  --name aisales-backend \
  --resource-group aisales-rg \
  --environment aisales-env \
  --image YOUR_REGISTRY/aisales-backend:latest \
  --target-port 8000 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 10
```

### Cost Estimation (Monthly)
- Container Apps: $30-120
- PostgreSQL: $30-150
- Redis: $20-80
- Front Door: $20-100
- **Total**: $100-450/month

---

## Self-Hosted Deployment

### Requirements
- Ubuntu 22.04 LTS
- 4GB RAM minimum (8GB recommended)
- 2 CPU cores minimum
- 50GB storage
- Docker & Docker Compose installed

### Step 1: Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
  -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Nginx
sudo apt install nginx certbot python3-certbot-nginx -y
```

### Step 2: Configure Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/aisales
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Step 3: SSL Certificate

```bash
# Get SSL certificate from Let's Encrypt
sudo certbot --nginx -d yourdomain.com -d api.yourdomain.com

# Auto-renewal (runs automatically)
sudo certbot renew --dry-run
```

### Step 4: Deploy Application

```bash
# Clone repository
git clone https://github.com/yourusername/ai-sales-commander.git
cd ai-sales-commander

# Configure environment
cp backend/.env.example backend/.env
nano backend/.env  # Edit with production values

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose exec backend alembic upgrade head
```

### Step 5: Set Up Monitoring

```bash
# Install monitoring tools
docker run -d --name=prometheus \
  -p 9090:9090 \
  prom/prometheus

docker run -d --name=grafana \
  -p 3001:3000 \
  grafana/grafana
```

### Cost Estimation (Monthly)
- VPS (DigitalOcean, Linode): $20-50
- Domain: $10-15/year
- SSL: Free (Let's Encrypt)
- **Total**: $20-50/month

---

## Post-Deployment

### 1. Verify Deployment

```bash
# Check health
curl https://api.yourdomain.com/health

# Check version
curl https://api.yourdomain.com/

# Test authentication
curl -X POST https://api.yourdomain.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}'
```

### 2. Set Up Monitoring

**Recommended Tools:**
- **Uptime**: UptimeRobot, Pingdom
- **Performance**: New Relic, Datadog
- **Logs**: Papertrail, Loggly, CloudWatch
- **Errors**: Sentry

### 3. Configure Backups

**Database Backups:**
```bash
# Automated daily backups
0 2 * * * docker-compose exec postgres pg_dump -U aisales aisales > /backups/db-$(date +\%Y\%m\%d).sql
```

**Application Backups:**
- Environment files
- SSL certificates
- Configuration files
- User uploads

### 4. Performance Optimization

- Enable CDN (Cloudflare, Fastly)
- Configure caching headers
- Optimize database queries
- Enable compression
- Set up load balancing

### 5. Security Hardening

```bash
# Update firewall rules
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Fail2ban for SSH protection
sudo apt install fail2ban -y

# Configure automatic security updates
sudo apt install unattended-upgrades -y
```

### 6. Monitoring Checklist

- [ ] Uptime monitoring
- [ ] Error tracking (Sentry)
- [ ] Performance metrics
- [ ] Log aggregation
- [ ] Alert notifications
- [ ] Resource usage tracking
- [ ] Database performance
- [ ] API response times

---

## Rollback Procedure

```bash
# Tag current version
git tag -a v1.0.0 -m "Production release"

# If issues occur, rollback
docker-compose down
git checkout previous-stable-tag
docker-compose up -d

# Restore database if needed
docker-compose exec postgres psql -U aisales aisales < backup.sql
```

---

## Scaling Strategies

### Horizontal Scaling
- Add more backend instances
- Load balance with Nginx/HAProxy
- Scale Celery workers independently
- Use managed database with read replicas

### Vertical Scaling
- Increase container resources
- Upgrade database instance
- Increase Redis memory
- Add more CPU/RAM to workers

### Database Optimization
- Add indexes for frequent queries
- Implement connection pooling
- Use read replicas
- Archive old data
- Optimize slow queries

---

## Support & Troubleshooting

### Common Issues

**Backend won't start:**
```bash
docker-compose logs backend
# Check database connection
# Verify environment variables
```

**High latency:**
```bash
# Check database performance
# Review slow query log
# Verify Redis connection
# Check worker queue size
```

**Memory issues:**
```bash
# Increase Docker memory limits
# Check for memory leaks
# Optimize queries
```

---

**Deployment complete!** 🎉

For issues, check [GitHub Issues](https://github.com/yourusername/ai-sales-commander/issues)
