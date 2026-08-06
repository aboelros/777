# 🏠 Run Locally - Quick Guide

## 🚀 3 Ways to Run Your App

### **Option 1: Docker (Easiest)** ⭐
```cmd
1. Double-click: setup.bat
2. Edit: backend\.env (add GEMINI_API_KEY)
3. Double-click: run.bat
4. Open: http://localhost:3000
```

### **Option 2: Development Mode (Fastest)**
```cmd
1. Double-click: run-dev.bat
2. Backend & Frontend open in separate windows
3. Open: http://localhost:3000
```

### **Option 3: Manual**
```cmd
# Backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# Edit .env with your keys
uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

---

## 📋 Prerequisites

**Install:**
- Docker Desktop (Option 1): https://www.docker.com/products/docker-desktop
- Python 3.11+ (Options 2 & 3): https://www.python.org/downloads/
- Node.js 20+ (Options 2 & 3): https://nodejs.org/

---

## 🔑 Environment Setup

### **backend\.env (REQUIRED):**
```env
SECRET_KEY=generate-40-random-characters
GEMINI_API_KEY=YOUR_GEMINI_KEY_HERE
AUTH_DATABASE_URL=postgresql+asyncpg://postgres:10052008mariem@db.gznafnmgtrgtlxzxxbzy.supabase.co:5432/postgres
APP_DATABASE_URL=postgresql+asyncpg://postgres:10052008mariem@db.vjdbthhdyemeugyhucoq.supabase.co:5432/postgres
REDIS_URL=redis://localhost:6379/0
TESTING_MODE=true
DEBUG=true
```

### **frontend\.env (Optional):**
```env
VITE_API_URL=http://localhost:8000
```

---

## 🎯 Access Your App

```
Frontend: http://localhost:3000
Backend:  http://localhost:8000
API Docs: http://localhost:8000/docs
```

---

## 🧪 Test Backend

```bash
curl http://localhost:8000/health
```

Expected:
```json
{"status":"healthy","database":"connected","redis":"connected"}
```

---

## 🛠️ Common Commands

### Docker:
```cmd
docker-compose up          # Start all services
docker-compose up -d       # Start in background
docker-compose down        # Stop all services
docker-compose logs -f     # View logs
```

### Backend:
```cmd
cd backend
venv\Scripts\activate      # Activate venv
pip install -r requirements.txt
alembic upgrade head       # Run migrations
uvicorn app.main:app --reload
```

### Frontend:
```cmd
cd frontend
npm install
npm run dev
```

---

## 🐛 Troubleshooting

### Docker not running:
- Start Docker Desktop
- Wait for green icon
- Try again

### Port in use:
```cmd
netstat -ano | findstr :8000
taskkill /F /PID <PID>
```

### Database error:
- Check internet (Supabase cloud)
- Verify database URLs in .env

### Module not found:
```cmd
# Backend:
cd backend
pip install -r requirements.txt

# Frontend:
cd frontend
npm install
```

---

## ✅ Quick Start Checklist

- [ ] Docker Desktop running (if using Option 1)
- [ ] Created backend\.env from .env.example
- [ ] Added GEMINI_API_KEY to backend\.env
- [ ] Internet connection active

---

## 🎉 Ready!

**Easiest:** Click `run.bat`  
**Fastest:** Click `run-dev.bat`  
**Manual:** Follow Option 3 above

Open http://localhost:3000 and start building! 🚀
