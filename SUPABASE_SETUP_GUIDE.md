# 🔧 Supabase Setup - Step by Step

## Your First Database Configuration

---

## 📊 **What You Have:**

### **Database 1 (Auth Database):**
```
Project URL: https://gznafnmgtrgtlxzxxbzy.supabase.co
Project Ref: gznafnmgtrgtlxzxxbzy
Anon API Key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd6bmFmbm1ndHJndGx4enh4Ynp5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA1ODAzMDAsImV4cCI6MjA3NjE1NjMwMH0.s68nAmrAc1VsYI25WE1Sj_LA6gWH3y17fv0VjMT0W0U
```

---

## 🔑 **What You NEED:**

You need the **PostgreSQL Connection String**, not just the API URL!

### **Where to Find It:**

```
1. Go to your Supabase dashboard:
   https://supabase.com/dashboard/project/gznafnmgtrgtlxzxxbzy

2. Click on "Settings" (left sidebar, bottom)

3. Click on "Database"

4. Scroll down to "Connection String"

5. Select "URI" tab

6. Copy the connection string that looks like:
   postgresql://postgres:[YOUR-PASSWORD]@db.gznafnmgtrgtlxzxxbzy.supabase.co:5432/postgres

7. Replace [YOUR-PASSWORD] with your actual database password
   (The password you set when creating the project)
```

---

## 📝 **Expected Connection String Format:**

```
postgresql://postgres:YOUR_PASSWORD_HERE@db.gznafnmgtrgtlxzxxbzy.supabase.co:5432/postgres
```

**IMPORTANT:** Replace `YOUR_PASSWORD_HERE` with the password you set when creating the project!

---

## ⚠️ **Common Mistakes:**

### ❌ **Wrong (API URL):**
```
https://gznafnmgtrgtlxzxxbzy.supabase.co
```
This is for REST API, not PostgreSQL!

### ✅ **Correct (PostgreSQL Connection String):**
```
postgresql://postgres:your_password@db.gznafnmgtrgtlxzxxbzy.supabase.co:5432/postgres
```
This is what your backend needs!

---

## 🎯 **Next Steps:**

### **Step 1: Get Your Connection String**

Go to Supabase Dashboard:
```
https://supabase.com/dashboard/project/gznafnmgtrgtlxzxxbzy/settings/database
```

Copy the connection string and **replace the password**!

### **Step 2: Create Second Database**

You need TWO databases:
- **Database 1:** For authentication (users, passwords) ← You just created this!
- **Database 2:** For application data (projects, orders, messages)

Create the second one:
```
1. Go to https://supabase.com
2. Click "New Project"
3. Name: aisales-app (or similar)
4. Choose same region as first database
5. Set password (can be same or different)
6. Wait 2 minutes
7. Get connection string from Settings → Database
```

### **Step 3: Update Your .env File**

Once you have BOTH connection strings:

```bash
# Open backend/.env and add:

# Auth Database (first database you created)
AUTH_DATABASE_URL=postgresql://postgres:PASSWORD1@db.gznafnmgtrgtlxzxxbzy.supabase.co:5432/postgres

# App Database (second database you'll create)
APP_DATABASE_URL=postgresql://postgres:PASSWORD2@db.XXXXXX.supabase.co:5432/postgres
```

---

## 🔐 **Finding Your Password:**

### **Option 1: You Remember It**
Use the password you set when creating the project!

### **Option 2: You Forgot It**
Reset it:
```
1. Go to Settings → Database
2. Scroll to "Database Settings"
3. Click "Reset Database Password"
4. Set new password
5. Update your connection string
```

---

## 📸 **Visual Guide:**

### **Where to Find Connection String:**

```
Supabase Dashboard
└── Your Project (gznafnmgtrgtlxzxxbzy)
    └── Settings (⚙️ icon, bottom left)
        └── Database
            └── Connection String
                └── URI (tab)
                    └── Copy this! ✅
```

---

## ✅ **Quick Checklist:**

Before continuing, make sure you have:

- [ ] Created **Database 1** (Auth) ✅ YOU HAVE THIS!
- [ ] Found connection string for Database 1
- [ ] Created **Database 2** (App) ⏳ DO THIS NEXT
- [ ] Found connection string for Database 2
- [ ] Updated `backend/.env` with both URLs
- [ ] Restarted your application

---

## 🚀 **What I'll Do Next:**

Once you provide:
1. ✅ Database 1 connection string (with password)
2. ⏳ Database 2 connection string (create it first)

I will:
- ✅ Update your `backend/.env` automatically
- ✅ Configure your application
- ✅ Test the connections
- ✅ Deploy your app with cloud databases!

---

## 📞 **Reply With:**

```
Database 1 (Auth):
postgresql://postgres:YOUR_PASSWORD@db.gznafnmgtrgtlxzxxbzy.supabase.co:5432/postgres

Database 2 (App):
postgresql://postgres:YOUR_PASSWORD@db.XXXXXX.supabase.co:5432/postgres
```

**Then I'll configure everything for you!** 🎉
