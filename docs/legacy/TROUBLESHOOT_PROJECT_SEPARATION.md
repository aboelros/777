# 🔍 Troubleshooting: "All Users See All Projects" Issue

## 🔴 **Problem Description**

When you create a new project, it shows up for ALL users instead of just the user who created it.

---

## 🎯 **Expected Behavior**

- ✅ User A creates Project X → Only User A can see Project X
- ✅ User B creates Project Y → Only User B can see Project Y
- ❌ User A should NOT see Project Y
- ❌ User B should NOT see Project X

---

## 🔍 **Diagnosis**

### **Step 1: Run the Diagnostic Script**

```bash
cd "C:\Users\ARKAN STOER\Desktop\777"
python test_project_separation.py
```

This will test if the **backend** is working correctly.

**If all tests pass** → The backend is fine, issue is in **frontend**  
**If tests fail** → The backend has a bug

---

## 🐛 **Possible Causes**

### **Cause 1: Frontend Not Sending JWT Token** ⚠️ **MOST LIKELY**

**Symptom:** All users see all projects

**Why:** If the JWT token is not being sent, the backend can't identify which user is making the request, so it might return all projects or fail.

**Check:**
1. Open browser DevTools (F12)
2. Go to Network tab
3. Make a request to `/api/v1/projects`
4. Check the request headers
5. Look for `Authorization: Bearer <token>`

**If missing:**
- Frontend is not sending the token
- User might not be logged in
- Token might be expired

**Fix:** See "Frontend Fixes" below

---

### **Cause 2: Backend Not Filtering by User** ❌ **UNLIKELY**

**Symptom:** Backend returns all projects regardless of user

**Why:** The `list_projects` endpoint is not filtering by `owner_id`

**Check:** Run the diagnostic script (see Step 1)

**Fix:** The code is already correct (line 88-92 in projects.py):
```python
result = await db.execute(
    select(Project)
    .where(Project.owner_id == UUID(user_id))  # ← Filtering by user
    .order_by(Project.created_at.desc())
)
```

---

### **Cause 3: Frontend Using Wrong API Endpoint** ❌ **UNLIKELY**

**Symptom:** Frontend calling an admin endpoint that returns all projects

**Check:** Look at the frontend code making the API call

**Fix:** Ensure it's calling `/api/v1/projects` (not `/api/v1/admin/projects` or similar)

---

### **Cause 4: Multiple Users Logged In Same Browser** ⚠️ **POSSIBLE**

**Symptom:** Switching between users in the same browser shows mixed data

**Why:** Browser cache or localStorage confusion

**Fix:** 
1. Clear browser cache and localStorage
2. Use incognito/private windows for different users
3. Use different browsers for different users

---

## 🛠️ **Frontend Fixes**

### **Fix 1: Ensure JWT Token is Sent**

Check `frontend/src/lib/api.js` (lines 14-25):

```javascript
// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;  // ← This must work
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);
```

**Verify:**
1. Open browser console
2. Type: `localStorage.getItem('access_token')`
3. Should return a JWT token (long string)
4. If `null` → User is not logged in

---

### **Fix 2: Check Login Flow**

Ensure login is working correctly:

```javascript
// After successful login
const response = await auth.login({ email, password });
const { access_token, refresh_token } = response.data;

// These must be saved
localStorage.setItem('access_token', access_token);
localStorage.setItem('refresh_token', refresh_token);
```

---

### **Fix 3: Add Logging to Debug**

Add console.log to see what's happening:

```javascript
// In frontend/src/lib/api.js
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    console.log('🔑 Token:', token ? 'Present' : 'Missing');  // ← Add this
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  }
);
```

Then check browser console when loading projects.

---

### **Fix 4: Verify API Response**

Add logging to see what the API returns:

```javascript
// When fetching projects
const response = await projects.list();
console.log('📦 Projects received:', response.data);
console.log('📊 Number of projects:', response.data.length);
```

---

## 🔧 **Backend Verification**

### **Check 1: Verify Endpoint is Filtering**

Look at `backend/app/api/v1/projects.py` line 80-95:

```python
@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    user_id: str = Depends(get_current_user_id),  # ← Gets user from JWT
    db: AsyncSession = Depends(get_db)
) -> Any:
    """List all projects owned by the current user."""
    result = await db.execute(
        select(Project)
        .where(Project.owner_id == UUID(user_id))  # ← FILTERS by user
        .order_by(Project.created_at.desc())
    )
    projects = result.scalars().all()
    return projects
```

**This is correct!** ✅

---

### **Check 2: Verify JWT Extraction**

Check `backend/app/core/security.py` - the `get_current_user_id` function:

```python
async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> str:
    """Extract user ID from JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

---

### **Check 3: Add Backend Logging**

Add logging to see what's happening:

```python
@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """List all projects owned by the current user."""
    
    # Add this logging
    logger.info(f"🔍 Listing projects for user: {user_id}")
    
    result = await db.execute(
        select(Project)
        .where(Project.owner_id == UUID(user_id))
        .order_by(Project.created_at.desc())
    )
    projects = result.scalars().all()
    
    # Add this logging
    logger.info(f"📦 Found {len(projects)} projects for user {user_id}")
    
    return projects
```

Then check backend logs when loading projects.

---

## 🧪 **Testing Steps**

### **Test 1: Create Two Users**

1. Register User A: `usera@test.com`
2. Register User B: `userb@test.com`

### **Test 2: Create Projects**

1. Login as User A
2. Create "Project A"
3. Logout
4. Login as User B
5. Create "Project B"

### **Test 3: Verify Separation**

1. Login as User A
2. Go to Projects page
3. **Should see:** Only "Project A"
4. **Should NOT see:** "Project B"

5. Logout
6. Login as User B
7. Go to Projects page
8. **Should see:** Only "Project B"
9. **Should NOT see:** "Project A"

---

## 📊 **Quick Diagnostic Checklist**

- [ ] Run `python test_project_separation.py` - Does it pass?
- [ ] Open browser DevTools → Network tab
- [ ] Load projects page
- [ ] Check request to `/api/v1/projects`
- [ ] Is `Authorization: Bearer <token>` header present?
- [ ] Check response - How many projects returned?
- [ ] Check browser console - Any errors?
- [ ] Check backend logs - What user_id is being used?
- [ ] Try in incognito window - Same issue?
- [ ] Try different browser - Same issue?

---

## 🎯 **Most Likely Solution**

Based on the symptoms, the issue is **most likely**:

### **JWT Token Not Being Sent**

**Symptoms:**
- All users see all projects
- Backend can't identify the user
- Might return all projects or error

**Solution:**
1. Check if user is actually logged in
2. Verify JWT token is in localStorage
3. Verify token is being sent in requests
4. Check token hasn't expired
5. Try logging out and logging in again

**Quick Fix:**
```javascript
// In browser console
localStorage.clear();  // Clear everything
// Then login again
```

---

## 📝 **Summary**

**Backend:** ✅ Already correctly filters by user  
**Frontend:** ⚠️ Likely not sending JWT token correctly  

**Next Steps:**
1. Run diagnostic script: `python test_project_separation.py`
2. Check browser DevTools Network tab
3. Verify JWT token is being sent
4. Check backend logs for user_id
5. Try clearing cache and logging in again

---

## 🆘 **Still Having Issues?**

If the problem persists:

1. **Capture Screenshots:**
   - Browser DevTools Network tab showing the request
   - Backend logs showing the user_id
   - Frontend showing all projects

2. **Check:**
   - Are you using the same email for multiple accounts?
   - Are you testing in the same browser session?
   - Did you clear cache between tests?

3. **Try:**
   - Use incognito/private window
   - Use different browsers for different users
   - Clear all browser data and start fresh

---

**The backend is already secure and working correctly!** The issue is likely in how the frontend is handling authentication. 🔒
