"""
Migration governance policy guard.

Enforces production release governance rules regarding database schema migrations:
- Application startup must not automatically execute schema migrations in production.
- Production startup cannot enable automatic migrations merely by setting RUN_MIGRATIONS_ON_STARTUP=true.
- Build-time migrations against production databases are strictly prohibited.
- Production migrations require explicit execution via dedicated release steps or operator CLI commands.
- HTTP-triggered migrations are disabled in production environments.
"""

import os
import sys
from typing import Optional, Tuple


def normalize_environment(environment: Optional[str] = None) -> str:
    """
    Normalize environment strings to canonical names.
    Handles casing, whitespace, and standard aliases.
    """
    if environment is None:
        environment = os.getenv("ENVIRONMENT", "development")

    cleaned = environment.strip().lower()
    if not cleaned:
        return "development"

    if cleaned in ("prod", "production") or cleaned.startswith("prod"):
        return "production"
    if cleaned in ("stage", "staging") or cleaned.startswith("stag"):
        return "staging"
    if cleaned in ("dev", "development", "local"):
        return "development"
    if cleaned in ("test", "testing"):
        return "test"

    return cleaned


def evaluate_startup_migration_policy(
    environment: Optional[str] = None,
    run_flag: Optional[str] = None,
) -> Tuple[bool, str]:
    """
    Evaluate whether database migrations should execute during application startup.

    Parameters:
        environment: Target deployment environment name.
                     Defaults to the ENVIRONMENT environment variable if unset.
        run_flag: String value of RUN_MIGRATIONS_ON_STARTUP environment variable.

    Returns:
        Tuple of (is_authorized, reason_description).
    """
    env_canonical = normalize_environment(environment)

    if run_flag is None:
        run_flag = os.getenv("RUN_MIGRATIONS_ON_STARTUP", "")

    run_flag_normalized = run_flag.strip().lower()
    is_explicitly_authorized = run_flag_normalized in ("true", "1", "yes")
    is_explicitly_disabled = run_flag_normalized in ("false", "0", "no")

    # Strict Production Prohibition:
    # Production startup must never automatically run schema migrations.
    # The prohibition cannot be bypassed merely by setting RUN_MIGRATIONS_ON_STARTUP=true.
    if env_canonical == "production":
        if is_explicitly_authorized:
            return (
                False,
                "Automatic startup migrations are strictly prohibited in production by production governance policy. "
                "Setting RUN_MIGRATIONS_ON_STARTUP=true cannot bypass this prohibition. "
                "Execute migrations via authorized release pipeline or operator command: python -m alembic upgrade head."
            )
        return (
            False,
            "Automatic startup migrations are disabled in production by production governance policy. "
            "Execute migrations via authorized release pipeline or operator command: python -m alembic upgrade head."
        )

    # Staging Environment:
    # Disabled by default, but permits explicit opt-in for isolated staging verification.
    if env_canonical == "staging":
        if is_explicitly_authorized:
            return (
                True,
                "Explicit RUN_MIGRATIONS_ON_STARTUP authorization detected for staging environment."
            )
        return (
            False,
            "Automatic startup migrations are disabled by default in staging. "
            "To enable for staging, set RUN_MIGRATIONS_ON_STARTUP=true, or execute: python -m alembic upgrade head."
        )

    # Non-production environments (development, test, local)
    if is_explicitly_disabled:
        return (
            False,
            f"Startup migrations explicitly disabled via RUN_MIGRATIONS_ON_STARTUP={run_flag_normalized}."
        )

    return (
        True,
        f"Startup migrations enabled by default for non-production environment: {env_canonical}."
    )


def evaluate_build_migration_policy(
    environment: Optional[str] = None,
    build_flag: Optional[str] = None,
) -> Tuple[bool, str]:
    """
    Evaluate whether database migrations should execute during container/service build phase.

    Parameters:
        environment: Target deployment environment name.
        build_flag: String value of RUN_MIGRATIONS_ON_BUILD environment variable.

    Returns:
        Tuple of (is_authorized, reason_description).
    """
    env_canonical = normalize_environment(environment)

    if build_flag is None:
        build_flag = os.getenv("RUN_MIGRATIONS_ON_BUILD", "")

    build_flag_normalized = build_flag.strip().lower()
    is_explicitly_authorized = build_flag_normalized in ("true", "1", "yes")

    # Strict Production Build Prohibition:
    # Builds must produce immutable artifacts. Mutating remote production databases during build is prohibited.
    if env_canonical == "production":
        return (
            False,
            "Build-time database migrations are strictly prohibited in production. "
            "Build artifacts must be immutable; schema changes belong exclusively to the release/deployment phase."
        )

    if env_canonical == "staging":
        if is_explicitly_authorized:
            return (
                True,
                "Explicit RUN_MIGRATIONS_ON_BUILD authorization detected for staging build."
            )
        return (
            False,
            "Build-time database migrations are disabled in staging by default."
        )

    # Non-production (development, local, test)
    if is_explicitly_authorized:
        return (
            True,
            f"Build-time database migrations authorized for {env_canonical} build."
        )

    return (
        False,
        "Build-time database migrations skipped by default."
    )


def evaluate_http_migration_policy(
    is_production: Optional[bool] = None,
) -> Tuple[bool, str]:
    """
    Evaluate whether HTTP-triggered migrations (such as /migrate) are permitted.

    Parameters:
        is_production: Boolean flag indicating if current environment is production.

    Returns:
        Tuple of (is_authorized, reason_description).
    """
    if is_production is None:
        from app.core.config import settings
        is_production = settings.is_production

    if is_production:
        return (
            False,
            "Automated migrations via HTTP are disabled in production. "
            "Run migrations through authorized release pipeline or CLI."
        )

    return (
        True,
        "HTTP migration execution permitted for non-production environment."
    )


if __name__ == "__main__":
    authorized, reason = evaluate_startup_migration_policy()
    print(f"[{'AUTHORIZED' if authorized else 'DISABLED'}] {reason}")
    sys.exit(0 if authorized else 1)
