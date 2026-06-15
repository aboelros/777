# WhatsApp Baileys Gateway

A production-ready WhatsApp gateway using Baileys library for QR code authentication and message handling.

## Features

- ✅ QR Code authentication (no Business API required)
- ✅ Session management with persistent storage
- ✅ Send and receive messages
- ✅ Webhook support for incoming messages
- ✅ RESTful API
- ✅ Docker support
- ✅ API key authentication

## Quick Start

### 1. Installation

```bash
cd whatsapp-gateway
npm install
```

### 2. Configuration

Copy the environment template:

```bash
cp .env.example .env
```

Edit `.env` and set your configuration:

```env
PORT=3000
API_KEY=your-secret-api-key-change-this
CALLBACK_SECRET=your-callback-secret-change-this
BACKEND_URL=http://localhost:8000
SESSION_DIR=./sessions
LOG_LEVEL=info
```

### 3. Run the Server

**Development mode:**
```bash
npm run dev
```

**Production mode:**
```bash
npm start
```

**Using Docker:**
```bash
docker-compose up -d
```

## API Documentation

### Authentication

All API requests require an API key in the Authorization header:

```
Authorization: Bearer your-api-key
```

### Endpoints

#### Create Session
```http
POST /sessions
Content-Type: application/json
Authorization: Bearer your-api-key

{
  "project_id": "uuid",
  "integration_id": "uuid",
  "metadata": {
    "phone_number": "1234567890"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "session_id": "uuid",
  "status": "qr_ready",
  "qr_code": "data:image/png;base64,...",
  "created_at": "2024-01-01T00:00:00.000Z"
}
```

#### Get Session Status
```http
GET /sessions/{sessionId}
Authorization: Bearer your-api-key
```

**Response:**
```json
{
  "status": "success",
  "status": "connected",
  "qr_code": null,
  "created_at": "2024-01-01T00:00:00.000Z",
  "last_activity": "2024-01-01T00:00:00.000Z"
}
```

#### Send Message
```http
POST /sessions/{sessionId}/messages
Content-Type: application/json
Authorization: Bearer your-api-key

{
  "to": "1234567890",
  "message": "Hello from AI Sales Commander!",
  "message_type": "text"
}
```

**Response:**
```json
{
  "status": "success",
  "message_id": "msg-id",
  "status": "sent",
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

#### Close Session
```http
POST /sessions/{sessionId}/close
Authorization: Bearer your-api-key
```

**Response:**
```json
{
  "status": "success",
  "status": "closed",
  "session_id": "uuid"
}
```

#### Get All Sessions
```http
GET /sessions
Authorization: Bearer your-api-key
```

**Response:**
```json
{
  "status": "success",
  "sessions": [...],
  "count": 1
}
```

#### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2024-01-01T00:00:00.000Z",
  "sessions": 1
}
```

## Integration with Backend

### 1. Update Backend Environment

Add these variables to your backend `.env`:

```env
WHATSAPP_BAILEYS_URL=http://localhost:3000
WHATSAPP_BAILEYS_API_KEY=your-secret-api-key-change-this
WHATSAPP_GATEWAY_CALLBACK_SECRET=your-callback-secret-change-this
```

### 2. Webhook Configuration

The gateway will send incoming messages to:
```
POST {BACKEND_URL}/api/v1/webhooks/whatsapp
```

Make sure your backend has this webhook endpoint configured.

## Usage Flow

1. **Create Integration**: User creates WhatsApp integration in backend
2. **Generate QR**: Backend calls `POST /sessions` to create session
3. **Scan QR**: User scans QR code with WhatsApp mobile app
4. **Connected**: Session status changes to "connected"
5. **Send Messages**: Backend can now send messages via the session
6. **Receive Messages**: Gateway forwards incoming messages to backend webhook

## Session Management

Sessions are stored in the `sessions/` directory. Each session has its own folder with authentication data.

**Important:** 
- Keep the `sessions/` directory backed up
- Don't delete session folders while sessions are active
- Sessions persist across server restarts

## Troubleshooting

### QR Code Not Generating
- Check that the session doesn't already exist
- Ensure WhatsApp Web is not already connected on another device
- Try creating a new session with a different ID

### Messages Not Sending
- Verify session status is "connected"
- Check that phone number format is correct (no + or spaces)
- Ensure the number is registered on WhatsApp

### Webhook Not Received
- Verify `BACKEND_URL` is set correctly
- Check that backend webhook endpoint exists
- Review gateway logs for webhook errors

## Production Deployment

### Deploy to Railway (Recommended)

Railway provides easy deployment with automatic HTTPS and persistent storage.

**Quick Deploy:**
1. Push code to GitHub
2. Connect repository to Railway
3. Add environment variables
4. Add volume at `/app/sessions` (1GB)
5. Deploy!

📖 **See [RAILWAY.md](RAILWAY.md) for complete Railway deployment guide**

### Using Docker

1. Build the image:
```bash
docker build -t whatsapp-gateway .
```

2. Run with docker-compose:
```bash
docker-compose up -d
```

3. View logs:
```bash
docker-compose logs -f
```

### Security Recommendations

1. **Change default API keys** in production
2. **Use HTTPS** for all API calls
3. **Restrict network access** to trusted IPs
4. **Backup sessions directory** regularly
5. **Monitor logs** for suspicious activity

## License

MIT
