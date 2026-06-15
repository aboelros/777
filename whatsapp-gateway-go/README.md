# WhatsApp Gateway (Whatsmeow)

Go-based WhatsApp gateway using the whatsmeow library for better reliability and stability.

## Features

- ✅ QR code generation
- ✅ Session management
- ✅ Message sending
- ✅ Session persistence (SQLite)
- ✅ REST API compatible with existing backend

## API Endpoints

### Create Session
```
POST /sessions
{
  "session_id": "unique-id",
  "metadata": {}
}
```

### Get Session Status
```
GET /sessions/:sessionId/status
```

### Close Session
```
POST /sessions/:sessionId/close
```

### Send Message
```
POST /sessions/:sessionId/send
{
  "to": "1234567890",
  "message": "Hello!"
}
```

## Running Locally

```bash
go mod download
go run main.go
```

## Building

```bash
docker build -t whatsapp-gateway-go .
docker run -p 8080:8080 whatsapp-gateway-go
```

## Environment Variables

- `PORT` - Server port (default: 8080)

## Deployment

Deploy to Railway using the Dockerfile. The service will automatically build and run.
