# API Reference

Welcome to the unified API documentation. This API powers the omnichannel platform, enabling cross-channel messaging (WhatsApp, FB, IG, Telegram, Shopify), customer management, AI bot automation, and multi-tenant project separation.

---

## Authentication

The API uses a dual-token Authentication architecture, relying on JSON Web Tokens (JWT) for secure, stateless access, combined with HTTP-Only cookies for refresh operations to mitigate XSS attacks.

**Flow:**
1. **Login:** Send credentials. Receive a short-lived `access_token` in the JSON response and a long-lived `refresh_token` in an HTTP-Only secure cookie.
2. **Accessing Endpoints:** Provide the `access_token` in the Authorization header (`Bearer <access_token>`).
3. **Token Refresh:** When the `access_token` expires (401 response), hit the refresh endpoint. The server reads the secure cookie and issues a new `access_token`.

---

## Base URLs & Versioning

All endpoints are versioned. The current stable version is `v1`.

**Environments:**
- **Production:** `https://api.example.com/v1`
- **Staging:** `https://staging-api.example.com/v1`
- **Testing (Local):** `http://localhost:8000/v1`

---

## Auth Endpoints

### 1. Register User
**Method:** `POST`
**Path:** `/auth/register`
**Auth Required:** No

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "firstName": "John",
  "lastName": "Doe"
}
```
**Response:**
```json
{
  "status": "success",
  "data": {
    "user": {
      "id": "usr_943892",
      "email": "user@example.com"
    }
  }
}
```

### 2. Login
**Method:** `POST`
**Path:** `/auth/login`
**Auth Required:** No

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```
**Response:**
*(Note: A `refresh_token` is also set as an HTTP-only cookie)*
```json
{
  "status": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "expires_in": 3600,
    "user": {
      "id": "usr_943892",
      "email": "user@example.com",
      "role": "admin"
    }
  }
}
```

### 3. Token Refresh
**Method:** `POST`
**Path:** `/auth/refresh`
**Auth Required:** Yes (via Refresh Token Cookie)

**Request:** (Empty body, relies on cookie)
```json
{}
```
**Response:**
```json
{
  "status": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "expires_in": 3600
  }
}
```

### 4. Logout
**Method:** `POST`
**Path:** `/auth/logout`
**Auth Required:** Yes

**Request:**
```json
{}
```
**Response:**
```json
{
  "status": "success",
  "message": "Successfully logged out"
}
```

### 5. Get Current User (Me)
**Method:** `GET`
**Path:** `/auth/me`
**Auth Required:** Yes

**Request:**
```json
{}
```
**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "usr_943892",
    "email": "user@example.com",
    "projects": ["proj_111", "proj_222"]
  }
}
```

---

## Projects Endpoints (CRUD)

Projects ensure multi-tenant separation. Each project acts as an isolated workspace.

### 1. List Projects
**Method:** `GET`
**Path:** `/projects`
**Auth Required:** Yes

**Request:** None
**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": "proj_111",
      "name": "Main Store",
      "role": "owner",
      "created_at": "2023-01-01T12:00:00Z"
    }
  ]
}
```

### 2. Create Project
**Method:** `POST`
**Path:** `/projects`
**Auth Required:** Yes

**Request:**
```json
{
  "name": "Secondary Store",
  "timezone": "America/New_York"
}
```
**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "proj_222",
    "name": "Secondary Store"
  }
}
```

### 3. Get Project
**Method:** `GET`
**Path:** `/projects/:projectId`
**Auth Required:** Yes

**Request:** None
**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "proj_111",
    "name": "Main Store"
  }
}
```

### 4. Update Project
**Method:** `PUT`
**Path:** `/projects/:projectId`
**Auth Required:** Yes

**Request:**
```json
{
  "name": "Updated Store Name"
}
```
**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "proj_111",
    "name": "Updated Store Name"
  }
}
```

### 5. Delete Project
**Method:** `DELETE`
**Path:** `/projects/:projectId`
**Auth Required:** Yes

**Request:** None
**Response:**
```json
{
  "status": "success",
  "message": "Project deleted successfully"
}
```

---

## Messages Endpoints

These endpoints handle outbound and inbound messages across all platforms.

### 1. Send Message
**Method:** `POST`
**Path:** `/projects/:projectId/messages`
**Auth Required:** Yes

**Request:**
```json
{
  "channel": "whatsapp",
  "recipient_id": "+1234567890",
  "type": "text",
  "content": {
    "body": "Hello! Your order has shipped."
  }
}
```
**Response:**
```json
{
  "status": "success",
  "data": {
    "message_id": "msg_abc123",
    "status": "queued",
    "timestamp": "2023-10-01T10:00:00Z"
  }
}
```

### 2. List Messages
**Method:** `GET`
**Path:** `/projects/:projectId/messages?customer_id=cust_xyz&limit=50`
**Auth Required:** Yes

**Request:** None
**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "message_id": "msg_abc123",
      "direction": "outbound",
      "channel": "whatsapp",
      "content": {
        "body": "Hello! Your order has shipped."
      },
      "status": "delivered"
    }
  ]
}
```

---

## Orders Endpoints

### 1. Create Order
**Method:** `POST`
**Path:** `/projects/:projectId/orders`
**Auth Required:** Yes

**Request:**
```json
{
  "customer_id": "cust_888",
  "items": [
    {
      "product_id": "prod_1",
      "quantity": 2
    }
  ],
  "total_amount": 49.98,
  "currency": "USD"
}
```
**Response:**
```json
{
  "status": "success",
  "data": {
    "order_id": "ord_999",
    "status": "pending"
  }
}
```

### 2. List Orders
**Method:** `GET`
**Path:** `/projects/:projectId/orders`
**Auth Required:** Yes

**Request:** None
**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "order_id": "ord_999",
      "total_amount": 49.98,
      "status": "pending"
    }
  ]
}
```

---

## Products Endpoints

### 1. List Products
**Method:** `GET`
**Path:** `/projects/:projectId/products`
**Auth Required:** Yes

**Request:** None
**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "product_id": "prod_1",
      "name": "Wireless Headphones",
      "price": 24.99,
      "stock": 150
    }
  ]
}
```

### 2. Create Product
**Method:** `POST`
**Path:** `/projects/:projectId/products`
**Auth Required:** Yes

**Request:**
```json
{
  "name": "Wireless Mouse",
  "description": "Ergonomic wireless mouse",
  "price": 19.99,
  "sku": "WM-01"
}
```
**Response:**
```json
{
  "status": "success",
  "data": {
    "product_id": "prod_2",
    "name": "Wireless Mouse"
  }
}
```

---

## Customers Endpoints

### 1. List Customers
**Method:** `GET`
**Path:** `/projects/:projectId/customers`
**Auth Required:** Yes

**Request:** None
**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "customer_id": "cust_888",
      "name": "Alice Smith",
      "phone": "+1234567890",
      "tags": ["vip", "returning"]
    }
  ]
}
```

### 2. Update Customer
**Method:** `PUT`
**Path:** `/projects/:projectId/customers/:customerId`
**Auth Required:** Yes

**Request:**
```json
{
  "tags": ["vip", "returning", "wholesale"]
}
```
**Response:**
```json
{
  "status": "success",
  "data": {
    "customer_id": "cust_888",
    "tags": ["vip", "returning", "wholesale"]
  }
}
```

---

## Integrations Endpoints

Manage setup flows for third-party platforms.

### 1. WhatsApp Business API Setup
**Method:** `POST`
**Path:** `/projects/:projectId/integrations/whatsapp`
**Auth Required:** Yes

**Request:**
```json
{
  "phone_number_id": "12345",
  "waba_id": "67890",
  "access_token": "EAA..."
}
```
**Response:**
```json
{
  "status": "success",
  "message": "WhatsApp integration configured successfully"
}
```

### 2. Facebook/Instagram Setup
**Method:** `POST`
**Path:** `/projects/:projectId/integrations/meta`
**Auth Required:** Yes

**Request:**
```json
{
  "page_id": "111222",
  "access_token": "EAA..."
}
```
**Response:**
```json
{
  "status": "success",
  "message": "Meta integration active"
}
```

### 3. Telegram Setup
**Method:** `POST`
**Path:** `/projects/:projectId/integrations/telegram`
**Auth Required:** Yes

**Request:**
```json
{
  "bot_token": "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
}
```
**Response:**
```json
{
  "status": "success",
  "message": "Telegram bot registered and webhook set"
}
```

### 4. Shopify Setup
**Method:** `POST`
**Path:** `/projects/:projectId/integrations/shopify`
**Auth Required:** Yes

**Request:**
```json
{
  "shop_url": "my-store.myshopify.com",
  "access_token": "shpua_..."
}
```
**Response:**
```json
{
  "status": "success",
  "message": "Shopify store linked"
}
```

---

## Webhooks

Handles incoming events from external platforms (messages, order updates).

### 1. Inbound Webhook (General)
**Method:** `POST`
**Path:** `/webhooks/:provider`
*(Provider can be `whatsapp`, `meta`, `telegram`, `shopify`)*
**Auth Required:** Verification Signature Header (e.g., `X-Hub-Signature` for Meta)

**Request (Example Meta/WhatsApp):**
```json
{
  "object": "whatsapp_business_account",
  "entry": [
    {
      "id": "12345",
      "changes": [
        {
          "field": "messages",
          "value": {
            "messaging_product": "whatsapp",
            "messages": [
              {
                "from": "16505551234",
                "id": "wamid.HBgL...",
                "text": { "body": "Hi there!" }
              }
            ]
          }
        }
      ]
    }
  ]
}
```
**Response:**
```json
{
  "status": "success"
}
```

---

## AI / Bot Endpoints

### 1. Update Bot Persona/Prompt
**Method:** `PUT`
**Path:** `/projects/:projectId/bot/config`
**Auth Required:** Yes

**Request:**
```json
{
  "is_active": true,
  "system_prompt": "You are a helpful customer support agent for our shoe store.",
  "model": "gpt-4o"
}
```
**Response:**
```json
{
  "status": "success",
  "data": {
    "is_active": true
  }
}
```

---

## Analytics Endpoints

### 1. Get Project Analytics
**Method:** `GET`
**Path:** `/projects/:projectId/analytics?period=30d`
**Auth Required:** Yes

**Request:** None
**Response:**
```json
{
  "status": "success",
  "data": {
    "messages_sent": 12450,
    "messages_received": 11002,
    "orders_generated_via_bot": 340,
    "total_revenue": 14500.50
  }
}
```

---

## WebSocket

Real-time messaging protocol for the frontend dashboard.

**Connection URL:** `wss://api.example.com/v1/ws?token=<access_token>`

**Events:**
- **Incoming Message (`message.new`)**
  ```json
  {
    "event": "message.new",
    "data": {
      "message_id": "msg_11",
      "content": "Hello",
      "channel": "telegram"
    }
  }
  ```
- **Order Update (`order.updated`)**
  ```json
  {
    "event": "order.updated",
    "data": {
      "order_id": "ord_999",
      "status": "shipped"
    }
  }
  ```

---

## Error Codes & Responses

All errors follow a standard format:

```json
{
  "status": "error",
  "code": "ERROR_CODE",
  "message": "Human readable description."
}
```

| Code | HTTP Status | Description |
|---|---|---|
| `UNAUTHORIZED` | 401 | Missing or invalid authentication token. |
| `FORBIDDEN` | 403 | User does not have access to this resource/project. |
| `NOT_FOUND` | 404 | The requested resource was not found. |
| `VALIDATION_ERROR` | 400 | Invalid request body/parameters. |
| `RATE_LIMITED` | 429 | Too many requests. |
| `INTERNAL_ERROR` | 500 | An unexpected error occurred on the server. |

---

## Security

1. **Multi-Tenant Separation:** All endpoints (except auth and webhooks) require a `:projectId`. The server strictly validates that the authenticated user's `user.id` is linked to `projectId`.
2. **Rate Limiting:** API requests are limited to 100 requests per minute per IP. Auth endpoints are limited to 10 requests per minute to prevent brute-force attacks.
3. **CORS:** Cross-Origin Resource Sharing is configured to only allow requests from authorized dashboard domains.
4. **CSP:** Content Security Policy headers are strictly enforced.
5. **JWT Expiry:** `access_token` expires in 15 minutes. `refresh_token` (HTTP-Only cookie) expires in 7 days.

---

## Testing the API

### TESTING_MODE
When the environment variable `TESTING_MODE=true` is set, the API bypasses external integrations (like actually calling the WhatsApp API) and mocks successful responses. This is ideal for local development and CI pipelines.

### cURL Example

```bash
# 1. Login to get token
curl -X POST http://localhost:8000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com", "password":"password"}'

# 2. Fetch Projects
curl -X GET http://localhost:8000/v1/projects \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 3. Send a Message
curl -X POST http://localhost:8000/v1/projects/proj_123/messages \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "whatsapp",
    "recipient_id": "+1234567890",
    "type": "text",
    "content": {"body": "Test message"}
  }'
```

### Postman
Import the OpenAPI spec (available at `/openapi.json`) into Postman. Set your `access_token` in the Authorization tab (Bearer Token) for the collection.
