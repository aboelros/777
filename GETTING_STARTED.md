# 🎯 Getting Started with AI Sales Commander

Welcome! This guide will help you go from zero to running application in the simplest way possible.

## What You'll Build

A complete AI-powered sales automation platform with:
- 🤖 Google Gemini AI assistant
- 🛍️ E-commerce integration (Shopify)
- 💬 Multi-channel messaging (WhatsApp, Telegram)
- 📊 Real-time analytics dashboard
- 🎨 Beautiful dark glass-morphism UI

## Prerequisites (5 minutes to install)

### Required:
1. **Docker Desktop** - [Download here](https://www.docker.com/products/docker-desktop)
2. **Google Cloud Account** - [Sign up free](https://cloud.google.com/free)

### Optional (for local development):
3. Node.js 20+ - [Download](https://nodejs.org/)
4. Python 3.11+ - [Download](https://www.python.org/)

---

## Quick Start (10 Minutes)

### Step 1: Get the Code (1 min)

```bash
# You already have it at:
cd "C:\Users\ARKAN STOER\Desktop\bot trial 2"
```

### Step 2: Set Up Environment (2 min)

```bash
# Copy environment templates
copy backend\.env.example backend\.env
copy frontend\.env.example frontend\.env

# Generate a secure secret key
cd backend
python scripts\generate_secret_key.py
```

Copy the generated `SECRET_KEY` and paste it into `backend\.env`:
```env
SECRET_KEY=your-generated-key-here
```

### Step 3: Configure Google Cloud (4 min)

#### Quick Setup for Development:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable **Vertex AI API**:
   - Search "Vertex AI API" in search bar
   - Click "Enable"
4. Create API Key:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "API Key"
   - Copy the key

5. Edit `backend\.env` and add:
```env
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_API_KEY=your-api-key-here
```

### Step 4: Start Everything (3 min)

```bash
# Start all services
docker-compose up -d

# Wait 30 seconds for services to start...

# Check services are running
docker-compose ps

# Initialize database
docker-compose exec backend alembic upgrade head
```

### Step 5: Open the App! (now)

🌐 **Open your browser**: http://localhost:3000

You should see the beautiful login page!

---

## First Time Setup

### Create Your Account

1. Click **"Create one now"** on the login page
2. Enter your email and password
3. Click **Sign Up**
4. You're in! 🎉

### Create Your First Project

1. After login, you'll see the dashboard
2. Click your profile → **Create Project**
3. Enter project name (e.g., "My Store")
4. Click **Create**

### Connect an Integration (Optional)

1. Go to **Integrations** in the sidebar
2. Click **Connect** on any platform
3. Enter credentials (or skip for now)

### Try the AI Assistant

1. Click **AI Assistant** in sidebar
2. Type: "Hello, what can you do?"
3. Watch the AI respond! 🤖

---

## What's Running?

When you run `docker-compose up -d`, these services start:

| Service | Port | What It Does |
|---------|------|--------------|
| **Frontend** | 3000 | React UI you interact with |
| **Backend** | 8000 | FastAPI server (API) |
| **PostgreSQL** | 5432 | Database |
| **Redis** | 6379 | Cache & message queue |
| **Celery Worker** | - | Background tasks |
| **Flower** | 5555 | Task monitor |

### Access Points:

- 🌐 **Main App**: http://localhost:3000
- 🔧 **API Docs**: http://localhost:8000/docs
- 📊 **Task Monitor**: http://localhost:5555

---

## Common First Steps

### 1. Explore the Dashboard
- View sales metrics
- See recent activity
- Check quick actions

### 2. Connect Shopify (If you have a store)
- Go to **Integrations**
- Click **Connect** on Shopify
- Enter your store credentials
- Orders will sync automatically

### 3. Test AI Features
- Go to **AI Assistant**
- Ask questions about orders
- Try: "Generate a follow-up message for order #1234"

### 4. Generate a Report
- Go to **Reports**
- Click **Generate Report**
- Select date range
- View analytics

---

## Troubleshooting

### Services Won't Start

```bash
# Check if ports are in use
netstat -ano | findstr "3000"
netstat -ano | findstr "8000"

# Restart everything
docker-compose down
docker-compose up -d
```

### Can't Access Frontend

```bash
# Check frontend logs
docker-compose logs frontend

# Rebuild if needed
docker-compose up -d --build frontend
```

### Database Connection Error

```bash
# Check PostgreSQL
docker-compose exec postgres pg_isready

# Restart backend
docker-compose restart backend
```

### "Module not found" errors

```bash
# Rebuild containers
docker-compose down
docker-compose up -d --build
```

---

## Learning Path

### Week 1: Getting Comfortable
- [ ] Set up and run the application
- [ ] Create your account and project
- [ ] Explore all pages in the UI
- [ ] Try the AI Assistant
- [ ] Read the README.md

### Week 2: Integration
- [ ] Connect your first integration
- [ ] Sync some orders
- [ ] Send test messages
- [ ] Generate reports
- [ ] Read API_DOCUMENTATION.md

### Week 3: Customization
- [ ] Customize UI colors (tailwind.config.js)
- [ ] Add custom dashboard widgets
- [ ] Create automation rules
- [ ] Read SECURITY.md

### Week 4: Production
- [ ] Set up production environment
- [ ] Configure custom domain
- [ ] Set up monitoring
- [ ] Deploy to cloud
- [ ] Read DEPLOYMENT.md

---

## Next Steps

📚 **Learn More:**
- [README.md](./README.md) - Full feature list
- [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) - API reference
- [SETUP.md](./SETUP.md) - Detailed setup

🔧 **Customize:**
- Edit `frontend/tailwind.config.js` for colors
- Modify `backend/app/core/config.py` for settings
- Add new pages in `frontend/src/pages/`

🚀 **Deploy:**
- [DEPLOYMENT.md](./DEPLOYMENT.md) - Production guide
- [SECURITY.md](./SECURITY.md) - Security best practices

💬 **Get Help:**
- Check documentation files
- Review code comments
- Open GitHub Issues

---

## Quick Commands Cheat Sheet

```bash
# Start everything
docker-compose up -d

# Stop everything
docker-compose down

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend

# Restart a service
docker-compose restart backend

# Rebuild and restart
docker-compose up -d --build backend

# Create admin user
docker-compose exec backend python scripts/create_admin.py

# Access database
docker-compose exec postgres psql -U aisales -d aisales

# Run migrations
docker-compose exec backend alembic upgrade head

# Check service status
docker-compose ps

# Remove everything (including data)
docker-compose down -v
```

---

## Tips for Success

💡 **Start Small**: Don't try to use all features at once. Start with dashboard and AI assistant.

💡 **Use API Docs**: The interactive docs at http://localhost:8000/docs let you test endpoints easily.

💡 **Check Logs**: When something doesn't work, check logs with `docker-compose logs [service]`

💡 **Read Comments**: The code has helpful comments explaining complex logic.

💡 **Experiment**: It's running locally - you can't break anything! Try things out.

💡 **Ask Questions**: Open GitHub Issues if you need help.

---

## Development Mode

Want to modify the code and see changes instantly?

### Backend Changes (Hot Reload Enabled)
```bash
# Just edit files in backend/app/
# FastAPI will auto-reload
```

### Frontend Changes (Hot Reload Enabled)
```bash
# Edit files in frontend/src/
# Vite will auto-reload in browser
```

### Database Changes
```bash
# 1. Edit backend/app/db/models.py
# 2. Create migration
docker-compose exec backend alembic revision --autogenerate -m "description"
# 3. Apply migration
docker-compose exec backend alembic upgrade head
```

---

## What Makes This Special?

✨ **Latest Tech**: Using newest versions of everything  
✨ **Beautiful UI**: Custom dark glass-morphism design  
✨ **AI-Powered**: Real Google Gemini integration  
✨ **Production-Ready**: Not a demo, actual deployable code  
✨ **Well-Documented**: 10+ documentation files  
✨ **Secure**: JWT auth, rate limiting, input validation  
✨ **Scalable**: Microservices pattern, background workers  

---

## Need Help?

1. **Read the docs** - Most questions are answered in documentation
2. **Check examples** - Code has working examples
3. **View logs** - Errors show up in service logs
4. **Ask for help** - Open a GitHub Issue

---

## You're Ready! 🚀

You now have a complete AI-powered sales platform running locally!

**What to do next?**
1. Explore the UI
2. Try the AI Assistant
3. Connect an integration
4. Read more documentation

**Ready to deploy?**
See [DEPLOYMENT.md](./DEPLOYMENT.md)

**Want to contribute?**
See [CONTRIBUTING.md](./CONTRIBUTING.md)

---

**Happy coding!** 💻✨

Built with ❤️ using cutting-edge technology
