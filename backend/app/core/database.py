"""
Database connection and session management using SQLAlchemy 2.0 async.
Single database architecture (simplified).
"""

from typing import AsyncGenerator, Optional
import ssl
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from .config import settings

# ============================================================================
# DATABASE - Single unified database
# ============================================================================

# SSL configuration for Railway PostgreSQL
def get_connect_args(target_url: Optional[str] = None):
    """Get connection arguments with SSL support for Railway PostgreSQL."""
    connect_args = {}
    check_url = target_url or settings.DATABASE_URL
    
    # Railway internal network doesn't need SSL (already secure)
    # Only external Railway connections need SSL
    if settings.ENVIRONMENT in ["production", "staging"]:
        if "railway" in check_url.lower() and "railway.internal" not in check_url.lower():
            # External Railway connection - use SSL with proper verification
            ssl_context = ssl.create_default_context()
            connect_args["ssl"] = ssl_context
        elif "railway.internal" in check_url.lower():
            # Internal Railway connection - disable SSL (already secure private network)
            connect_args["ssl"] = False
        
    # Supabase/pgbouncer compatibility: Disable prepared statement caching
    # pgbouncer in transaction mode does not support prepared statements properly
    import uuid
    connect_args["statement_cache_size"] = 0
    connect_args["prepared_statement_cache_size"] = 0
    connect_args["prepared_statement_name_func"] = lambda: f"__asyncpg_{uuid.uuid4()}__"
    
    return connect_args

from .database_guard import resolve_active_database_url

active_database_url = resolve_active_database_url()

# Create async engine
engine = create_async_engine(
    active_database_url,
    echo=settings.DB_ECHO,
    # Always use NullPool when connecting to a remote PgBouncer! 
    # PgBouncer does the pooling, SQLAlchemy shouldn't pool the virtual connections.
    poolclass=NullPool,
    connect_args=get_connect_args(active_database_url),
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()

# ============================================================================
# Backward Compatibility Aliases
# ============================================================================

# For code that still references old dual-database names
SessionLocal = AsyncSessionLocal
AuthSessionLocal = AsyncSessionLocal
AppSessionLocal = AsyncSessionLocal
AuthBase = Base
AppBase = Base


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency to get database session.
    
    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Backward compatibility aliases
get_auth_db = get_db
get_app_db = get_db


async def init_db():
    """
    Initialize database by creating all tables.
    Use Alembic migrations in production instead.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Close database connections."""
    await engine.dispose()
