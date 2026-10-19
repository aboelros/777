"""
Database isolation guard and test environment validation.
Prevents automated tests from targeting development or production databases.
"""

import os
import sys
from typing import List, Optional, Tuple
from .config import settings
from .db_identity import (
    DatabaseIdentity,
    normalize_db_identity,
    are_same_physical_target,
    assert_not_production_target,
)


def detect_test_execution() -> Tuple[bool, str]:
    """
    Detect whether test execution is active across multiple indicators.
    Returns (is_active, indicator_reason).
    """
    if settings.TESTING:
        return True, "settings.TESTING is True"
    if settings.TESTING_MODE:
        return True, "settings.TESTING_MODE is True"
    env_testing = os.getenv("TESTING", "").strip().lower()
    if env_testing in ("true", "1", "yes"):
        return True, "TESTING environment variable is set"
    if "PYTEST_CURRENT_TEST" in os.environ:
        return True, "PYTEST_CURRENT_TEST environment variable is set"
    if "pytest" in sys.modules:
        return True, "'pytest' module is loaded in sys.modules"
    if any("pytest" in os.path.basename(arg).lower() for arg in sys.argv):
        return True, "pytest detected in command line arguments"
    return False, "Not in test mode"


def validate_test_database_isolation(
    settings_obj,
    is_test_active: bool,
    test_reason: str,
) -> str:
    """
    Validates that test execution targets a strictly authorized, isolated test database identity.
    Enforces all 8 fail-closed rejection boundaries.
    """
    # Guard 1 (Case 8): Test mode against production configuration
    if settings_obj.is_production:
        if is_test_active or settings_obj.TESTING or settings_obj.TESTING_MODE:
            raise RuntimeError(
                "FAIL CLOSED: Test mode is strictly prohibited in production environment."
            )
        return settings_obj.DATABASE_URL

    # Guard 2 (Case 7): Non-test execution safely returns DATABASE_URL
    if not is_test_active:
        return settings_obj.DATABASE_URL

    # Test mode is active: verify explicit test flags
    is_explicit_test_flag = settings_obj.TESTING or (os.getenv("TESTING", "").strip().lower() in ("true", "1", "yes"))
    if not is_explicit_test_flag:
        raise RuntimeError(
            f"FAIL CLOSED: Test execution detected ({test_reason}), but explicit test mode "
            "(TESTING=true) is not set in settings or environment. Halting to protect the development database."
        )

    # Guard 3 (Case 1): Test mode with no explicit test URL
    if not settings_obj.TEST_DATABASE_URL or not settings_obj.TEST_DATABASE_URL.strip():
        raise RuntimeError(
            "FAIL CLOSED: Test execution is active, but TEST_DATABASE_URL is not configured. "
            "Halting to protect the development database."
        )

    # Guard 4 (Case 2): Test mode with no explicit authorization flag
    if not settings_obj.REQUIRE_TEST_DB_EXPLICIT_AUTHORIZATION:
        raise RuntimeError(
            "FAIL CLOSED: REQUIRE_TEST_DB_EXPLICIT_AUTHORIZATION must be True to run tests. "
            "This ensures you have explicitly verified an isolated test environment."
        )

    # Collect approved test database identities
    approved_urls: List[str] = []
    if settings_obj.APPROVED_TEST_DATABASE_URL and settings_obj.APPROVED_TEST_DATABASE_URL.strip():
        approved_urls.append(settings_obj.APPROVED_TEST_DATABASE_URL.strip())
    if settings_obj.ALLOWED_TEST_DATABASE_URLS:
        for u in settings_obj.ALLOWED_TEST_DATABASE_URLS:
            if u and isinstance(u, str) and u.strip():
                approved_urls.append(u.strip())

    if not approved_urls:
        raise RuntimeError(
            "FAIL CLOSED: No approved test database identities configured "
            "(APPROVED_TEST_DATABASE_URL or ALLOWED_TEST_DATABASE_URLS required). "
            "Full-identity authorization is required before running tests."
        )

    # Guard 5 (Case 6): Parse and normalize identities (fails closed on malformed/ambiguous URLs)
    test_id = normalize_db_identity(settings_obj.TEST_DATABASE_URL, "TEST_DATABASE_URL")
    dev_id = normalize_db_identity(settings_obj.DATABASE_URL, "DATABASE_URL")
    approved_identities = [
        normalize_db_identity(u, "APPROVED_TEST_DATABASE_URL") for u in approved_urls
    ]

    # Explicit protection against targeting production Supabase reference
    assert_not_production_target(settings_obj.TEST_DATABASE_URL, test_id, "TEST_DATABASE_URL")
    for app_id, app_url in zip(approved_identities, approved_urls):
        assert_not_production_target(app_url, app_id, "Approved test target")

    # Guard 6 (Case 3): Test URL identical to development database
    if test_id.database == dev_id.database:
        raise RuntimeError(
            f"FAIL CLOSED: TEST_DATABASE_URL target database '{test_id.database}' matches "
            f"development database name '{dev_id.database}'. Halting to prevent data pollution or loss."
        )
    if are_same_physical_target(test_id, dev_id):
        raise RuntimeError(
            "FAIL CLOSED: TEST_DATABASE_URL resolves to the same host, port, and database as DATABASE_URL. "
            "Halting to protect the development database."
        )

    # Ensure development database was not erroneously authorized
    for app_id in approved_identities:
        if app_id.database == dev_id.database or are_same_physical_target(app_id, dev_id):
            raise RuntimeError(
                f"FAIL CLOSED: Approved test target ({app_id.sanitized_endpoint}) resolves to the "
                "development database target. The development database cannot be authorized."
            )

    # Protect development image storage database if configured
    if getattr(settings_obj, "IMAGE_STORAGE_DATABASE_URL", None):
        dev_img_id = normalize_db_identity(settings_obj.IMAGE_STORAGE_DATABASE_URL, "IMAGE_STORAGE_DATABASE_URL")
        if test_id.database == dev_img_id.database:
            raise RuntimeError(
                f"FAIL CLOSED: TEST_DATABASE_URL target database '{test_id.database}' matches "
                f"development image storage database name '{dev_img_id.database}'. Halting to protect the development database."
            )
        if are_same_physical_target(test_id, dev_img_id):
            raise RuntimeError(
                "FAIL CLOSED: TEST_DATABASE_URL resolves to the same host, port, and database as IMAGE_STORAGE_DATABASE_URL. "
                "Halting to protect the development database."
            )
        for app_id in approved_identities:
            if app_id.database == dev_img_id.database or are_same_physical_target(app_id, dev_img_id):
                raise RuntimeError(
                    f"FAIL CLOSED: Approved test target ({app_id.sanitized_endpoint}) resolves to the "
                    "development image storage database target. The development database cannot be authorized."
                )

    # Guard 7 (Cases 4 & 5): Full-identity match against approved identities
    matched = any(
        test_id.dialect == app_id.dialect
        and test_id.driver == app_id.driver
        and test_id.host == app_id.host
        and test_id.port == app_id.port
        and test_id.database == app_id.database
        and test_id.query_params == app_id.query_params
        for app_id in approved_identities
    )

    if not matched:
        db_match = any(app_id.database == test_id.database for app_id in approved_identities)
        host_port_match = any(app_id.host == test_id.host and app_id.port == test_id.port for app_id in approved_identities)

        if db_match:
            # Case 4: Same database name but unapproved host or port
            raise RuntimeError(
                f"FAIL CLOSED: Database name '{test_id.database}' matches approved target, but endpoint "
                f"'{test_id.host}:{test_id.port}' is not authorized. Halting before database initialization."
            )
        elif host_port_match:
            # Case 5: Unapproved database name even if host and port are approved
            raise RuntimeError(
                f"FAIL CLOSED: Host and port '{test_id.host}:{test_id.port}' match approved target, but database "
                f"'{test_id.database}' is not authorized. Halting before database initialization."
            )
        else:
            raise RuntimeError(
                f"FAIL CLOSED: TEST_DATABASE_URL identity ({test_id.sanitized_endpoint}) does not "
                "match any explicitly approved test database identity. Halting before database initialization."
            )

    # Optional secondary database name allowlist
    if settings_obj.ALLOWED_TEST_DATABASES:
        allowed_names = [d.lower().strip() for d in settings_obj.ALLOWED_TEST_DATABASES if d.strip()]
        if test_id.database not in allowed_names:
            raise RuntimeError(
                f"FAIL CLOSED: Target test database '{test_id.database}' is not in ALLOWED_TEST_DATABASES. "
                "Halting before database initialization."
            )

    return settings_obj.TEST_DATABASE_URL


def resolve_active_database_url(settings_obj=None) -> str:
    """
    Entry point invoked by database.py to determine and validate the active database URL.
    """
    if settings_obj is None:
        from .config import get_settings
        settings_obj = get_settings()
    is_test_active, test_reason = detect_test_execution()
    return validate_test_database_isolation(settings_obj, is_test_active, test_reason)


def resolve_alembic_database_url(
    settings_obj=None,
    is_offline: Optional[bool] = None,
    is_test_active: Optional[bool] = None,
    test_reason: Optional[str] = None,
) -> str:
    """
    Resolve and validate the active database URL for Alembic migrations.

    When running online (is_offline=False), routes strictly through
    validate_test_database_isolation() to prevent tests or unauthorized
    configurations from running migrations against development or production databases.
    When running offline (is_offline=True), provides a safe dialect URL for static
    SQL compilation without opening database connections.
    """
    if settings_obj is None:
        settings_obj = settings

    if is_offline is None:
        try:
            from alembic import context
            is_offline = context.is_offline_mode()
        except (AttributeError, NameError, ImportError):
            is_offline = False

    if is_offline:
        # Offline mode only requires a dialect string for SQL compilation.
        # It never opens a network connection or touches live databases.
        return settings_obj.DATABASE_URL

    if is_test_active is None:
        is_test_active, detected_reason = detect_test_execution()
        if test_reason is None:
            test_reason = detected_reason
    elif test_reason is None:
        test_reason = "Explicitly provided is_test_active flag"

    return validate_test_database_isolation(settings_obj, is_test_active, test_reason)
