# 🚀 AI Sales Commander - Complete User Guide

## 📋 Table of Contents
1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [AI Assistant Features](#ai-assistant-features)
4. [Reports & Analytics](#reports--analytics)
5. [API Endpoints](#api-endpoints)
6. [How to Use Features](#how-to-use-features)

---

## 🎯 Overview

**AI Sales Commander** is a comprehensive e-commerce AI assistant platform that automates customer support, order management, and provides intelligent analytics.

### ✨ Key Features

#### 🤖 AI Assistant (Powered by Google Gemini)
- **Intelligent Customer Support**: Automatically respond to customer inquiries
- **Order Management**: Query and update orders via natural language
- **Sentiment Analysis**: Understand customer emotions and urgency
- **Function Calling**: AI can take actions (send messages, update orders, create tickets)
- **Context-Aware**: Remembers conversation history and order details
- **Multi-Channel**: Works with WhatsApp, Telegram, Instagram, Facebook

#### 📊 Advanced Reports & Analytics
- **Sales Reports**: Revenue, order value, trends
- **Order Reports**: Fulfillment rates, status tracking
- **Customer Reports**: Engagement metrics, channel usage
- **Performance Reports**: AI automation metrics, system health
- **ROI Reports**: Cost savings from AI automation
- **AI-Powered Insights**: Actionable recommendations

#### 🔗 Integrations
- **Shopify**: Sync orders automatically
- **WhatsApp Business**: Customer messaging
- **Telegram**: Bot integration
- **Instagram/Facebook**: Social media support
- **Custom APIs**: Extensible architecture

---

## 🚀 Getting Started

### 1. Login
```
Email: 1111111@test.com
Password: 1111111
```

### 2. Access the Dashboard
After login, you'll see:
- **Overview**: Key metrics at a glance
- **Recent Orders**: Latest transactions
- **Messages**: Customer communications
- **AI Usage**: Token consumption and costs

### 3. Navigation
- **📊 Dashboard**: Main overview
- **📦 Orders**: Manage orders
- **💬 Messages**: Customer conversations
- **🤖 AI Assistant**: Chat with AI
- **📈 Reports**: Generate analytics
- **🔗 Integrations**: Connect platforms

---

## 🤖 AI Assistant Features

### How to Use the AI Assistant

The AI assistant can help you with various tasks through natural language.

#### 1. Query the Assistant
```
POST /api/v1/assistant/query
```

**Example Request:**
```json
{
  "project_id": "your-project-id",
  "message": "What orders do we have pending?",
  "order_id": "optional-order-id",
  "context": {},
  "use_function_calling": true
}
```

**What You Can Ask:**
- "Show me today's sales"
- "How many pending orders do we have?"
- "Generate a reply to this customer message"
- "What's the status of order #12345?"
- "Send a WhatsApp message to customer about their order"

#### 2. Generate Customer Replies
```
POST /api/v1/assistant/generate-reply
```

**Example:**
```json
{
  "project_id": "your-project-id",
  "order_id": "order-123",
  "customer_message": "When will my order arrive?"
}
```

**AI Will:**
- Understand the context
- Check order status
- Generate professional response
- Suggest follow-up actions

#### 3. Analyze Sentiment
```
POST /api/v1/assistant/analyze-sentiment
```

**Returns:**
- Sentiment: positive/neutral/negative
- Urgency: low/medium/high/urgent
- Key concerns
- Recommended response tone

### AI Function Calling

The AI can autonomously execute these actions:

1. **send_message**: Send messages to customers
2. **update_order_status**: Change order statuses
3. **fetch_order_details**: Get order information
4. **create_support_ticket**: Escalate issues
5. **schedule_followup**: Set automated reminders
6. **generate_report**: Create analytics reports
7. **track_order**: Get tracking information
8. **analyze_customer_sentiment**: Analyze emotions

---

## 📊 Reports & Analytics

### Available Report Types

#### 1. Sales Report
**What it includes:**
- Total revenue
- Number of orders
- Average order value
- Revenue by day
- Top performing days
- Status breakdown
- AI-generated insights

**How to Generate:**
```javascript
// Frontend
const report = await reports.generate({
  report_type: 'sales',
  start_date: '2025-01-01',
  end_date: '2025-01-31'
});
```

#### 2. Orders Report
**What it includes:**
- Total orders
- Fulfillment rate
- Cancellation rate
- Provider breakdown
- Order details
- Status distribution

#### 3. Customer Report
**What it includes:**
- Total messages
- Unique customers
- Response rate
- Channel usage
- Engagement trends
- Messages per customer

#### 4. Performance Report
**What it includes:**
- AI usage rate
- Average response time
- Active integrations
- System health
- Message processing rate

#### 5. ROI Report
**What it includes:**
- Revenue impact
- Time saved by AI
- Cost savings estimate
- Conversion rates
- Productivity gains
- Automation efficiency

### Using Reports

**Frontend Usage:**
```javascript
import { reports } from './services/api';

// Generate report
const salesReport = await reports.generate({
  report_type: 'sales',
  start_date: new Date('2025-01-01'),
  end_date: new Date('2025-01-31')
});

// List all reports
const allReports = await reports.list();

// Get specific report
const report = await reports.get(reportId);
```

---

## 🔌 API Endpoints

### Authentication
```
POST /api/v1/auth/login         - Login
POST /api/v1/auth/register      - Register new user
GET  /api/v1/auth/me            - Get current user
POST /api/v1/auth/refresh       - Refresh token
```

### AI Assistant
```
POST /api/v1/assistant/query              - Ask AI anything
POST /api/v1/assistant/generate-reply     - Generate customer reply
POST /api/v1/assistant/analyze-sentiment  - Analyze message sentiment
GET  /api/v1/assistant/usage/{project_id} - Get AI usage stats
```

### Reports
```
POST   /api/v1/reports/{project_id}/generate      - Generate new report
GET    /api/v1/reports/{project_id}               - List all reports
GET    /api/v1/reports/{project_id}/{report_id}   - Get specific report
DELETE /api/v1/reports/{project_id}/{report_id}   - Delete report
```

### Orders
```
GET    /api/v1/orders/{project_id}         - List orders
GET    /api/v1/orders/{project_id}/{id}    - Get order details
POST   /api/v1/orders/{project_id}         - Create order
PATCH  /api/v1/orders/{project_id}/{id}    - Update order
DELETE /api/v1/orders/{project_id}/{id}    - Delete order
```

### Messages
```
GET    /api/v1/messages/{project_id}       - List messages
GET    /api/v1/messages/{project_id}/{id}  - Get message
POST   /api/v1/messages/{project_id}       - Send message
```

### Integrations
```
GET    /api/v1/integrations/{project_id}             - List integrations
POST   /api/v1/integrations/{project_id}/connect     - Connect platform
POST   /api/v1/integrations/{project_id}/{id}/sync   - Sync data
DELETE /api/v1/integrations/{project_id}/{id}        - Disconnect
```

---

## 💡 How to Use Features

### 1. Connecting Shopify

1. Go to **Integrations** page
2. Click **Connect Shopify**
3. Enter your Shopify credentials:
   - Shop URL: `your-store.myshopify.com`
   - Access Token: (from Shopify admin)
4. Click **Connect**
5. Orders will sync automatically every 15 minutes

### 2. Using AI Assistant in Chat

**In the frontend:**
1. Navigate to **AI Assistant** page
2. Select a project
3. Type your question or request
4. AI will respond with:
   - Answer to your question
   - Suggested actions
   - Function calls (if applicable)

**Example Conversations:**

```
You: "What are today's sales?"
AI: "Today you've had 15 orders totaling $1,245.50. Your best-selling product is..."

You: "Send a thank you message to customer ID 123"
AI: "I'll send that message. Here's what I'll send: [message preview]"
[Function Call: send_message(customer_id=123, message="...", channel="whatsapp")]

You: "Generate a sales report for last week"
AI: "I'll generate that report for you."
[Function Call: generate_report(report_type="sales", date_range="last_7_days")]
```

### 3. Generating Reports

**Method 1: Via UI**
1. Go to **Reports** page
2. Click **Generate New Report**
3. Select report type
4. Choose date range
5. Click **Generate**
6. View insights and download

**Method 2: Via AI Assistant**
```
You: "Generate a ROI report for this month"
AI: [Generates and displays report]
```

**Method 3: Via API**
```javascript
const report = await fetch(`${API_URL}/api/v1/reports/${projectId}/generate`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    report_type: 'roi',
    start_date: '2025-01-01',
    end_date: '2025-01-31'
  })
});
```

### 4. Automated Customer Support

**Setup:**
1. Connect your messaging platforms (WhatsApp, Telegram, etc.)
2. Enable AI auto-response in settings
3. Configure response templates

**How it works:**
1. Customer sends message
2. AI analyzes sentiment and intent
3. AI generates appropriate response
4. Response is sent automatically (or requires approval based on settings)
5. Human can take over anytime

### 5. Monitoring AI Usage

**Check costs:**
1. Navigate to **Dashboard**
2. View "AI Usage" widget
3. See:
   - Total tokens used
   - Estimated costs
   - Messages automated
   - Time saved

**API endpoint:**
```
GET /api/v1/assistant/usage/{project_id}?days=30
```

---

## 🎨 Frontend Features

### Dark Theme with Glass Effects
- Modern dark UI with glassmorphism
- Smooth animations
- Responsive design
- Beautiful gradient cards

### Real-time Updates
- Live order updates
- Real-time message notifications
- Auto-refresh dashboards

### Data Visualizations
- Revenue charts
- Order trends
- Message analytics
- Performance metrics

---

## 🔧 Configuration

### Environment Variables

**Backend (.env):**
```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-1.5-pro
GEMINI_TEMPERATURE=0.7
GEMINI_MAX_TOKENS=2048

SHOPIFY_API_KEY=your_shopify_key
SHOPIFY_API_SECRET=your_shopify_secret

WHATSAPP_API_KEY=your_whatsapp_key
TELEGRAM_BOT_TOKEN=your_telegram_token
```

**Frontend (.env.local):**
```env
VITE_API_URL=http://localhost:8000
```

---

## 📈 Best Practices

### 1. AI Assistant Usage
- Be specific in your queries
- Provide context when asking about orders
- Review AI-generated messages before sending
- Use function calling for complex workflows

### 2. Reports
- Generate weekly reports to track trends
- Use AI insights for decision-making
- Export reports for offline analysis
- Compare periods to measure growth

### 3. Integration Management
- Keep integrations active
- Sync regularly
- Monitor sync logs
- Update credentials promptly

### 4. Cost Management
- Monitor AI token usage
- Set budget alerts
- Use AI for high-value tasks
- Optimize prompts for efficiency

---

## 🐛 Troubleshooting

### Login Issues
- Clear browser cache
- Check credentials
- Verify backend is running
- Check CORS settings

### AI Not Responding
- Verify GEMINI_API_KEY is set
- Check API quota
- Review backend logs
- Test with simple query

### Reports Not Generating
- Ensure date range has data
- Check database connection
- Verify project access
- Review error logs

### Integration Sync Failing
- Verify API credentials
- Check integration status
- Review sync logs
- Test API connection

---

## 🆘 Support

### Getting Help
1. Check logs: `docker-compose logs backend`
2. Review error messages in browser console
3. Check API documentation at `http://localhost:8000/docs`
4. Review this guide

### Log Locations
- **Backend**: Docker logs
- **Frontend**: Browser console
- **Database**: PostgreSQL logs
- **Celery**: Worker logs

---

## 🎉 Next Steps

1. ✅ Login to the platform
2. ✅ Create your first project
3. ✅ Connect Shopify
4. ✅ Set up messaging platforms
5. ✅ Try the AI assistant
6. ✅ Generate your first report
7. ✅ Enable automated responses
8. ✅ Monitor your ROI

---

## 📝 Summary

**AI Sales Commander** is your complete e-commerce automation platform with:
- 🤖 Intelligent AI assistant
- 📊 Comprehensive analytics
- 💬 Multi-channel messaging
- 📦 Order management
- 🔗 Platform integrations
- 💰 ROI tracking

**Everything is ready to use right now!**

---

*Built with ❤️ using FastAPI, React, Google Gemini AI, PostgreSQL, Redis, and Celery*
