# 🔐 Login Credentials

## ✅ **Updated Test Account (No Browser Warnings!)**

The test account password has been updated to a secure password that won't trigger browser breach warnings.

---

## 📧 **Test Account Credentials:**

```
Email:    test@aisales.local
Password: AiSales2024!Demo
```

---

## 🚀 **How To Use:**

### **Step 1:** Start the application
```bash
docker-compose up -d
```

### **Step 2:** Open browser
```
http://localhost:3000
```

### **Step 3:** Login with credentials
```
📧 Email: test@aisales.local
🔑 Password: AiSales2024!Demo
```

### **Step 4:** Create your projects and start using AI Sales Commander!

---

## 🔒 **Why Did We Change This?**

### **Old Credentials (Had Issues):**
- Email: `1111111@test.com`
- Password: `1111111`
- ❌ Browser warning: "Password found in data breach"
- ❌ Very weak password

### **New Credentials (Secure):**
- Email: `test@aisales.local`
- Password: `AiSales2024!Demo`
- ✅ No browser warnings
- ✅ Secure password (uppercase, lowercase, numbers, special chars)
- ✅ Meets all security requirements

---

## 🛡️ **Security Notes:**

### **For Development:**
- ✅ This test account is **only created in development mode**
- ✅ It's automatically created on first startup
- ✅ Perfect for testing and demos

### **For Production:**
- ⚠️ **DO NOT use test credentials in production!**
- ⚠️ Create proper user accounts via registration
- ⚠️ Use strong, unique passwords
- ⚠️ Enable 2FA (future feature)

---

## 🎯 **Creating New Accounts:**

### **Via Frontend:**
1. Go to login page
2. Click "Sign Up" (if available)
3. Fill in your details
4. Use a strong password!

### **Via API:**
```bash
POST /api/v1/auth/register
{
  "email": "your@email.com",
  "password": "YourSecurePassword123!",
  "name": "Your Name"
}
```

---

## 📝 **Password Requirements:**

For new accounts, passwords must have:
- ✅ Minimum 8 characters
- ✅ At least one uppercase letter
- ✅ At least one lowercase letter
- ✅ At least one digit
- ✅ Optional: Special characters

**Example good passwords:**
- `MyStore2024!`
- `AiSales#2024`
- `SecurePass123!`

**Example bad passwords:**
- `password` (too simple)
- `12345678` (no letters)
- `Password` (no numbers)

---

## 🔄 **First Time Setup:**

When you first start the backend, it will automatically:

1. ✅ Create database tables
2. ✅ Create test account (`test@aisales.local`)
3. ✅ Create demo project
4. ✅ Log credentials to console

**Look for this in backend logs:**
```
============================================================
✅ DATABASE READY FOR TESTING!
============================================================
📧 Email: test@aisales.local
🔑 Password: AiSales2024!Demo
============================================================
```

---

## 🎉 **You're Ready!**

No more browser warnings! Login with the new secure credentials and enjoy your AI Sales Commander! 🚀✨
