# Railway Deployment - Quick Start

## 🚀 Deploy in 3 Steps

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "WhatsApp Baileys Gateway"
git remote add origin https://github.com/YOUR_USERNAME/whatsapp-gateway.git
git push -u origin main
```

### 2. Deploy on Railway
1. Go to [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway will auto-deploy

### 3. Configure
Add these environment variables in Railway:
```
API_KEY=your-secure-random-key
CALLBACK_SECRET=your-callback-secret
BACKEND_URL=https://your-backend.railway.app
SESSION_DIR=/app/sessions
```

**Important:** Add a Volume at `/app/sessions` (1GB) for session persistence!

### 4. Get Your URL
Railway will generate a URL like: `https://your-app.railway.app`

## Update Backend
Add to your backend environment:
```
WHATSAPP_BAILEYS_URL=https://your-gateway.railway.app
WHATSAPP_BAILEYS_API_KEY=your-secure-random-key
```

## Test
```bash
curl https://your-gateway.railway.app/health
```

📖 **Full guide:** See [RAILWAY.md](RAILWAY.md) for detailed instructions
