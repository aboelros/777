# 🆔 Project Code Feature - Implementation Guide

## 📋 **What Was Added**

A new **`project_code`** field has been added to the Project model to provide a **unique, human-readable identifier** for each project, making it easier to differentiate projects from each other.

---

## ✨ **Feature Overview**

### **What is project_code?**
- A **unique identifier** for each project (e.g., `PROJ-001`, `STORE-ABC`, `MYBRAND`)
- **Human-readable** and easy to remember
- **Required** for all new projects
- **Indexed** for fast lookups
- **Unique across all projects** (not just per user)

### **Why is this useful?**
- ✅ Easy to identify projects in logs and reports
- ✅ Share project references with team members
- ✅ Use in URLs or external systems
- ✅ Organize projects with meaningful codes
- ✅ Quick project lookup by code

---

## 🔧 **Technical Changes**

### **1. Database Schema**

**Added to `projects` table:**
```sql
project_code VARCHAR(50) UNIQUE NOT NULL INDEX
```

**Example:**
```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY,
    owner_id UUID NOT NULL,
    project_code VARCHAR(50) UNIQUE NOT NULL,  -- ← NEW
    name VARCHAR(255) NOT NULL,
    description TEXT,
    ...
);

CREATE INDEX ix_projects_project_code ON projects(project_code);
```

---

### **2. API Changes**

#### **Create Project (POST /api/v1/projects)**

**Before:**
```json
{
  "name": "My Store",
  "description": "E-commerce store",
  "timezone": "UTC"
}
```

**After:**
```json
{
  "project_code": "MYSTORE-001",  // ← NEW (required)
  "name": "My Store",
  "description": "E-commerce store",
  "timezone": "UTC"
}
```

**Validation:**
- ✅ Must be 3-50 characters
- ✅ Must be unique across all projects
- ✅ Returns 400 error if code already exists

---

#### **Update Project (PATCH /api/v1/projects/{id})**

**Can now update project_code:**
```json
{
  "project_code": "NEWCODE-123"  // ← Optional
}
```

**Validation:**
- ✅ Must be unique (if changing)
- ✅ Returns 400 error if new code already exists

---

#### **Project Response**

**All project responses now include project_code:**
```json
{
  "id": "uuid-here",
  "owner_id": "user-uuid",
  "project_code": "MYSTORE-001",  // ← NEW
  "name": "My Store",
  "description": "E-commerce store",
  "timezone": "UTC",
  "is_active": true,
  "created_at": "2025-11-28T...",
  "updated_at": "2025-11-28T..."
}
```

---

## 📝 **Usage Examples**

### **Example 1: Create Project with Code**

```bash
curl -X POST https://api.example.com/api/v1/projects \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_code": "TECHSTORE-001",
    "name": "Tech Store",
    "description": "Electronics e-commerce"
  }'
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "owner_id": "user-uuid",
  "project_code": "TECHSTORE-001",
  "name": "Tech Store",
  "description": "Electronics e-commerce",
  "timezone": "UTC",
  "settings": {},
  "is_active": true,
  "created_at": "2025-11-28T16:00:00Z",
  "updated_at": null
}
```

---

### **Example 2: Try Duplicate Code (Error)**

```bash
curl -X POST https://api.example.com/api/v1/projects \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_code": "TECHSTORE-001",
    "name": "Another Store"
  }'
```

**Response (400 Bad Request):**
```json
{
  "detail": "Project code 'TECHSTORE-001' already exists. Please choose a different code."
}
```

---

### **Example 3: Update Project Code**

```bash
curl -X PATCH https://api.example.com/api/v1/projects/{project_id} \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_code": "TECHSTORE-002"
  }'
```

---

## 🗂️ **Project Code Naming Conventions**

### **Recommended Formats:**

1. **Sequential Numbers:**
   - `PROJ-001`, `PROJ-002`, `PROJ-003`
   - Good for: Simple numbering

2. **Business Name + Number:**
   - `TECHSTORE-001`, `FASHIONBRAND-001`
   - Good for: Multiple businesses

3. **Category + Number:**
   - `ECOM-001`, `SAAS-001`, `RETAIL-001`
   - Good for: Organizing by type

4. **Short Codes:**
   - `TS01`, `FB01`, `RT01`
   - Good for: Compact identifiers

5. **Custom Codes:**
   - `MYBRAND`, `CLIENTA`, `PROJECTX`
   - Good for: Meaningful names

### **Best Practices:**
- ✅ Use uppercase for consistency
- ✅ Use hyphens or underscores for readability
- ✅ Keep it short (3-20 characters ideal)
- ✅ Make it memorable
- ✅ Use consistent format across projects
- ❌ Avoid special characters (except `-` and `_`)
- ❌ Avoid spaces

---

## 🔄 **Migration Guide**

### **For Existing Projects**

If you have existing projects without `project_code`, run the migration:

```bash
cd backend
alembic upgrade head
```

**What happens:**
1. Adds `project_code` column to `projects` table
2. **Automatically generates codes** for existing projects:
   - Format: `PROJ-001`, `PROJ-002`, `PROJ-003`, etc.
   - Based on creation order
3. Makes column non-nullable
4. Adds unique constraint and index

**Example:**
```
Existing Project 1 (created first)  → project_code = "PROJ-001"
Existing Project 2 (created second) → project_code = "PROJ-002"
Existing Project 3 (created third)  → project_code = "PROJ-003"
```

### **After Migration**

You can update the auto-generated codes to meaningful ones:

```bash
# Update project code
curl -X PATCH https://api.example.com/api/v1/projects/{project_id} \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_code": "MYSTORE-MAIN"
  }'
```

---

## 🎯 **Use Cases**

### **1. Logging and Debugging**
```python
logger.info(
    "Processing order",
    project_code=project.project_code,  # ← Easy to identify
    order_id=order.id
)
```

**Log Output:**
```
Processing order project_code=TECHSTORE-001 order_id=uuid-here
```

---

### **2. Team Communication**
```
"Hey, can you check project TECHSTORE-001? 
 The WhatsApp integration isn't working."
```

Much easier than:
```
"Hey, can you check project 550e8400-e29b-41d4-a716-446655440000?"
```

---

### **3. External Integrations**
```python
# Use project_code in webhook URLs
webhook_url = f"https://api.example.com/webhooks/{project.project_code}"

# Use in file names
report_file = f"report_{project.project_code}_{date}.pdf"

# Use in API keys
api_key = f"{project.project_code}_{random_string}"
```

---

### **4. Database Queries**
```python
# Find project by code (faster than searching by name)
project = await db.execute(
    select(Project).where(Project.project_code == "TECHSTORE-001")
)
```

---

## 📊 **Frontend Integration**

### **Display Project Code**

```jsx
// In project list
<div className="project-card">
  <div className="project-code">{project.project_code}</div>
  <h3>{project.name}</h3>
  <p>{project.description}</p>
</div>
```

### **Create Project Form**

```jsx
<form onSubmit={handleCreateProject}>
  <input
    type="text"
    name="project_code"
    placeholder="Project Code (e.g., MYSTORE-001)"
    required
    minLength={3}
    maxLength={50}
    pattern="[A-Z0-9-_]+"
  />
  <input
    type="text"
    name="name"
    placeholder="Project Name"
    required
  />
  <button type="submit">Create Project</button>
</form>
```

---

## 🔐 **Security Considerations**

### **Project Code is NOT Secret**
- ✅ Safe to display in UI
- ✅ Safe to use in logs
- ✅ Safe to share with team members
- ❌ Don't use as authentication
- ❌ Don't use as password

### **Access Control**
- Project code doesn't bypass security
- Users still need to own the project to access it
- `verify_project_access()` still checks `owner_id`

---

## 📈 **Benefits**

### **For Developers:**
- ✅ Easier debugging (readable codes in logs)
- ✅ Faster database queries (indexed)
- ✅ Better error messages
- ✅ Cleaner code (use codes instead of UUIDs)

### **For Users:**
- ✅ Easy project identification
- ✅ Memorable project references
- ✅ Better organization
- ✅ Professional appearance

### **For Teams:**
- ✅ Clear communication
- ✅ Consistent naming
- ✅ Quick project lookup
- ✅ Better collaboration

---

## 🚀 **Deployment Steps**

1. **Update code** (already done)
2. **Run migration**:
   ```bash
   cd backend
   alembic upgrade head
   ```
3. **Restart backend**:
   ```bash
   # If using Docker
   docker-compose restart backend
   
   # If running manually
   # Stop and restart uvicorn
   ```
4. **Update frontend** (if needed):
   - Add `project_code` field to create/update forms
   - Display `project_code` in project lists
5. **Test**:
   - Create new project with code
   - Try duplicate code (should fail)
   - Update existing project code
   - Verify uniqueness

---

## ✅ **Summary**

**What Changed:**
- ✅ Added `project_code` field to Project model
- ✅ Added unique constraint and index
- ✅ Updated API schemas (Create, Update, Response)
- ✅ Added validation for uniqueness
- ✅ Created database migration
- ✅ Auto-generates codes for existing projects

**What You Need to Do:**
1. Run migration: `alembic upgrade head`
2. Restart backend
3. Update frontend to include `project_code` field
4. (Optional) Update auto-generated codes to meaningful ones

**Benefits:**
- ✅ Easy project identification
- ✅ Better organization
- ✅ Improved logging and debugging
- ✅ Professional appearance
- ✅ Team collaboration

---

**Questions?** Check the API documentation at `/docs` for interactive examples!
