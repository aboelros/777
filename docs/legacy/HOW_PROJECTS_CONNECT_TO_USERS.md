# 🔗 How Projects Are Connected to Users

## 📊 **Database Relationship**

### **Schema Overview**

```
┌─────────────────────────┐
│       USERS TABLE       │
├─────────────────────────┤
│ id (UUID) PK            │ ←──────┐
│ email (unique)          │        │
│ password_hash           │        │ ONE-TO-MANY
│ name                    │        │ RELATIONSHIP
│ role                    │        │
│ is_active               │        │
│ created_at              │        │
└─────────────────────────┘        │
                                   │
                                   │
                                   │
┌─────────────────────────┐        │
│     PROJECTS TABLE      │        │
├─────────────────────────┤        │
│ id (UUID) PK            │        │
│ owner_id (UUID) FK ─────┼────────┘
│ project_code (unique)   │
│ name                    │
│ description             │
│ timezone                │
│ settings (JSONB)        │
│ is_active               │
│ created_at              │
│ updated_at              │
└─────────────────────────┘
```

---

## 🔑 **The Connection: `owner_id`**

### **Database Level**

**In `backend/app/db/models.py`:**

```python
class Project(Base):
    """Project/Brand model - multi-tenant support."""
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # 🔗 THIS IS THE CONNECTION!
    owner_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"),  # Links to users.id
        nullable=False  # Every project MUST have an owner
    )
    
    project_code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    # ... other fields ...
    
    # Relationship (for ORM queries)
    owner = relationship("User", back_populates="projects")
```

**What this means:**
- Every project has an `owner_id` field
- `owner_id` is a **foreign key** pointing to `users.id`
- **CASCADE DELETE**: If a user is deleted, all their projects are deleted too
- **NOT NULL**: A project cannot exist without an owner

---

## 👤 **User Side**

**In `backend/app/db/models.py`:**

```python
class User(Base):
    """User model."""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255))
    role = Column(String(50), default="user")
    # ... other fields ...
    
    # Relationship (for ORM queries)
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
```

**What this means:**
- A user can have **multiple projects** (one-to-many)
- When you query `user.projects`, you get all projects owned by that user
- **DELETE ORPHAN**: If the relationship is removed, the project is deleted

---

## 🔄 **How It Works in Practice**

### **1. Creating a Project**

**When a user creates a project:**

```python
# backend/app/api/v1/projects.py (line 33-39)

new_project = Project(
    owner_id=UUID(user_id),  # ← User's ID from JWT token
    project_code=project_data.project_code,
    name=project_data.name,
    description=project_data.description,
    timezone=project_data.timezone,
    settings=project_data.settings or {}
)
```

**Flow:**
```
1. User logs in → Gets JWT token with user_id
2. User creates project → API extracts user_id from token
3. Project created with owner_id = user_id
4. Project saved to database
```

**Database Result:**
```sql
INSERT INTO projects (id, owner_id, project_code, name, ...)
VALUES (
    'project-uuid',
    'user-uuid',  -- ← This links the project to the user
    'MYSTORE-001',
    'My Store',
    ...
);
```

---

### **2. Listing Projects**

**When a user lists their projects:**

```python
# backend/app/api/v1/projects.py (line 88-92)

result = await db.execute(
    select(Project)
    .where(Project.owner_id == UUID(user_id))  # ← FILTER by owner
    .order_by(Project.created_at.desc())
)
projects = result.scalars().all()
```

**Flow:**
```
1. User requests projects → API extracts user_id from JWT token
2. Database query: SELECT * FROM projects WHERE owner_id = user_id
3. Returns ONLY projects owned by this user
```

**SQL Query:**
```sql
SELECT * FROM projects 
WHERE owner_id = 'user-uuid'  -- ← Only this user's projects
ORDER BY created_at DESC;
```

---

### **3. Accessing a Specific Project**

**When a user accesses a project:**

```python
# backend/app/api/v1/projects.py (line 107-112)

result = await db.execute(
    select(Project)
    .where(Project.id == project_id)
    .where(Project.owner_id == UUID(user_id))  # ← Security check
)
project = result.scalar_one_or_none()

if not project:
    raise HTTPException(404, "Project not found")  # ← Access denied!
```

**Flow:**
```
1. User requests project by ID
2. Database checks: Does this project exist AND does it belong to this user?
3. If YES → Return project
4. If NO → Return 404 (even if project exists but belongs to another user)
```

**SQL Query:**
```sql
SELECT * FROM projects 
WHERE id = 'project-uuid' 
  AND owner_id = 'user-uuid';  -- ← Both conditions must match
```

---

## 🔐 **Security: Multi-Tenant Isolation**

### **How It Prevents Cross-User Access**

**Scenario:**
- User A (ID: `aaa-111`) owns Project X (ID: `xxx-111`)
- User B (ID: `bbb-222`) tries to access Project X

**What Happens:**

```python
# User B's request
GET /api/v1/projects/xxx-111
Authorization: Bearer <User B's token>

# Backend extracts user_id from token
user_id = "bbb-222"  # User B's ID

# Database query
SELECT * FROM projects 
WHERE id = 'xxx-111'           # Project X
  AND owner_id = 'bbb-222';    # User B's ID

# Result: NO MATCH (Project X has owner_id = 'aaa-111')
# Response: 404 Not Found
```

**User B cannot access Project X!** ✅

---

## 📊 **Real-World Example**

### **Database State:**

```sql
-- USERS TABLE
| id      | email              | name    |
|---------|-------------------|---------|
| aaa-111 | alice@example.com | Alice   |
| bbb-222 | bob@example.com   | Bob     |

-- PROJECTS TABLE
| id      | owner_id | project_code | name           |
|---------|----------|--------------|----------------|
| xxx-111 | aaa-111  | ALICE-STORE  | Alice's Store  |
| xxx-222 | aaa-111  | ALICE-BRAND  | Alice's Brand  |
| yyy-111 | bbb-222  | BOB-SHOP     | Bob's Shop     |
```

### **Queries:**

**Alice lists her projects:**
```sql
SELECT * FROM projects WHERE owner_id = 'aaa-111';

Result:
- ALICE-STORE (Alice's Store)
- ALICE-BRAND (Alice's Brand)
```

**Bob lists his projects:**
```sql
SELECT * FROM projects WHERE owner_id = 'bbb-222';

Result:
- BOB-SHOP (Bob's Shop)
```

**Alice tries to access Bob's project:**
```sql
SELECT * FROM projects 
WHERE id = 'yyy-111' AND owner_id = 'aaa-111';

Result: NO MATCH (yyy-111 has owner_id = 'bbb-222')
Response: 404 Not Found
```

---

## 🔗 **Relationship Types**

### **1. One-to-Many (User → Projects)**

```
User A
  ├─ Project 1
  ├─ Project 2
  └─ Project 3

User B
  ├─ Project 4
  └─ Project 5
```

**A user can have MANY projects**  
**A project belongs to ONE user**

### **2. Cascade Behavior**

**If User A is deleted:**
```sql
DELETE FROM users WHERE id = 'aaa-111';

-- Automatically deletes:
- Project 1 (owner_id = aaa-111)
- Project 2 (owner_id = aaa-111)
- Project 3 (owner_id = aaa-111)
```

This is because of `ondelete="CASCADE"` in the foreign key.

---

## 🎯 **How JWT Token Works**

### **Login Flow:**

```
1. User logs in with email + password
   POST /api/v1/auth/login
   { "email": "alice@example.com", "password": "..." }

2. Backend verifies credentials
   - Checks email exists
   - Verifies password hash

3. Backend creates JWT token
   token = jwt.encode({
       "sub": "aaa-111",  # ← User's ID
       "email": "alice@example.com",
       "exp": expiration_time
   }, SECRET_KEY)

4. Frontend receives token
   { "access_token": "eyJhbGc...", ... }

5. Frontend stores token
   localStorage.setItem('access_token', token)

6. Frontend sends token with every request
   Authorization: Bearer eyJhbGc...
```

### **API Request Flow:**

```
1. Frontend makes request
   GET /api/v1/projects
   Authorization: Bearer eyJhbGc...

2. Backend extracts token
   token = request.headers['Authorization'].split(' ')[1]

3. Backend decodes token
   payload = jwt.decode(token, SECRET_KEY)
   user_id = payload['sub']  # ← "aaa-111"

4. Backend uses user_id in query
   SELECT * FROM projects WHERE owner_id = 'aaa-111'

5. Returns ONLY this user's projects
```

---

## 📋 **Summary**

### **Connection Method:**
- **Foreign Key**: `projects.owner_id` → `users.id`
- **Relationship**: One user → Many projects
- **Security**: Every query filters by `owner_id`

### **Key Points:**
✅ Every project has an `owner_id`  
✅ `owner_id` links to the user who created it  
✅ Users can only see/edit their own projects  
✅ API filters all queries by `owner_id`  
✅ JWT token identifies which user is making the request  
✅ Database enforces referential integrity  

### **Security Guarantees:**
🔒 User A cannot see User B's projects  
🔒 User A cannot edit User B's projects  
🔒 User A cannot delete User B's projects  
🔒 If User A is deleted, their projects are deleted too  
🔒 A project cannot exist without an owner  

---

## 🔍 **Verify the Connection**

### **Check Database:**

```sql
-- See all projects with their owners
SELECT 
    p.project_code,
    p.name AS project_name,
    u.email AS owner_email,
    u.name AS owner_name
FROM projects p
JOIN users u ON p.owner_id = u.id
ORDER BY u.email, p.created_at;
```

### **Check via API:**

```bash
# Login as User A
curl -X POST https://api.example.com/api/v1/auth/login \
  -d '{"email": "alice@example.com", "password": "..."}'

# Get token from response
TOKEN="eyJhbGc..."

# List projects (should only see Alice's projects)
curl https://api.example.com/api/v1/projects \
  -H "Authorization: Bearer $TOKEN"
```

---

**The connection is simple but powerful: `owner_id` links projects to users, and the API enforces this relationship on every request!** 🔗
