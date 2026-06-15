# 📚 API Documentation

## Base URL

```
Development: http://localhost:8000
Production: https://api.yourdomain.com
```

## Authentication

All endpoints (except `/auth/register` and `/auth/login`) require JWT authentication.

### Headers

```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

---

## 🔐 Authentication Endpoints

### Register User

```http
POST /api/v1/auth/register
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "name": "John Doe"
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "user",
  "is_active": true,
  "created_at": "2025-01-12T10:00:00Z"
}
```

### Login

```http
POST /api/v1/auth/login
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 900
}
```

### Refresh Token

```http
POST /api/v1/auth/refresh
```

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Get Current User

```http
GET /api/v1/auth/me
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "user",
  "is_active": true,
  "created_at": "2025-01-12T10:00:00Z"
}
```

---

## 📁 Projects Endpoints

### Create Project

```http
POST /api/v1/projects
```

**Request Body:**
```json
{
  "name": "My Store",
  "description": "E-commerce store",
  "timezone": "America/New_York",
  "settings": {}
}
```

### List Projects

```http
GET /api/v1/projects
```

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "name": "My Store",
    "description": "E-commerce store",
    "timezone": "America/New_York",
    "is_active": true,
    "created_at": "2025-01-12T10:00:00Z"
  }
]
```

### Get Project

```http
GET /api/v1/projects/{project_id}
```

### Update Project

```http
PATCH /api/v1/projects/{project_id}
```

### Delete Project

```http
DELETE /api/v1/projects/{project_id}
```

---

## 🔌 Integrations Endpoints

### Connect Integration

```http
POST /api/v1/integrations/{project_id}/connect
```

**Request Body:**
```json
{
  "provider": "shopify",
  "config": {
    "api_key": "your-api-key",
    "api_secret": "your-api-secret",
    "shop_url": "yourstore.myshopify.com"
  }
}
```

### List Integrations

```http
GET /api/v1/integrations/{project_id}
```

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "project_id": "uuid",
    "provider": "shopify",
    "status": "connected",
    "config": {
      "api_key": "your...key",
      "shop_url": "yourstore.myshopify.com"
    },
    "last_sync": "2025-01-12T10:00:00Z",
    "created_at": "2025-01-12T09:00:00Z"
  }
]
```

### Sync Integration

```http
POST /api/v1/integrations/{project_id}/{integration_id}/sync
```

**Response:** `202 Accepted`
```json
{
  "status": "queued",
  "message": "Sync task queued for shopify integration"
}
```

### Disconnect Integration

```http
DELETE /api/v1/integrations/{project_id}/{integration_id}
```

---

## 🛒 Orders Endpoints

### List Orders

```http
GET /api/v1/orders/{project_id}?status=pending&days=30&page=1&page_size=50
```

**Query Parameters:**
- `status` (optional): Filter by status
- `provider` (optional): Filter by provider
- `days` (optional): Days to look back (default: 30)
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 50)

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "project_id": "uuid",
    "external_id": "1234",
    "provider": "shopify",
    "status": "pending",
    "customer": {
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+1234567890"
    },
    "items": [
      {
        "name": "Product A",
        "quantity": 2,
        "price": 29.99
      }
    ],
    "total": 59.98,
    "currency": "USD",
    "order_date": "2025-01-12T10:00:00Z"
  }
]
```

### Get Order

```http
GET /api/v1/orders/{project_id}/{order_id}
```

### Update Order

```http
PATCH /api/v1/orders/{project_id}/{order_id}
```

**Request Body:**
```json
{
  "status": "fulfilled",
  "fulfilled_date": "2025-01-12T12:00:00Z"
}
```

### Order Statistics

```http
GET /api/v1/orders/{project_id}/stats/summary?days=30
```

**Response:** `200 OK`
```json
{
  "period_days": 30,
  "total_orders": 150,
  "total_revenue": 12500.50,
  "orders_by_status": {
    "pending": 10,
    "fulfilled": 130,
    "cancelled": 10
  },
  "average_order_value": 83.34
}
```

---

## 💬 Messages Endpoints

### Send Message

```http
POST /api/v1/messages/{project_id}/send
```

**Request Body:**
```json
{
  "recipient": {
    "phone": "+1234567890",
    "name": "John Doe"
  },
  "content": "Your order has been shipped!",
  "provider": "whatsapp",
  "content_type": "text",
  "order_id": "uuid"
}
```

### Get Inbox

```http
GET /api/v1/messages/{project_id}/inbox?direction=inbound&days=7&page=1
```

**Query Parameters:**
- `direction` (optional): inbound or outbound
- `provider` (optional): Filter by provider
- `order_id` (optional): Filter by order
- `is_read` (optional): Filter by read status
- `days` (optional): Days to look back

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "project_id": "uuid",
    "order_id": "uuid",
    "direction": "inbound",
    "provider": "whatsapp",
    "content": "Where is my order?",
    "sender": {
      "phone": "+1234567890",
      "name": "John Doe"
    },
    "is_read": false,
    "ai_generated": false,
    "created_at": "2025-01-12T10:00:00Z"
  }
]
```

### Get Conversation

```http
GET /api/v1/messages/{project_id}/conversation/{order_id}
```

### Mark Message as Read

```http
PATCH /api/v1/messages/{project_id}/{message_id}/read
```

### Message Statistics

```http
GET /api/v1/messages/{project_id}/stats/summary?days=30
```

---

## 🤖 AI Assistant Endpoints

### Query Assistant

```http
POST /api/v1/assistant/query
```

**Request Body:**
```json
{
  "project_id": "uuid",
  "message": "What is the status of order #1234?",
  "use_function_calling": true,
  "context": {},
  "order_id": "uuid"
}
```

**Response:** `200 OK`
```json
{
  "reply": "Order #1234 is currently being prepared for shipment...",
  "function_calls": [
    {
      "name": "fetch_order_details",
      "parameters": {
        "order_id": "1234"
      }
    }
  ],
  "tokens_used": 150,
  "cost": 0.000375,
  "model": "gemini-1.5-pro-latest"
}
```

### Generate Reply

```http
POST /api/v1/assistant/generate-reply?project_id=uuid&order_id=uuid&customer_message=text
```

### Analyze Sentiment

```http
POST /api/v1/assistant/analyze-sentiment?project_id=uuid&message=text
```

**Response:** `200 OK`
```json
{
  "sentiment": "negative",
  "urgency": "high",
  "concerns": ["delivery delay", "order status"],
  "recommended_tone": "empathetic and proactive"
}
```

### AI Usage Statistics

```http
GET /api/v1/assistant/usage/{project_id}?days=30
```

**Response:** `200 OK`
```json
{
  "period_days": 30,
  "total_api_calls": 450,
  "total_tokens_used": 125000,
  "total_cost_usd": 0.3125,
  "average_cost_per_call": 0.000694
}
```

---

## 📊 Reports Endpoints

### Generate Report

```http
POST /api/v1/reports/{project_id}/generate
```

**Request Body:**
```json
{
  "report_type": "sales",
  "start_date": "2025-01-01T00:00:00Z",
  "end_date": "2025-01-31T23:59:59Z",
  "filters": {}
}
```

**Report Types:**
- `sales`: Sales performance and revenue analytics
- `messages`: Communication statistics
- `performance`: Overall system KPIs

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "project_id": "uuid",
  "report_type": "sales",
  "summary": "Generated 150 orders with $12,500.50 in total revenue...",
  "payload": {
    "total_orders": 150,
    "total_revenue": 12500.50,
    "...": "..."
  },
  "generated_at": "2025-01-12T10:00:00Z"
}
```

### List Reports

```http
GET /api/v1/reports/{project_id}?report_type=sales&page=1
```

### Get Report

```http
GET /api/v1/reports/{project_id}/{report_id}
```

### Delete Report

```http
DELETE /api/v1/reports/{project_id}/{report_id}
```

---

## 🔔 Webhooks

### Shopify Webhook

```http
POST /api/v1/webhooks/shopify
```

Receives order events from Shopify. Requires HMAC verification.

### WhatsApp Webhook

```http
POST /api/v1/webhooks/whatsapp
```

Receives incoming messages from WhatsApp Business API.

### Telegram Webhook

```http
POST /api/v1/webhooks/telegram
```

Receives bot updates from Telegram.

---

## Error Responses

### Standard Error Format

```json
{
  "detail": "Error message",
  "code": "ERROR_CODE",
  "timestamp": "2025-01-12T10:00:00Z"
}
```

### Common Status Codes

- `200 OK`: Request succeeded
- `201 Created`: Resource created
- `204 No Content`: Success with no response body
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

---

## Rate Limits

- **Authentication**: 5 requests/minute
- **AI Endpoints**: 60 requests/minute
- **Standard Endpoints**: 100 requests/minute

Headers returned on rate limit:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1673521200
```

---

## Interactive Documentation

For interactive API testing, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

**Last Updated**: 2025-01-12
