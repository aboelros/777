# 🔍 DEBUG: Function Calling Investigation

## Date: 2025-12-01 19:01

---

## ❌ ISSUE

The bot is STILL not calling `check_inventory` when users ask for the product catalog, despite multiple prompt updates.

## 🔧 LATEST FIXES

### **1. Explicit Catalog Detection**
**File:** `backend/app/services/ai_orchestrator.py`
- Added keyword detection for catalog requests (English + Arabic).
- When detected, the user prompt now says:
  ```
  ⚠️ CRITICAL INSTRUCTION: The customer is asking for the product catalog/list. 
  You MUST call the `check_inventory` function with query="all" to retrieve the products. 
  DO NOT respond with text only. Call the function first, then present the results to the customer.
  ```

### **2. Enhanced Logging**
**File:** `backend/app/services/gemini_client.py`
- Added logging to show:
  - Tool count and names when initializing the model
  - Which functions (if any) were called in the response

---

## 🧪 HOW TO DEBUG

1. **Restart Backend**
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload
   ```

2. **Send Catalog Request**
   > "القائمة" (The list)
   > "What products do you have?"

3. **Check Logs**
   Look for these log entries:

   **A. Tool Initialization:**
   ```
   Initializing model with tools
   tool_count: 7
   tool_names: ['check_inventory', 'create_order', ...]
   ```
   ✅ If you see this, tools are being passed to the model.

   **B. Response Generation:**
   ```
   Gemini response generated successfully
   has_function_calls: True/False
   function_names: ['check_inventory'] or []
   ```
   ✅ If `has_function_calls: True` and `function_names: ['check_inventory']`, the function WAS called.
   ❌ If `has_function_calls: False`, the model chose NOT to call the function.

---

## 🔍 POSSIBLE ROOT CAUSES

If the logs show `has_function_calls: False`:

1. **Model Preference:** Gemini might be choosing to respond with text instead of calling the function, despite the instructions.
2. **Context Length:** The prompt might be too long, causing the model to skip function calling.
3. **API Version:** The google-generativeai library version might have issues with function calling.

### **Next Steps if Still Failing:**

1. **Try a more direct approach:** Modify the code to FORCE a function call by pre-populating the response with a function call structure.
2. **Check API version:** Verify `google-generativeai` library version.
3. **Test with a simpler prompt:** Remove all context and just send "Call check_inventory with query='all'".

---

**Status:** ⚠️ DEBUGGING - Logs will reveal if the issue is prompt-based or API-based.
