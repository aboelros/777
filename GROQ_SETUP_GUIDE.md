# 🛠️ Groq API Troubleshooting

It looks like the Groq API key isn't being used yet. This usually means:
1.  **Key not added to Railway:** Generating it is not enough; it must be in the environment variables.
2.  **Redeploy Pending:** The app needs to restart to pick up the new key.
3.  **Copy-Paste Error:** The key might have spaces around it (I just pushed a fix for this!).

## ✅ Step-by-Step Fix

### 1. Add Key to Railway (Crucial!)
1.  Go to **Railway Dashboard** -> **Backend Service**.
2.  Click **Variables**.
3.  Add:
    *   **Name:** `GROQ_API_KEY`
    *   **Value:** `gsk_...` (your key)
4.  **Wait for Redeploy:** You will see a new deployment start. Wait for "Application startup complete".

### 2. Check Logs
After the app restarts, look at the logs. You should see:
`Groq client initialized successfully with key: gsk_...`

### 3. Test It
Send a **new** voice note or image to the bot.
*   **Voice:** Should verify `Transcribing audio with Groq Whisper...`
*   **Image:** Should verify `Analyzing image with Groq Vision (LLaVA 1.5)...`

**Note:** The "0 API Calls" on Groq dashboard will only update **after** you successfully process a message.
