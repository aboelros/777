# Automind Mobile — API Integration Specification

## 1. Overview & Architectural Principles

Automind Mobile integrates with the FastAPI backend through a typed API client using **Dio**. All requests are secured using JWT tokens, tenant project isolation, and standardized JSON payloads.

---

## 2. Base Configuration & Environments

```dart
class AppConfig {
  static const String devEmulatorUrl = 'http://10.0.2.2:8000';
  static const String devDeviceUrl = 'http://localhost:8000';
  static const String prodApiUrl = 'https://ai-sales-bot-api-vdr6.onrender.com';
  
  // WebSocket endpoints
  static const String devEmulatorWs = 'ws://10.0.2.2:8000';
  static const String prodWs = 'wss://ai-sales-bot-api-vdr6.onrender.com';
}
```

---

## 3. Endpoints and Payload Contracts

### 3.1 Authentication
- **POST `/api/v1/auth/login`**
  - Request: `{"email": "user@example.com", "password": "SecretPassword123"}`
  - Response:
    ```json
    {
      "access_token": "eyJhbG...",
      "refresh_token": "def456...",
      "token_type": "bearer",
      "expires_in": 3600
    }
    ```
- **POST `/api/v1/auth/refresh`**
  - Request: `{"refresh_token": "def456..."}`
  - Response: Updated `TokenResponse`
- **POST `/api/v1/auth/logout`**
  - Request Headers: `Authorization: Bearer <token>`
  - Request Body: `{"refresh_token": "def456..."}`
  - Response: `{"message": "Logged out successfully"}`
- **GET `/api/v1/auth/me`**
  - Response:
    ```json
    {
      "id": "uuid",
      "email": "user@example.com",
      "name": "Jane Doe",
      "role": "ADMIN",
      "is_active": true,
      "created_at": "2026-01-01T00:00:00Z"
    }
    ```

### 3.2 Projects & Tenant Authorization
All tenant-scoped endpoints require valid membership verified server-side.
- **GET `/api/v1/projects`**: Lists projects accessible to the authenticated user.
- **POST `/api/v1/projects`**: Creates a new project workspace.

### 3.3 Dashboard Summary
- **GET `/api/v1/reports/{project_id}/dashboard-summary`**
  - Returns period aggregates:
    ```json
    {
      "today": {"orders": 12, "revenue": 1450.0, "messages": 84, "escalations": 2},
      "yesterday": {"orders": 9, "revenue": 980.0, "messages": 62, "escalations": 1},
      "this_week": {"orders": 64, "revenue": 7820.0, "messages": 412, "escalations": 8},
      "this_month": {"orders": 240, "revenue": 31200.0, "messages": 1820, "escalations": 24}
    }
    ```

### 3.4 Unified Inbox & Human Takeover
- **GET `/api/v1/messages/{project_id}/conversations`**:
  Returns list of conversation summaries with `ai_enabled` flag, latest message, and unread counts.
- **GET `/api/v1/messages/{project_id}/conversations/{conversation_id}/messages`**:
  Returns paginated messages in conversation thread.
- **POST `/api/v1/messages/{project_id}/send`**:
  Sends a message from human agent or bot.
- **PATCH `/api/v1/messages/{project_id}/customers/{profile_id}/toggle-ai?enabled=false`**:
  **Takeover Trigger**: Sets `ai_enabled = false` for the specific customer profile so AI stops auto-replying and leaves conversation in human hands.

### 3.5 Real-Time WebSocket
- **URL**: `/ws/{project_id}`
- **Events**:
  ```json
  {
    "type": "new_message",
    "message": {
      "id": "uuid",
      "content": "Hello, is this product still in stock?",
      "direction": "inbound",
      "platform": "whatsapp",
      "created_at": "2026-10-22T10:00:00Z",
      "customer_id": "uuid",
      "customer_name": "Ahmad"
    }
  }
  ```

### 3.6 Orders Management
- **GET `/api/v1/orders/{project_id}`**: Retrieves list of orders.
- **GET `/api/v1/orders/{project_id}/{order_id}`**: Order details with line items and customer data.
- **PATCH `/api/v1/orders/{project_id}/{order_id}`**: Updates order status (`pending`, `confirmed`, `shipped`, `delivered`, `cancelled`).

### 3.7 AI Bot Training & Instructions
- **GET `/api/v1/bot-training/{project_id}/instructions`**: List of AI instructions.
- **POST `/api/v1/bot-training/{project_id}/instructions`**: Add new instruction.
- **PUT `/api/v1/bot-training/{project_id}/instructions/{id}`**: Update instruction.
- **DELETE `/api/v1/bot-training/{project_id}/instructions/{id}`**: Delete instruction.

### 3.8 Products Catalog
- **GET `/api/v1/products/{project_id}`**: List of catalog products.
- **POST `/api/v1/products/{project_id}`**: Create catalog item.
- **PUT `/api/v1/products/{project_id}/{product_id}`**: Update catalog item.
- **DELETE `/api/v1/products/{project_id}/{product_id}`**: Delete catalog item.

---

## 4. Error Mapping & Status Codes

| HTTP Status | Mobile Exception | User Presentation |
|---|---|---|
| `401 Unauthorized` | `AuthException` | Prompts session re-authentication or token refresh |
| `403 Forbidden` | `PermissionException` | "Access denied. You do not have permissions for this action." |
| `404 Not Found` | `NotFoundException` | Resource or project not found |
| `422 Unprocessable` | `ValidationException` | Field-level error messages displayed below inputs |
| `429 Rate Limited` | `RateLimitException` | "Too many requests. Please wait a moment." |
| `500+ Server Error` | `ServerException` | "Service temporarily unavailable. Please retry shortly." |
| Network Timeout | `NetworkException` | "Unable to reach Automind server. Check your connection." |
