# 💳 Subscription & Billing System - Complete Guide

## 🎉 Overview

Your AI Sales Commander now has a complete **tiered subscription system** with 5 pricing plans from **$0 to $500/month**, usage tracking, limit enforcement, and a beautiful pricing page.

---

## 💰 Pricing Plans

### **5 Tiers from Free to Enterprise**

| Tier | Price/Month | Price/Year | Savings | Target |
|------|-------------|------------|---------|--------|
| **Free** | $0 | $0 | - | Individuals trying the platform |
| **Starter** | $25 | $250 | ~17% | Small businesses getting started |
| **Professional** | $99 | $999 | ~17% | Growing businesses (MOST POPULAR) |
| **Business** | $249 | $2,490 | ~17% | Established businesses scaling |
| **Enterprise** | $500 | $5,000 | ~17% | Large organizations |

---

## 📊 Plan Details

### **1. Free Plan ($0/month)**

**Limits:**
- 1 Project
- 100 Messages/month
- 10 Orders/month
- 1,000 AI Requests/month
- 2 Integrations
- 1GB Storage
- 1 Team Member

**Features:**
- Basic Analytics
- Community Support
- Order Creation
- Message Management

**Perfect For:**
- Testing the platform
- Personal projects
- Learning the system

---

### **2. Starter Plan ($25/month)**

**Limits:**
- 3 Projects
- 1,000 Messages/month
- 100 Orders/month
- 10,000 AI Requests/month
- 5 Integrations
- 10GB Storage
- 1 Team Member

**Features:**
- ✅ AI Auto-Responses
- ✅ Order Management
- ✅ Advanced Analytics
- ✅ Email Support

**Perfect For:**
- Small online stores
- Startups
- Side businesses

---

### **3. Professional Plan ($99/month)** ⭐ MOST POPULAR

**Limits:**
- 10 Projects
- 10,000 Messages/month
- 1,000 Orders/month
- 100,000 AI Requests/month
- Unlimited Integrations
- 50GB Storage
- 3 Team Members

**Features:**
- ✅ Full AI Automation
- ✅ Social Media Management
- ✅ Conversation Memory
- ✅ Customer Profiling
- ✅ Business Context Learning
- ✅ API Access
- ✅ Priority Email Support
- ✅ Weekly Reports

**Perfect For:**
- Growing e-commerce businesses
- Multi-channel sellers
- Agencies

---

### **4. Business Plan ($249/month)**

**Limits:**
- 25 Projects
- 50,000 Messages/month
- 5,000 Orders/month
- 500,000 AI Requests/month
- Unlimited Integrations
- 200GB Storage
- 5 Team Members

**Features:**
- ✅ Everything in Professional
- ✅ Bulk Operations
- ✅ Custom AI Training
- ✅ White-Label Options
- ✅ Phone & Email Support
- ✅ Daily Reports
- ✅ Custom Dashboards

**Perfect For:**
- Established e-commerce brands
- Multi-store operations
- Enterprise teams

---

### **5. Enterprise Plan ($500/month)**

**Limits:**
- ✨ **UNLIMITED** Everything
- Unlimited Projects
- Unlimited Messages
- Unlimited Orders
- Unlimited AI Requests
- 1TB+ Storage
- Unlimited Team Members

**Features:**
- ✅ Everything in Business
- ✅ Custom AI Models
- ✅ Dedicated Account Manager
- ✅ Custom Integrations
- ✅ SLA Guarantee
- ✅ 24/7 Priority Support
- ✅ Real-time Reports
- ✅ Custom Development
- ✅ On-premise Option
- ✅ Advanced Security
- ✅ Compliance Support

**Perfect For:**
- Large corporations
- Enterprise organizations
- Custom requirements

---

## 🗄️ Database Schema

### **User Model Updates**

Added subscription fields to `User` table:

```python
subscription_tier           # Enum: free, starter, professional, business, enterprise
subscription_status         # Enum: active, cancelled, expired, trial, past_due
subscription_started_at     # When subscription began
subscription_expires_at     # When it expires
stripe_customer_id          # Stripe customer ID
stripe_subscription_id      # Stripe subscription ID
```

### **Subscription Table**

New `subscriptions` table:

```python
# Core subscription details
tier                        # Current tier
status                      # Subscription status
billing_cycle              # monthly or annually
price_monthly              # Monthly price
price_annually             # Annual price

# Billing dates
started_at
expires_at
trial_ends_at
cancelled_at
next_billing_date

# Usage limits
limit_messages             # Messages per month
limit_orders               # Orders per month
limit_ai_requests          # AI requests per month
limit_projects             # Max projects
limit_integrations         # Max integrations
limit_storage_gb           # Storage in GB
limit_team_members         # Team size

# Features enabled
features                   # JSONB: {"ai_automation": true, ...}

# Billing history
total_paid                 # Total paid to date
invoices                   # Array of invoice objects
```

### **UsageTracking Table**

New `usage_tracking` table for billing:

```python
subscription_id            # FK to subscription
user_id                    # FK to user
period_start               # Billing period start
period_end                 # Billing period end

# Usage counts
messages_sent              # Messages sent
messages_received          # Messages received
orders_created             # Orders created
ai_requests                # AI API calls
ai_tokens_used             # Total tokens
storage_used_gb            # Storage used

# Cost tracking
ai_cost                    # AI usage cost
storage_cost               # Storage cost
total_cost                 # Total cost
limits_exceeded            # Array of exceeded limits
overage_charges            # Extra charges
```

---

## 🌐 API Endpoints

### **GET /subscriptions/plans**

Get all available subscription plans.

**Response:**
```json
{
  "success": true,
  "plans": [
    {
      "tier": "professional",
      "name": "Professional",
      "monthly_price": 99,
      "annual_price": 999,
      "description": "For growing businesses...",
      "features": [...],
      "limits": {
        "messages": 10000,
        "orders": 1000,
        "ai_requests": 100000,
        "projects": 10,
        "integrations": 999999,
        "storage_gb": 50.0,
        "team_members": 3,
        "ai_automation": true,
        "advanced_reports": true,
        ...
      }
    }
  ],
  "total": 5
}
```

---

### **GET /subscriptions/my-subscription**

Get current user's subscription details.

**Response:**
```json
{
  "success": true,
  "user_id": "uuid",
  "email": "user@example.com",
  "tier": "professional",
  "status": "active",
  "tier_info": {
    "name": "Professional",
    "monthly_price": 99,
    "features": [...]
  },
  "subscription": {
    "started_at": "2025-01-01T00:00:00Z",
    "expires_at": "2025-02-01T00:00:00Z",
    "next_billing_date": "2025-02-01T00:00:00Z",
    "billing_cycle": "monthly",
    "total_paid": 99.00
  },
  "usage": {
    "messages": 2456,
    "orders": 234,
    "projects": 5,
    "ai_requests": 45678,
    "storage_gb": 12.5
  },
  "limits_status": {
    "messages": {
      "allowed": true,
      "limit": 10000,
      "current": 2456,
      "remaining": 7544,
      "percentage_used": 24.6
    },
    "orders": {
      "allowed": true,
      "limit": 1000,
      "current": 234,
      "remaining": 766,
      "percentage_used": 23.4
    }
  }
}
```

---

### **POST /subscriptions/upgrade**

Upgrade or change subscription tier.

**Request:**
```json
{
  "tier": "professional",
  "billing_cycle": "annually"
}
```

**Response:**
```json
{
  "success": true,
  "subscription_id": "uuid",
  "tier": "professional",
  "status": "active",
  "billing_cycle": "annually",
  "price": 999,
  "next_billing_date": "2026-01-01T00:00:00Z",
  "message": "Successfully upgraded to Professional!"
}
```

---

### **GET /subscriptions/usage**

Get current month usage statistics.

**Response:**
```json
{
  "success": true,
  "usage": {
    "messages": 2456,
    "orders": 234,
    "projects": 5,
    "ai_requests": 45678,
    "ai_tokens": 1234567,
    "storage_gb": 12.5
  },
  "limits": {
    "messages": {
      "allowed": true,
      "limit": 10000,
      "current": 2456,
      "remaining": 7544,
      "percentage_used": 24.6
    }
  }
}
```

---

### **GET /subscriptions/check-limit/{resource}**

Check if user can use a specific resource.

**Example:** `/subscriptions/check-limit/messages`

**Response:**
```json
{
  "success": true,
  "resource": "messages",
  "can_use": true,
  "allowed": true,
  "limit": 10000,
  "current": 2456,
  "remaining": 7544,
  "percentage_used": 24.6
}
```

---

### **GET /subscriptions/check-feature/{feature}**

Check if user has access to a feature.

**Example:** `/subscriptions/check-feature/ai_automation`

**Response:**
```json
{
  "success": true,
  "feature": "ai_automation",
  "has_access": true
}
```

---

## 🎨 Frontend Pricing Page

### **Accessing the Page**

Navigate to: `http://localhost:3000/subscription`

### **Features**

#### **1. Current Subscription Display**
Shows your active plan with:
- Tier name and icon
- Current usage stats
- Messages, Orders, AI Requests counters

#### **2. Billing Toggle**
Switch between:
- **Monthly** billing
- **Annual** billing (Save 17%)

#### **3. Pricing Cards (5 Plans)**
Each card shows:
- Tier icon (Star, Zap, Users, TrendingUp, Crown)
- Price (monthly or annual)
- Savings for annual billing
- Feature list
- "Current Plan" or "Upgrade Now" button
- Popular badge for Professional tier

#### **4. Feature Comparison Table**
Complete comparison showing:
- All limits (messages, orders, AI requests, etc.)
- All features (checkmarks for included)
- Easy side-by-side comparison

#### **5. Visual Design**
- Beautiful gradient cards
- Animated hover effects
- Color-coded tiers
- Responsive layout
- Glass morphism design

---

## 🔒 Limit Enforcement

### **Automatic Limit Checking**

The system automatically checks limits for:

1. **Messages**: Before sending a message
2. **Orders**: Before creating an order
3. **AI Requests**: Before making AI call
4. **Projects**: Before creating project
5. **Storage**: Before uploading files

### **Usage Example in Code**

```python
from app.services.subscription_service import SubscriptionService

# Check if user can send message
subscription_service = SubscriptionService(db)
can_send = await subscription_service.can_use_resource(user_id, "messages")

if not can_send:
    raise HTTPException(
        status_code=429,
        detail="Message limit exceeded. Please upgrade your plan."
    )

# Track usage
await subscription_service.track_usage(user_id, "messages_sent", 1)
```

---

## 📈 Usage Tracking

### **Automatic Tracking**

Usage is tracked for:
- ✅ Messages sent/received
- ✅ Orders created
- ✅ AI requests made
- ✅ AI tokens used
- ✅ Storage consumed

### **Monthly Reset**

All usage counters reset on the 1st of each month.

### **Overage Handling**

When limits are exceeded:
1. User is notified
2. Action is blocked
3. Upgrade prompt shown
4. Optional: Allow overage with extra charge

---

## 🎯 Feature Access Control

### **Features by Tier**

| Feature | Free | Starter | Professional | Business | Enterprise |
|---------|------|---------|--------------|----------|------------|
| AI Automation | ❌ | ✅ | ✅ | ✅ | ✅ |
| Advanced Reports | ❌ | ✅ | ✅ | ✅ | ✅ |
| Social Media Mgmt | ❌ | ❌ | ✅ | ✅ | ✅ |
| Conversation Memory | ❌ | ❌ | ✅ | ✅ | ✅ |
| Order Automation | ❌ | ✅ | ✅ | ✅ | ✅ |
| API Access | ❌ | ❌ | ✅ | ✅ | ✅ |
| White Label | ❌ | ❌ | ❌ | ✅ | ✅ |
| Custom AI | ❌ | ❌ | ❌ | ✅ | ✅ |

### **Checking Feature Access**

```python
has_ai_automation = await subscription_service.can_use_feature(
    user_id,
    "ai_automation"
)

if not has_ai_automation:
    return {"error": "This feature requires Professional plan or higher"}
```

---

## 💳 Payment Integration (Stripe Ready)

### **Stripe Fields Included**

The system includes fields for Stripe integration:

```python
stripe_customer_id          # Stripe customer ID
stripe_subscription_id      # Stripe subscription ID
stripe_payment_method_id    # Payment method
```

### **Integration Points**

Ready to integrate with Stripe for:
1. **Subscription Creation**: Create Stripe subscription on upgrade
2. **Webhook Handling**: Process payment events
3. **Invoice Generation**: Automatic billing
4. **Payment Methods**: Card storage
5. **Cancellation**: Handle cancellations

---

## 🚀 Quick Start

### **Step 1: View Plans**

```bash
curl http://localhost:8000/api/v1/subscriptions/plans
```

### **Step 2: Check Current Subscription**

```bash
curl http://localhost:8000/api/v1/subscriptions/my-subscription \
  -H "Authorization: Bearer {token}"
```

### **Step 3: Upgrade Plan**

```bash
curl -X POST http://localhost:8000/api/v1/subscriptions/upgrade \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "tier": "professional",
    "billing_cycle": "annually"
  }'
```

### **Step 4: Check Usage**

```bash
curl http://localhost:8000/api/v1/subscriptions/usage \
  -H "Authorization: Bearer {token}"
```

---

## 📊 Admin Features

### **View All Subscriptions**

```sql
SELECT 
  u.email,
  u.subscription_tier,
  u.subscription_status,
  s.billing_cycle,
  s.next_billing_date,
  s.total_paid
FROM users u
LEFT JOIN subscriptions s ON u.id = s.user_id
ORDER BY s.total_paid DESC;
```

### **Track Monthly Revenue**

```sql
SELECT 
  subscription_tier,
  COUNT(*) as users,
  SUM(price_monthly) as monthly_revenue
FROM subscriptions
WHERE status = 'active' AND billing_cycle = 'monthly'
GROUP BY subscription_tier;
```

---

## 🎉 Summary

Your subscription system now includes:

✅ **5 pricing tiers** from $0 to $500/month  
✅ **Annual billing** with 17% savings  
✅ **Usage tracking** for all resources  
✅ **Automatic limit enforcement**  
✅ **Feature access control**  
✅ **Beautiful pricing page**  
✅ **Complete API** for management  
✅ **Stripe-ready** for payments  
✅ **Database models** fully implemented  
✅ **Per-user tier display**  

**Each user can see their tier and limits in the database!** 🎊

---

*Built with ❤️ for scalable SaaS pricing*  
*Last Updated: January 2025*
