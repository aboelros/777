# AI Sales Commander — Project Overview

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white) ![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white) ![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white) ![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)

**AI Sales Commander** is a production-ready, enterprise-grade AI-powered sales automation platform that unifies e-commerce operations, multi-channel customer communication, and intelligent business analytics using Google Gemini AI. It transforms e-commerce businesses with AI automation that handles customer inquiries automatically, provides real-time business intelligence, unifies communication across WhatsApp, Telegram, Instagram, and Facebook, and integrates with platforms like Shopify.

## Architecture

```mermaid
flowchart TD
    subgraph Frontend [FRONTEND (React + Vite)]
        UI[Modern Dark UI & Real-time Updates]
    end

    subgraph Backend [BACKEND (FastAPI + Python 3.11)]
        API[RESTful API & WebSockets]
        Auth[JWT Auth & RBAC]
    end

    subgraph Data Layer
        DB[(PostgreSQL)]
        Cache[(Redis Cache)]
    end

    subgraph Background Processing
        Workers[Celery Workers]
    end

    subgraph AI Engine
        AI[Google Gemini AI]
    end

    subgraph Integrations [External Integrations]
        Shopify[Shopify]
        WhatsApp[WhatsApp]
        Telegram[Telegram]
        Meta[Meta / FB / IG]
    end

    Frontend <-->|HTTPS/WSS| Backend
    Backend <--> DB
    Backend <--> Cache
    Backend <--> Workers
    Backend <--> AI
    Backend <--> Integrations
    Workers <--> AI
    Workers <--> DB
```

## Tech Stack

| Category | Technologies | Description |
|---|---|---|
| **Backend** | FastAPI, Python 3.11, Pydantic, SQLAlchemy 2.0, Alembic | High-performance async framework handling REST APIs, WebSocket connections, data validation, and database interactions. |
| **Frontend** | React 18, Vite, TailwindCSS, TanStack Query, Zustand, Framer Motion | Modern dark theme UI with glassmorphism, responsive design, fast builds, and efficient state management. |
| **AI Engine** | Google Vertex AI (Gemini 1.5 Pro) | NLP, intent recognition, sentiment analysis, and autonomous function calling. |
| **Messaging** | Redis, Celery | Distributed task queue for asynchronous processing, message broking, and scheduling background jobs. |
| **Infrastructure** | PostgreSQL 15, Docker, Docker Compose, Railway/Render | Containerized deployment, scalable relational database storage, and cloud-ready infrastructure. |

## Project Structure

```text
ai-sales-commander/
├── backend/                      # Python FastAPI Backend
│   ├── app/
│   │   ├── main.py               # Application entry point
│   │   ├── core/                 # Config, security (JWT, bcrypt), DB connection
│   │   ├── api/v1/               # API Routes (auth, projects, integrations, etc.)
│   │   ├── models/               # Pydantic Schemas
│   │   ├── db/                   # SQLAlchemy Models
│   │   ├── services/             # Business Logic (Gemini client, Shopify, WhatsApp)
│   │   └── workers/              # Celery tasks and configuration
│   ├── alembic/                  # Database migrations
│   ├── scripts/                  # Utility scripts (e.g., generate_secret_key.py)
│   ├── tests/                    # Test suite (pytest)
│   ├── requirements.txt          # Python dependencies
│   └── Dockerfile                # Backend container
│
├── frontend/                     # React Frontend
│   ├── src/
│   │   ├── pages/                # Page components (Dashboard, Inbox, Auth, etc.)
│   │   ├── components/           # Reusable UI elements (GlassCard, Sidebar, etc.)
│   │   ├── lib/                  # Utilities and API client
│   │   └── store/                # Zustand state management
│   ├── package.json              # Node dependencies
│   ├── tailwind.config.js        # Tailwind CSS styling configuration
│   └── Dockerfile                # Frontend container
│
├── docker-compose.yml            # Multi-service orchestration
└── .github/workflows/            # GitHub Actions CI/CD pipelines
```

## How It Works

1. **Incoming Event**: A webhook arrives from an external platform (e.g., Shopify order update, WhatsApp message).
2. **Authentication & Routing**: The API Gateway (FastAPI) receives the webhook, verifies the HMAC signature, and routes it to the appropriate handler.
3. **Task Queue**: The event is handed off to the Redis/Celery queue for asynchronous processing so the API can respond quickly.
4. **Processing**: The Celery worker picks up the task and processes it.
5. **AI Interaction**: If the event requires intelligent handling (like a customer message), the worker calls the Google Gemini AI integration. The AI analyzes sentiment, intent, and context, deciding if it needs to trigger autonomous actions (e.g., fetch order details).
6. **Response / Action**: The AI formulates a response or updates the system state.
7. **Delivery**: The system dispatches the response back to the customer via the appropriate messaging integration or updates the local database.

## Multi-Tenancy

The platform is designed with a strict multi-tenant architecture to ensure complete data isolation across users. 
- **User Accounts**: Each user account can own multiple "Projects" (brands or stores).
- **Project Scoping**: Everything from integrations, orders, messages, and customers is linked to a specific `project_id`.
- **Database Level Isolation**: The `projects` table has an `owner_id` foreign key linking it to the `users` table. 
- **API Level Security**: Every API endpoint extracts the user's ID from the JWT token and appends a `WHERE owner_id = :user_id` clause (or equivalent) to database queries. This means a user can never access or modify data belonging to a project they do not own, ensuring enterprise-grade data security.

## Key Concepts

- **Projects**: The core organizational unit. A project represents a specific brand or store. It acts as the boundary for multi-tenant data.
- **Integrations**: Connections to external platforms tied to a project. These include Shopify for e-commerce and Meta/Telegram for messaging.
- **Customers**: Profiles representing individual end-users interacting with the project via messaging or e-commerce orders.
- **Messages**: Unified inbound and outbound communication threads across multiple channels (WhatsApp, Telegram, etc.) managed within a single inbox.
- **Orders**: Unified e-commerce data synchronized from platforms like Shopify, tracking the full lifecycle and fulfillment status.
- **AI Bot**: The Google Gemini-powered assistant configured per project. It features autonomous action execution (function calling) to handle tasks like updating orders or sending responses automatically.

## Quick Start

Get up and running locally with the test account (Email: `1111111@test.com`, Password: `1111111`).

```bash
# 1. Run the all-in-one startup script (handles .env creation, starting containers, and DB seeding)
run.bat

# 2. Open the frontend in your browser
http://localhost:3000

# 3. Access API docs to explore endpoints
http://localhost:8000/docs
```

## Contributing

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

### Reporting Bugs
1. Check if the bug has already been reported in Issues.
2. If not, create a new issue with a clear title/description, steps to reproduce, expected vs actual behavior, and environment details.

### Pull Requests
1. Fork the repository and clone it locally.
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes following the existing code style (PEP 8 for Python, ES6+/Airbnb for React).
4. Test your changes (`pytest` for backend, `npm test` for frontend).
5. Commit using conventional commits (e.g., `feat: add amazing feature`).
6. Push to your fork and open a Pull Request.

### Code Style
- **Python (Backend)**: Follow PEP 8, use `black` for formatting, `ruff` for linting, add type hints and docstrings.
- **JavaScript/React (Frontend)**: Use ES6+, functional components, hooks, and JSDoc comments for complex logic.

## Changelog

### [1.0.0] - 2025-01-12

**Added**
- 🎉 Initial release of AI Sales Commander
- ✨ FastAPI backend with async support
- 🤖 Google Gemini AI integration with function-calling
- 🔐 JWT authentication with refresh token rotation
- 📊 Multi-tenant project management
- 🔌 Integration framework for external platforms
- 🛍️ Shopify integration service
- 💬 WhatsApp Business API integration
- 📱 Telegram bot integration
- 📦 Order management and tracking
- 💬 Unified message inbox
- 📈 Analytics and reporting system
- 👷 Background workers with Celery
- 🎨 React frontend with dark glass-morphism theme
- 📱 Responsive dashboard with real-time stats
- 🤖 AI Assistant chat interface
- 🔄 WebSocket support for real-time updates
- 🐳 Docker and docker-compose configuration
- 📚 Comprehensive API documentation
- 🔒 Security guidelines and best practices
- 🧪 Testing infrastructure setup
- 🚀 CI/CD pipeline with GitHub Actions

**Security**
- Implemented JWT token authentication
- Added CORS protection
- Rate limiting on API endpoints
- Input validation with Pydantic
- SQL injection prevention
- HMAC verification for webhooks
- Sensitive data masking in logs
