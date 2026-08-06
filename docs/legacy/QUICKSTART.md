# ⚡ Quick Start Guide

Get AI Sales Commander running in under 10 minutes!

## Prerequisites Check

✅ Docker Desktop installed  
✅ 8GB+ RAM available  
✅ Google Cloud account (for AI features)

## Step 1: Clone & Configure (2 minutes)

```bash
cd "C:\Users\ARKAN STOER\Desktop\bot trial 2"

# Copy environment files
copy backend\.env.example backend\.env
copy frontend\.env.example frontend\.env
```

## Step 2: Generate Secret Key (30 seconds)

```bash
cd backend
python scripts/generate_secret_key.py
```

Copy the generated `SECRET_KEY` and paste it into `backend/.env`

## Step 3: Configure Google Cloud (3 minutes)

### Option A: Quick Setup (API Key)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable **Vertex AI API**
3. Create API Key in "APIs & Services" > "Credentials"
4. Add to `backend/.env`:
   ```env
   GOOGLE_CLOUD_PROJECT=your-project-id
   GOOGLE_API_KEY=your-api-key
   ```

### Option B: Production Setup (Service Account)
1. Create Service Account with "Vertex AI User" role
2. Download JSON key to `backend/service-account.json`
3. Add to `backend/.env`:
   ```env
   GOOGLE_CLOUD_PROJECT=your-project-id
   GOOGLE_APPLICATION_CREDENTIALS=/app/service-account.json
   ```

## Step 4: Start Everything (2 minutes)

```bash
# Start all services
docker-compose up -d

# Wait for services to be healthy (30 seconds)
docker-compose ps

# Initialize database
docker-compose exec backend alembic upgrade head

# Create admin user (optional)
docker-compose exec backend python scripts/create_admin.py
```

## Step 5: Access the App (now!)

🌐 **Frontend**: http://localhost:3000  
🔧 **API Docs**: http://localhost:8000/docs  
📊 **Celery Monitor**: http://localhost:5555

## First Login

1. Open http://localhost:3000
2. Click "Create one now"
3. Register with your email
4. Login and create your first project!

## Quick Test

### Test API Health
```bash
curl http://localhost:8000/health
```

### Test AI Assistant
```bash
curl -X POST http://localhost:8000/api/v1/assistant/query \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "YOUR_PROJECT_ID",
    "message": "Hello!",
    "use_function_calling": true
  }'
```

## Troubleshooting

### Services won't start
```bash
docker-compose down -v
docker-compose up -d --build
```

### Database connection error
```bash
docker-compose exec postgres pg_isready
docker-compose restart backend
```

### Frontend won't load
```bash
docker-compose logs frontend
docker-compose restart frontend
```

## Next Steps

✅ Connect an integration (Shopify, WhatsApp, Telegram)  
✅ Import your first orders  
✅ Try the AI Assistant  
✅ Generate your first report  

## Need Help?

- 📚 Full docs: [README.md](./README.md)
- 🔧 Setup guide: [SETUP.md](./SETUP.md)
- 🔒 Security: [SECURITY.md](./SECURITY.md)
- 📖 API docs: [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)

## Pro Tips

🔥 **Use the interactive API docs** at http://localhost:8000/docs to test endpoints

🔥 **Monitor background tasks** at http://localhost:5555 (Flower dashboard)

🔥 **Check logs** with `docker-compose logs -f backend`

🔥 **Hot reload** is enabled for both backend and frontend during development

---

**You're ready to go! 🚀**

Start automating your sales with AI-powered customer communication!
