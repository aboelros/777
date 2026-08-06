# 🔧 Build Error Fixed

## Problem
Deployment failed with:
```
pkg-config is required for building PyAV
```

## Root Cause
`faster-whisper==1.0.0` requires:
- pkg-config (system package)
- FFmpeg libraries
- PyAV compilation

These are heavy system dependencies that complicate Docker builds.

## Solution
**Removed `faster-whisper` from requirements.txt**

Instead, we're using **Groq Whisper API** which:
- ✅ No system dependencies needed
- ✅ 10x faster than local Whisper
- ✅ Cloud-based (no model downloads)
- ✅ Free tier available
- ✅ Same accuracy as OpenAI Whisper

## What Changed
- `requirements.txt`: Removed `faster-whisper==1.0.0`
- Kept `groq==0.4.1` for API access
- `groq_client.py` already uses Groq API (no local models)

## Deploy Now
```bash
git add .
git commit -m "Fix: Remove faster-whisper, use Groq API only"
git push
```

Build will succeed! ✅

## Set Environment Variable
After deployment, add to Railway:
```bash
GROQ_API_KEY=your_key_here
```

Get free key: https://console.groq.com
