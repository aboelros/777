"""Alembic environment configuration for async migrations."""

from logging.config import fileConfig
from typing import Optional
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
import asyncio

# Import your models here
from app.core.database import Base
from app.domains.auth.models import *
from app.domains.projects.models import *
from app.domains.integrations.models import *
from app.domains.orders.models import *
from app.domains.messages.models import *
from app.domains.ai.models import *
from app.domains.analytics.models import *
from app.domains.products.models import *
from app.domains.social.models import *
from app.domains.customers.models import *
from app.domains.billing.models import *
from app.domains.crm.models import *

from app.core.config import settings
from app.core.database_guard import resolve_alembic_database_url


def get_target_database_url(
    settings_obj=None,
    is_offline: Optional[bool] = None,
    is_test_active: Optional[bool] = None,
    test_reason: Optional[str] = None,
) -> str:
    """Resolve active database URL for Alembic migrations, enforcing isolation guards."""
    return resolve_alembic_database_url(
        settings_obj=settings_obj,
        is_offline=is_offline,
        is_test_active=is_test_active,
        test_reason=test_reason,
    )


# this is the Alembic Config object
try:
    config = context.config
except (AttributeError, NameError):
    config = None

if config is not None:
    # Resolve target URL enforcing database isolation guard
    target_database_url = get_target_database_url()

    # Override sqlalchemy.url with setting from environment
    # Escape % chars because configparser treats % as interpolation syntax (e.g. %40 → crash)
    config.set_main_option("sqlalchemy.url", target_database_url.replace("%", "%%"))

    # Interpret the config file for Python logging
    if config.config_file_name is not None:
        fileConfig(config.config_file_name)

# Model metadata for 'autogenerate' support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    
    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations with the given connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in async mode."""
    import ssl
    import uuid
    
    configuration = config.get_section(config.config_ini_section)
    target_url = get_target_database_url(is_offline=False)
    configuration["sqlalchemy.url"] = target_url
    
    # statement_cache_size=0 is REQUIRED for Supabase PgBouncer transaction pooler (port 6543)
    # Without this, asyncpg throws DuplicatePreparedStatementError
    connect_args = {
        "statement_cache_size": 0,
        "prepared_statement_name_func": lambda: f"__asyncpg_{uuid.uuid4()}__",
    }

    # SSL configuration for Railway PostgreSQL (legacy, kept for compatibility)
    if settings.ENVIRONMENT in ["production", "staging"]:
        if "railway" in target_url.lower() and "railway.internal" not in target_url.lower():
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            connect_args["ssl"] = ssl_context
    
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args=connect_args,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if config is not None:
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        run_migrations_online()
