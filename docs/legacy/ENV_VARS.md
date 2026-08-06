# Environment Variables - Quick Reference

## 🔴 REQUIRED (System won't work without these)

```bash
# Database
DATABASE_URL=postgresql://...

# Gemini AI
GEMINI_API_KEY=your_gemini_key

# JWT Security
SECRET_KEY=your_secret_key_here
```

## 🟡 CRITICAL FOR FEATURES (Needed for specific functionality)

```bash
# Backblaze B2 Storage (for product images)
S3_BUCKET_NAME=trialfrr
S3_REGION=us-east-005
S3_ENDPOINT_URL=https://s3.us-east-005.backblazeb2.com
S3_ACCESS_KEY=your_backblaze_keyID
S3_SECRET_KEY=your_backblaze_applicationKey

# WhatsApp Gateway (configured per integration in DB)
# Note: These are now stored in integration.config, not env vars
# But you can set defaults:
WA_GATEWAY_BASE_URL=https://your-wa-gateway.com
WA_GATEWAY_API_KEY=optional_api_key
```

## 🟢 OPTIONAL (Enhances functionality)

```bash
# Groq AI (fallback for voice/image if Gemini fails)
GROQ_API_KEY=your_groq_api_key

# Sentry Error Tracking
SENTRY_DSN=your_sentry_dsn

# Redis (for caching - optional)
REDIS_URL=redis://...
```

## 📋 How to Set in Railway

1. Go to your Railway project
2. Click on your service
3. Go to "Variables" tab
4. Click "New Variable"
5. Add each variable one by one

## 🔍 How to Verify

After deployment, check logs for:
- ✅ `Gemini API configured` - Gemini working
- ✅ `Groq client initialized` - Groq working (if set)
- ✅ `S3StorageService initialized` - Backblaze working
- ⚠️ `boto3 not installed` - Requirements issue
- ⚠️ `No GROQ_API_KEY found` - Groq disabled (OK, it's optional)

## 🎯 Priority Order

1. **Deploy First:** DATABASE_URL, GEMINI_API_KEY, SECRET_KEY
2. **Add Next:** S3_* variables (for image uploads)
3. **Add Later:** GROQ_API_KEY (for better media processing)
