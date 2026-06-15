# WhatsApp Baileys Gateway - Railway Deployment Guide

## 🚂 Deploy to Railway in 5 Minutes

### Prerequisites
- Railway account (sign up at [railway.app](https://railway.app))
- GitHub account (to connect your repository)

---

## 📦 Option 1: Deploy from GitHub (Recommended)

### Step 1: Push to GitHub

1. Initialize git in the whatsapp-gateway folder:
```bash
cd whatsapp-gateway
git init
git add .
git commit -m "Initial commit - WhatsApp Baileys Gateway"
```

2. Create a new repository on GitHub

3. Push your code:
```bash
git remote add origin https://github.com/YOUR_USERNAME/whatsapp-gateway.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy on Railway

1. Go to [railway.app](https://railway.app) and sign in
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your `whatsapp-gateway` repository
5. Railway will automatically detect it's a Node.js app and deploy it

### Step 3: Configure Environment Variables

In your Railway project dashboard:

1. Go to **Variables** tab
2. Add these environment variables:

```
PORT=3000
API_KEY=your-secure-api-key-change-this
CALLBACK_SECRET=your-callback-secret-change-this
BACKEND_URL=https://your-backend-url.railway.app
SESSION_DIR=/app/sessions
LOG_LEVEL=info
```

**Important:** 
- Change `API_KEY` and `CALLBACK_SECRET` to secure random values
- Set `BACKEND_URL` to your actual backend URL on Railway

### Step 4: Add Volume for Sessions (Important!)

Railway needs persistent storage for WhatsApp sessions:

1. Go to **Settings** tab
2. Scroll to **Volumes**
3. Click **"Add Volume"**
4. Set:
   - **Mount Path**: `/app/sessions`
   - **Size**: 1GB (should be enough)
5. Click **"Add"**

### Step 5: Get Your Gateway URL

1. Go to **Settings** tab
2. Under **Networking**, click **"Generate Domain"**
3. Copy the generated URL (e.g., `https://your-app.railway.app`)

---

## 🔧 Option 2: Deploy with Railway CLI

### Step 1: Install Railway CLI

```bash
npm install -g @railway/cli
```

### Step 2: Login

```bash
railway login
```

### Step 3: Initialize Project

```bash
cd whatsapp-gateway
railway init
```

### Step 4: Deploy

```bash
railway up
```

### Step 5: Set Environment Variables

```bash
railway variables set PORT=3000
railway variables set API_KEY=your-secure-api-key
railway variables set CALLBACK_SECRET=your-callback-secret
railway variables set BACKEND_URL=https://your-backend.railway.app
railway variables set SESSION_DIR=/app/sessions
railway variables set LOG_LEVEL=info
```

### Step 6: Add Volume

```bash
railway volume add /app/sessions
```

---

## 🔗 Connect Backend to Gateway

### Update Backend Environment Variables

In your backend Railway project, add:

```
WHATSAPP_BAILEYS_URL=https://your-gateway.railway.app
WHATSAPP_BAILEYS_API_KEY=your-secure-api-key
WHATSAPP_GATEWAY_CALLBACK_SECRET=your-callback-secret
```

**Make sure the API_KEY matches between gateway and backend!**

---

## ✅ Verify Deployment

### Test Health Endpoint

```bash
curl https://your-gateway.railway.app/health
```

Expected response:
```json
{
  "status": "ok",
  "timestamp": "2024-01-01T00:00:00.000Z",
  "sessions": 0
}
```

### Test Authentication

```bash
curl -H "Authorization: Bearer your-api-key" \
  https://your-gateway.railway.app/sessions
```

Expected response:
```json
{
  "status": "success",
  "sessions": [],
  "count": 0
}
```

---

## 📊 Monitor Your Deployment

### View Logs

**In Railway Dashboard:**
1. Go to your project
2. Click on the **Deployments** tab
3. Click on the latest deployment
4. View real-time logs

**Using CLI:**
```bash
railway logs
```

### Check Metrics

Railway provides:
- CPU usage
- Memory usage
- Network traffic
- Request count

Access these in the **Metrics** tab.

---

## 🔒 Security Best Practices

### 1. Use Strong API Keys

Generate secure random keys:
```bash
# On Linux/Mac
openssl rand -hex 32

# On Windows (PowerShell)
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Maximum 256 }))
```

### 2. Enable HTTPS Only

Railway provides HTTPS by default. Never use HTTP in production.

### 3. Restrict CORS (if needed)

Add to `src/server.js`:
```javascript
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(',') || '*'
}));
```

Then set in Railway:
```
ALLOWED_ORIGINS=https://your-backend.railway.app,https://your-frontend.com
```

---

## 🐛 Troubleshooting

### Sessions Not Persisting

**Problem:** Sessions lost after restart

**Solution:** Ensure volume is mounted at `/app/sessions`
```bash
railway volume list
```

### Out of Memory

**Problem:** App crashes with OOM error

**Solution:** Upgrade Railway plan or optimize session storage

### Can't Connect to Backend

**Problem:** Webhooks not reaching backend

**Solution:** 
1. Verify `BACKEND_URL` is correct
2. Check backend has webhook endpoint
3. Review gateway logs for errors

### Port Already in Use

**Problem:** Railway shows port conflict

**Solution:** Railway automatically sets `PORT` env var. The app uses `process.env.PORT || 3000`, so it should work automatically.

---

## 💰 Pricing Considerations

### Railway Free Tier
- $5 free credit per month
- Good for testing and development
- May need to upgrade for production

### Recommended Plan
- **Hobby Plan**: $5/month
- Includes $5 credit
- Better for production use
- More resources and uptime

### Cost Optimization
- Use 1GB volume (sessions are small)
- Monitor resource usage
- Scale only when needed

---

## 🚀 Production Checklist

- [ ] Volume mounted for session persistence
- [ ] Strong API keys configured
- [ ] Backend URL configured correctly
- [ ] Health endpoint responding
- [ ] Logs showing no errors
- [ ] Test QR code generation
- [ ] Test message sending
- [ ] Webhook delivery working
- [ ] Monitoring set up
- [ ] Backup strategy for sessions

---

## 📝 Quick Reference

### Railway URLs
- Dashboard: https://railway.app/dashboard
- Docs: https://docs.railway.app
- Status: https://status.railway.app

### Important Files
- `railway.json` - Railway configuration
- `nixpacks.toml` - Build configuration
- `package.json` - Dependencies and scripts

### Environment Variables
```
PORT=3000
API_KEY=<secure-random-key>
CALLBACK_SECRET=<secure-random-key>
BACKEND_URL=https://your-backend.railway.app
SESSION_DIR=/app/sessions
LOG_LEVEL=info
```

---

## 🆘 Need Help?

1. **Check Logs**: Most issues show up in logs
2. **Railway Docs**: https://docs.railway.app
3. **Test Locally**: Ensure it works locally first
4. **Health Endpoint**: Always check `/health` first

---

## 🎉 You're All Set!

Your WhatsApp Baileys Gateway is now running on Railway with:
- ✅ Automatic deployments from GitHub
- ✅ Persistent session storage
- ✅ HTTPS enabled
- ✅ Scalable infrastructure
- ✅ Easy monitoring and logs

Now you can connect your WhatsApp and start building your AI sales bot! 🚀
