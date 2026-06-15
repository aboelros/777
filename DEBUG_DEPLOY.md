# 🕵️‍♂️ Debugging Deployment

I suspect the deployment might not be updating correctly, or logs are being hidden.
I've added **DEBUG PRINT statements** to the code. These are harder to miss.

## ⏳ What to Do
1.  **Wait for Redeploy** (2-3 mins).
2.  **Check Logs** for these exact lines:
    *   `DEBUG: Loading main.py...`
    *   `DEBUG: Loading groq_client.py...`

## 🔍 Diagnosis
*   **If you see BOTH:** The code is updated and Groq is loading. The key log should be there too.
*   **If you see ONLY main.py:** Groq import is failing silently.
*   **If you see NEITHER:** The deployment is **stuck on old code**.

Let me know what you see!
