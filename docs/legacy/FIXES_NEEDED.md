# Critical Issues & Fixes Needed

## 1. ✅ FIXED: SQLAlchemy Greenlet Errors in Subscriptions
**Problem:** `greenlet_spawn has not been called` errors in subscription endpoints
**Root Cause:** Synchronous code trying to use async database operations
**Status:** Need to verify subscription_service.py uses proper async/await

## 2. ⚠️ PARTIAL: Voice Notes & Images Not Understanding
**Current State:**
- Code exists to download media (lines 776-863 in webhooks.py)
- Uses Gemini for transcription/analysis
- BUT: Missing faster-whisper and Groq Vision integration

**What's Missing:**
- faster-whisper for better voice transcription
- Groq Vision API for image understanding
- Fallback logic if Gemini fails

**Files to Update:**
- `backend/app/services/gemini_client.py` - Add faster-whisper
- `backend/requirements.txt` - Add faster-whisper, groq
- Create `backend/app/services/groq_client.py` - For Groq Vision

## 3. ⚠️ WhatsApp Bot Only Chats with Previous Numbers
**Problem:** Bot doesn't respond to NEW customers, only existing ones
**Root Cause:** Likely in AIOrchestrator or integration lookup logic

**Investigation Needed:**
- Check `app/services/ai_orchestrator.py` 
- Verify customer creation logic (lines 884-894 in webhooks.py looks OK)
- Check if integration is properly linked to project

## 4. ❓ Photo Upload Not Working (No Errors)
**Problem:** Silent failure - no errors but uploads don't work
**Possible Causes:**
- S3/Backblaze credentials not set
- boto3 installed but misconfigured
- Frontend not sending correct format
- CORS issues

**Debug Steps:**
1. Check if boto3 is actually installed after deployment
2. Verify S3_* environment variables are set
3. Add more logging to file_storage.py upload_image
4. Test with curl/Postman to isolate frontend vs backend

## Priority Order:
1. Fix greenlet errors (blocking UI)
2. Add voice/image understanding (user experience)
3. Fix new customer chat issue (critical for growth)
4. Debug photo upload (nice to have)
