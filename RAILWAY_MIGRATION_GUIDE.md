# 🚂 Railway Deployment - Database Migration Guide

## 📋 **What You Need to Do**

You've added the `project_code` field to the Project model. Now you need to update your Railway database.

---

## 🎯 **Quick Steps**

### **Option 1: Automatic Migration (Recommended)**

Railway will automatically run migrations on deployment if configured correctly.

**1. Ensure your `start.sh` includes migration:**

Check `backend/start.sh`:
```bash
#!/bin/bash

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Start the application
echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

**2. Push to GitHub:**
```bash
git add .
git commit -m "Add project_code field to projects"
git push origin main
```

**3. Railway will automatically:**
- Pull the new code
- Run `alembic upgrade head`
- Apply the migration
- Restart the app

---

### **Option 2: Manual Migration via Railway CLI**

If automatic migration doesn't work:

**1. Install Railway CLI:**
```bash
npm install -g @railway/cli
```

**2. Login to Railway:**
```bash
railway login
```

**3. Link to your project:**
```bash
cd "C:\Users\ARKAN STOER\Desktop\777\backend"
railway link
```

**4. Run migration:**
```bash
railway run alembic upgrade head
```

---

### **Option 3: Manual Migration via Railway Shell**

**1. Go to Railway Dashboard:**
- Open https://railway.app
- Select your project
- Go to your backend service

**2. Open Shell:**
- Click on "Shell" tab or "Connect" button
- This opens a terminal in your Railway container

**3. Run migration:**
```bash
cd /app
alembic upgrade head
```

**4. Verify:**
```bash
alembic current
```

Should show: `add_project_code (head)`

---

## 🔍 **Verify Migration Worked**

### **Check 1: Database Inspection**

**Via Railway Dashboard:**
1. Go to your PostgreSQL service
2. Click "Data" tab
3. Look at `projects` table
4. Should see `project_code` column

### **Check 2: API Test**

**Create a project with project_code:**
```bash
curl -X POST https://your-railway-app.railway.app/api/v1/projects \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_code": "TEST-001",
    "name": "Test Project"
  }'
```

**If successful:**
```json
{
  "id": "uuid",
  "owner_id": "user-uuid",
  "project_code": "TEST-001",  // ← Should be present
  "name": "Test Project",
  ...
}
```

**If error:**
```json
{
  "detail": "column \"project_code\" does not exist"
}
```
→ Migration didn't run, try manual migration

---

## 🐛 **Troubleshooting**

### **Issue 1: Migration Not Running Automatically**

**Symptom:** Railway deploys but migration doesn't run

**Causes:**
- `start.sh` doesn't have migration command
- `start.sh` not executable
- Migration file has errors

**Fix:**

**1. Check `start.sh` is executable:**
```bash
chmod +x backend/start.sh
git add backend/start.sh
git commit -m "Make start.sh executable"
git push
```

**2. Check Railway logs:**
- Go to Railway Dashboard
- Click on your backend service
- Check "Deployments" → Latest deployment → "View Logs"
- Look for "Running database migrations..."

**3. If not found, add to `start.sh`:**
```bash
#!/bin/bash
set -e  # Exit on error

echo "🔄 Running database migrations..."
alembic upgrade head

echo "🚀 Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

---

### **Issue 2: Migration File Not Found**

**Symptom:** `alembic upgrade head` says "No such file"

**Cause:** Migration file not committed to git

**Fix:**
```bash
git add backend/alembic/versions/add_project_code.py
git commit -m "Add project_code migration"
git push
```

---

### **Issue 3: Existing Projects Without project_code**

**Symptom:** Migration fails because existing projects don't have `project_code`

**Cause:** The migration should handle this automatically

**What the migration does:**
1. Adds `project_code` column (nullable first)
2. Generates codes for existing projects (`PROJ-001`, `PROJ-002`, etc.)
3. Makes column non-nullable
4. Adds unique constraint

**If it fails:**
Run this SQL manually in Railway PostgreSQL:

```sql
-- Add column (nullable)
ALTER TABLE projects ADD COLUMN project_code VARCHAR(50);

-- Generate codes for existing projects
WITH numbered_projects AS (
    SELECT id, ROW_NUMBER() OVER (ORDER BY created_at) as row_num
    FROM projects
)
UPDATE projects
SET project_code = 'PROJ-' || LPAD(numbered_projects.row_num::text, 3, '0')
FROM numbered_projects
WHERE projects.id = numbered_projects.id;

-- Make non-nullable and add constraints
ALTER TABLE projects ALTER COLUMN project_code SET NOT NULL;
ALTER TABLE projects ADD CONSTRAINT uq_projects_project_code UNIQUE (project_code);
CREATE INDEX ix_projects_project_code ON projects(project_code);
```

---

### **Issue 4: Duplicate project_code Error**

**Symptom:** Can't create project - "project_code already exists"

**Cause:** Auto-generated codes might conflict

**Fix:** Use a different code format:
```json
{
  "project_code": "MYSTORE-001",  // Instead of PROJ-001
  "name": "My Store"
}
```

---

## 📝 **Migration File Details**

**Location:** `backend/alembic/versions/add_project_code.py`

**What it does:**
1. ✅ Adds `project_code VARCHAR(50)` column
2. ✅ Auto-generates codes for existing projects
3. ✅ Makes column required (NOT NULL)
4. ✅ Adds unique constraint
5. ✅ Creates index for fast lookups

**Rollback (if needed):**
```bash
railway run alembic downgrade -1
```

---

## 🚀 **Deployment Checklist**

- [ ] Migration file created: `backend/alembic/versions/add_project_code.py`
- [ ] Migration file committed to git
- [ ] `start.sh` includes `alembic upgrade head`
- [ ] `start.sh` is executable (`chmod +x`)
- [ ] Code pushed to GitHub
- [ ] Railway deployment triggered
- [ ] Check Railway logs for "Running database migrations..."
- [ ] Check Railway logs for "alembic upgrade head" success
- [ ] Test creating project with `project_code`
- [ ] Verify existing projects have auto-generated codes

---

## 🎯 **Expected Railway Deployment Flow**

```
1. Push to GitHub
   ↓
2. Railway detects changes
   ↓
3. Railway builds new image
   ↓
4. Railway runs start.sh
   ↓
5. start.sh runs: alembic upgrade head
   ↓
6. Migration adds project_code column
   ↓
7. Migration generates codes for existing projects
   ↓
8. start.sh runs: uvicorn app.main:app
   ↓
9. Application starts with new schema
   ✅ DONE!
```

---

## 🔧 **Railway Environment Variables**

Make sure these are set in Railway:

```bash
# Database (should be auto-set by Railway PostgreSQL)
DATABASE_URL=postgresql://...

# Required for migrations
PYTHONUNBUFFERED=1
```

---

## 📊 **Check Migration Status**

**Via Railway CLI:**
```bash
railway run alembic current
```

**Expected output:**
```
add_project_code (head)
```

**Via Railway Shell:**
```bash
# Connect to Railway shell
# Then run:
cd /app
alembic current
```

---

## ✅ **Success Indicators**

### **1. Railway Logs Show:**
```
🔄 Running database migrations...
INFO  [alembic.runtime.migration] Running upgrade -> add_project_code
🚀 Starting application...
INFO:     Started server process
```

### **2. API Works:**
```bash
# Create project with code
curl -X POST https://your-app.railway.app/api/v1/projects \
  -H "Authorization: Bearer TOKEN" \
  -d '{"project_code": "TEST-001", "name": "Test"}'

# Response includes project_code
{
  "project_code": "TEST-001",
  ...
}
```

### **3. Existing Projects Have Codes:**
```bash
# List projects
curl https://your-app.railway.app/api/v1/projects \
  -H "Authorization: Bearer TOKEN"

# Response shows auto-generated codes
[
  {
    "project_code": "PROJ-001",  // ← Auto-generated
    "name": "Old Project 1",
    ...
  },
  {
    "project_code": "PROJ-002",  // ← Auto-generated
    "name": "Old Project 2",
    ...
  }
]
```

---

## 🆘 **If Something Goes Wrong**

### **Rollback Migration:**
```bash
railway run alembic downgrade -1
```

### **Check Database Directly:**
```bash
railway run psql $DATABASE_URL -c "\d projects"
```

Should show `project_code` column.

### **Force Re-run Migration:**
```bash
# Downgrade
railway run alembic downgrade -1

# Upgrade again
railway run alembic upgrade head
```

---

## 📞 **Quick Reference**

**Deploy with migration:**
```bash
git add .
git commit -m "Add project_code field"
git push origin main
# Railway auto-deploys and runs migration
```

**Manual migration:**
```bash
railway run alembic upgrade head
```

**Check status:**
```bash
railway run alembic current
```

**Rollback:**
```bash
railway run alembic downgrade -1
```

---

## 🎉 **Summary**

1. **Push code to GitHub** → Railway auto-deploys
2. **Migration runs automatically** (if `start.sh` configured)
3. **Existing projects get codes** (`PROJ-001`, `PROJ-002`, etc.)
4. **New projects require `project_code`** field
5. **All projects now have unique codes** ✅

---

**Your Railway deployment will handle this automatically!** Just push to GitHub and Railway does the rest. 🚂
