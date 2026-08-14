"""
Main FastAPI application entry point.
Configures middleware, routes, and lifecycle events.
"""

from uuid import UUID
from fastapi import FastAPI, Request, status, Depends, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
import time
import structlog




from app.core.config import settings
from app.core.database import init_db, close_db, AsyncSessionLocal, get_db
from app.core.seed import seed_database
from app.core.error_handlers import setup_error_handlers
from app.api.v1 import (
    admin, auth, assistant, bot_training, chat_bot, deals, drip_campaigns,
    enhanced_bot, integrations, knowledge, messages, order_management,
    orders, payments_invoicing, photos, products, projects, reports,
    social_media, storage, subscriptions, webhooks
)

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    print("DEBUG: Lifespan running (restored)")
    # Startup
    # Initialize startup checks
    try:
        if settings.GEMINI_API_KEY:
             logger.info("✅ Gemini API Key configured for AI, Vision, and Voice")
        else:
             logger.warning("⚠️ GEMINI_API_KEY is missing - Intelligence features will be limited")

    except Exception as e:
        logger.warning("Startup check failed", error=str(e))
    # Initialize Groq client to verify key at startup

    try:
        from app.services.cache_service import cache
        await cache.connect()
    except Exception as e:
        logger.warning("Cache service initialization failed", error=str(e))

    # Check available Gemini models
    try:
        import google.generativeai as genai
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            # List models that support generateContent
            models = list(genai.list_models())
            available_models = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
            print(f"DEBUG: Available Gemini Models: {available_models}")
            logger.info("Available Gemini Models", models=available_models)
        else:
            print("DEBUG: GEMINI_API_KEY is missing")
    except Exception as e:
        print(f"DEBUG: Failed to list Gemini models: {e}")
        logger.error("Failed to list Gemini models", error=str(e))
        
    logger.info("✅ Database ready - migrations run by start.sh")
    
    # Start background tasks
    from app.services.background_tasks import start_background_tasks
    await start_background_tasks()
    logger.info("✅ Background tasks started (order follow-ups)")
    
    # Log all registered routes for debugging
    logger.info("🗺️ Registered Routes:")
    for route in app.routes:
        if hasattr(route, "methods"):
            logger.info(f"Route: {route.path}", methods=list(route.methods))
    
    yield
    
    # Shutdown
    logger.info("Application shutting down")
    await close_db()


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered sales automation and customer communication platform",
    version=settings.API_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Setup global error handlers
setup_error_handlers(app)


# ============================================================================
# Middleware & Security Configuration
# ============================================================================
# FastAPI Middleware Order (Stack): Last Added is Outermost (runs first for Request)

from app.core.rate_limit import limiter, _rate_limit_exceeded_handler, RateLimitExceeded, SlowAPIMiddleware
from app.core.security import require_role

# 1. Rate Limiting (Innermost - closest to handler)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# 2. CORS Configuration (Middle)
# Explicitly allow production and development origins to ensure credentials (cookies) work
cors_origins = [
    "https://777-self.vercel.app",
    "https://frontend-beryl-eta-37.vercel.app",
    "https://aisalescommander.com",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:5174",
]

# Merge with settings.CORS_ORIGINS if provided
if settings.CORS_ORIGINS:
    for origin in settings.CORS_ORIGINS:
        if origin and origin != "*" and origin not in cors_origins:
            cors_origins.append(origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Process-Time"]
)

import uuid
from starlette.middleware.base import BaseHTTPMiddleware

class RequestContextMiddleware(BaseHTTPMiddleware):
    """Binds a unique request ID to the structlog context."""
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            path=request.url.path,
            method=request.method
        )
        
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        response.headers["X-Request-ID"] = request_id
        
        logger.info(
            "request_completed",
            status_code=response.status_code,
            process_time_ms=round(process_time * 1000, 2)
        )
        
        structlog.contextvars.clear_contextvars()
        return response

app.add_middleware(RequestContextMiddleware)

# 3. Security Headers (Manual Helmet-equivalent)
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses (CSP, HSTS, etc.)"""
    response = await call_next(request)
    
    # Content Security Policy (Strict)
    # Nonces should be used for inline scripts in production; for now, disallow unsafe-inline
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "img-src 'self' data: https:; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "connect-src 'self' https://aisalescommander.com https://graph.facebook.com https://graph.instagram.com; "
        "frame-ancestors 'none';"
    )
    
    # Strict Transport Security (HSTS)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=(), payment=()"
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
    
    return response

# 4. Request Logging & Process Time (Outermost - runs first for request)
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add request processing time header."""
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.3f}s"
        return response
    except Exception as e:
        logger.error("Request failed", error=str(e), path=request.url.path)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )


# ============================================================================
# Exception Handlers
# ============================================================================
# Note: All exception handlers are registered in setup_error_handlers(app) above
# See app/core/error_handlers.py for the actual handler implementations


# ============================================================================
# Routes
# ============================================================================

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - health check."""
    return {
        "status": "online",
        "app": settings.APP_NAME,
        "version": settings.API_VERSION,
        "environment": settings.ENVIRONMENT
    }


@app.get("/health", tags=["Health"])
@limiter.exempt
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow()}


@app.get("/health/db", tags=["Health"])
@limiter.exempt
async def database_health_check(db: AsyncSession = Depends(get_db)):
    """Database health check endpoint."""
    try:
        # Simple query to test database connection
        from sqlalchemy import text
        result = await db.execute(text("SELECT 1"))
        result.scalar()
        return {
            "status": "healthy", 
            "database": "connected",
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        return {
            "status": "unhealthy", 
            "database": "disconnected", 
            "error": str(e),
            "timestamp": datetime.utcnow()
        }



@app.get("/debug/config", tags=["Debug"])
async def debug_config(_: dict = Depends(require_role("admin"))):
    """Debug endpoint to check configuration."""
    db_host = "unknown"
    if settings.DATABASE_URL and "@" in settings.DATABASE_URL:
        try:
            db_host = settings.DATABASE_URL.split("@")[1].split("/")[0]
        except:
            db_host = "parse_error"
    
    return {
        "environment": settings.ENVIRONMENT,
        "cors_origins": settings.CORS_ORIGINS,
        "testing_mode": settings.TESTING_MODE,
        "has_secret_key": bool(settings.SECRET_KEY),
        "has_database_url": bool(settings.DATABASE_URL),
        "db_host": db_host,
        "db_driver": "asyncpg" if "asyncpg" in settings.DATABASE_URL else "unknown"
    }


@app.get("/check-enums", tags=["Debug"])
async def check_enums(_: dict = Depends(require_role("admin"))):
    """
    Check valid ENUM values for role and subscription fields.
    Shows what values are actually allowed in the database.
    """
    from sqlalchemy import text
    try:
        async with AsyncSessionLocal() as session:
            # Get ENUM types and their values
            result = await session.execute(text("""
                SELECT t.typname, e.enumlabel
                FROM pg_type t 
                JOIN pg_enum e ON t.oid = e.enumtypid  
                WHERE t.typname IN ('userrole', 'subscriptiontier', 'subscriptionstatus')
                ORDER BY t.typname, e.enumsortorder
            """))
            enums = result.fetchall()
            
            # Group by type
            enum_dict = {}
            for type_name, value in enums:
                if type_name not in enum_dict:
                    enum_dict[type_name] = []
                enum_dict[type_name].append(value)
            
            return {
                "success": True,
                "enums": enum_dict,
                "valid_roles": enum_dict.get('userrole', ['ADMIN', 'USER', 'MANAGER']),
                "valid_subscription_tiers": enum_dict.get('subscriptiontier', ['FREE', 'BASIC', 'PRO']),
                "valid_subscription_statuses": enum_dict.get('subscriptionstatus', ['ACTIVE', 'INACTIVE'])
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Could not fetch ENUM values. Using defaults.",
            "defaults": {
                "valid_roles": ["ADMIN", "USER", "MANAGER"],
                "valid_subscription_tiers": ["FREE", "BASIC", "PRO", "ENTERPRISE"],
                "valid_subscription_statuses": ["ACTIVE", "INACTIVE", "CANCELLED"]
            }
        }


@app.get("/hash-password", tags=["Debug"])
async def hash_password(password: str, _: dict = Depends(require_role("admin"))):
    """
    Generate a bcrypt hash for a password.
    Use this to manually create users in the database.
    
    Example: /hash-password?password=MyPassword123
    """
    from app.core.security import get_password_hash
    
    if not password or len(password) < 8:
        return {
            "error": "Password must be at least 8 characters"
        }
    
    password_hash = get_password_hash(password)
    
    return {
        "password": password,
        "password_hash": password_hash,
        "instructions": "Use the SQL below in Railway Database → Data tab",
        "sql_example": f"""
-- Copy and modify this SQL to insert user:
INSERT INTO users (id, email, password_hash, name, role, is_active, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    'your@email.com',
    '{password_hash}',
    'Your Name',
    'ADMIN',
    true,
    NOW(),
    NOW()
);
        """
    }


@app.get("/check-schema", tags=["Debug"])
async def check_schema(_: dict = Depends(require_role("admin"))):
    """
    Check if users table has the required columns.
    """
    from sqlalchemy import text
    try:
        async with AsyncSessionLocal() as session:
            # Get column names from users table
            result = await session.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'users'
                ORDER BY ordinal_position
            """))
            columns = result.fetchall()
            
            column_list = [{"name": col[0], "type": col[1]} for col in columns]
            has_subscription_tier = any(col[0] == 'subscription_tier' for col in columns)
            
            return {
                "success": True,
                "total_columns": len(columns),
                "has_subscription_tier": has_subscription_tier,
                "columns": column_list
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.get("/migrate", tags=["Debug"])
async def run_migrations(_: dict = Depends(require_role("admin"))):
    """
    Manually trigger database migrations.
    Use this if migrations didn't run automatically.
    """
    import subprocess
    import os
    try:
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode,
            "current_dir": os.getcwd(),
            "message": "Migrations completed" if result.returncode == 0 else "Migrations failed"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "current_dir": os.getcwd()
        }


@app.get("/seed-direct", tags=["Debug"])
async def seed_direct(_: dict = Depends(require_role("admin"))):
    """
    Seed database using direct SQL (bypasses ORM).
    Creates: test@aisales.local / AiSales2024!Demo
    """
    from sqlalchemy import text
    from app.core.security import get_password_hash
    import uuid
    from datetime import datetime
    
    try:
        async with AsyncSessionLocal() as session:
            # Check if user exists
            check = await session.execute(
                text("SELECT id FROM users WHERE email = :email"),
                {"email": "test@aisales.local"}
            )
            existing = check.fetchone()
            
            if existing:
                return {
                    "success": True,
                    "message": "Account already exists",
                    "credentials": {
                        "email": "test@aisales.local",
                        "password": "AiSales2024!Demo"
                    }
                }
            
            # Create user with direct SQL
            user_id = str(uuid.uuid4())
            password_hash = get_password_hash("AiSales2024!Demo")
            now = datetime.utcnow()
            
            await session.execute(text("""
                INSERT INTO users (
                    id, email, password_hash, name, role, is_active, 
                    created_at, updated_at
                )
                VALUES (
                    :id, :email, :password_hash, :name, :role, :is_active,
                    :created_at, :updated_at
                )
            """), {
                "id": user_id,
                "email": "test@aisales.local",
                "password_hash": password_hash,
                "name": "Test User",
                "role": "admin",
                "is_active": True,
                "created_at": now,
                "updated_at": now
            })
            
            await session.commit()
            
            return {
                "success": True,
                "message": "Test account created successfully (direct SQL)",
                "credentials": {
                    "email": "test@aisales.local",
                    "password": "AiSales2024!Demo"
                }
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.get("/seed", tags=["Debug"])
async def seed_test_account(_: dict = Depends(require_role("admin"))):
    """
    Seed database with test account.
    Creates: test@aisales.local / AiSales2024!Demo
    Can be called by simply visiting the URL in browser.
    
    IMPORTANT: Run /migrate endpoint first if you get schema errors!
    """
    try:
        async with AsyncSessionLocal() as session:
            await seed_database(session)
        return {
            "success": True,
            "message": "Test account created successfully",
            "credentials": {
                "email": "test@aisales.local",
                "password": "AiSales2024!Demo"
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Database schema error - try /seed-direct endpoint instead"
        }


# WebSocket Endpoint
@app.websocket("/ws/{project_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: UUID):
    from app.core.websockets import manager
    await manager.connect(websocket, project_id)
    try:
        while True:
            # Listen for messages to keep the connection alive
            await websocket.receive_text()
    except Exception:
        # Handle disconnects properly
        manager.disconnect(websocket, project_id)


# Include API v1 routes
app.include_router(admin.router, prefix=f"/api/{settings.API_VERSION}/admin", tags=["Administration"])
app.include_router(auth.router, prefix=f"/api/{settings.API_VERSION}/auth", tags=["Authentication"])
app.include_router(projects.router, prefix=f"/api/{settings.API_VERSION}/projects", tags=["Projects"])
app.include_router(integrations.router, prefix=f"/api/{settings.API_VERSION}/integrations", tags=["Integrations"])
app.include_router(orders.router, prefix=f"/api/{settings.API_VERSION}/orders", tags=["Orders"])
app.include_router(messages.router, prefix=f"/api/{settings.API_VERSION}/messages", tags=["Messages"])
app.include_router(assistant.router, prefix=f"/api/{settings.API_VERSION}/assistant", tags=["AI Assistant"])
app.include_router(reports.router, prefix=f"/api/{settings.API_VERSION}/reports", tags=["Reports"])
app.include_router(chat_bot.router, prefix=f"/api/{settings.API_VERSION}/chat-bot", tags=["Chat Bot"])
app.include_router(products.router, prefix=f"/api/{settings.API_VERSION}/products", tags=["Products"])
app.include_router(bot_training.router, prefix=f"/api/{settings.API_VERSION}/bot-training", tags=["Bot Training"])
app.include_router(social_media.router, prefix=f"/api/{settings.API_VERSION}/social", tags=["Social Media"])
app.include_router(enhanced_bot.router, prefix=f"/api/{settings.API_VERSION}/enhanced-bot", tags=["Enhanced Bot"])
app.include_router(order_management.router, prefix=f"/api/{settings.API_VERSION}/order-management", tags=["Order Management"])
app.include_router(subscriptions.router, prefix=f"/api/{settings.API_VERSION}/subscriptions", tags=["Subscriptions"])
app.include_router(webhooks.router, prefix=f"/api/{settings.API_VERSION}/webhooks", tags=["Webhooks"])
app.include_router(photos.router, prefix=f"/api/{settings.API_VERSION}/projects", tags=["Photos"])
app.include_router(storage.router, prefix=f"/api/{settings.API_VERSION}/storage", tags=["Storage"])
app.include_router(knowledge.router, prefix=f"/api/{settings.API_VERSION}/knowledge", tags=["Knowledge Base"])
app.include_router(payments_invoicing.router, prefix=f"/api/{settings.API_VERSION}/payments", tags=["Payments & Invoicing"])
app.include_router(deals.router, prefix=f"/api/{settings.API_VERSION}/deals", tags=["Sales Pipeline"])
app.include_router(drip_campaigns.router, prefix=f"/api/{settings.API_VERSION}/drip-campaigns", tags=["Drip Campaigns"])


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
