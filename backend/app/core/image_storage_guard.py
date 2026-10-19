"""
Image storage database isolation guard.
Ensures dedicated image storage cannot target development or unapproved databases in tests.
Strictly decoupled from primary application database authorization.
"""

import os
from typing import List
from .config import settings
from .db_identity import (
    normalize_db_identity,
    are_same_physical_target,
    assert_not_production_target,
)
from .database_guard import detect_test_execution


def validate_image_storage_isolation(
    settings_obj,
    is_test_active: bool,
    test_reason: str,
) -> str:
    """
    Validates and resolves the dedicated image storage database URL.
    Ensures image storage cannot target development databases or unapproved targets in tests.
    """
    if settings_obj.is_production:
        if is_test_active or settings_obj.TESTING or settings_obj.TESTING_MODE:
            raise RuntimeError(
                "FAIL CLOSED: Test mode is strictly prohibited in production environment."
            )
        if not settings_obj.IMAGE_STORAGE_DATABASE_URL:
            raise ValueError("IMAGE_STORAGE_DATABASE_URL not configured")
        return settings_obj.IMAGE_STORAGE_DATABASE_URL

    if not is_test_active:
        if not settings_obj.IMAGE_STORAGE_DATABASE_URL:
            raise ValueError("IMAGE_STORAGE_DATABASE_URL not configured")
        return settings_obj.IMAGE_STORAGE_DATABASE_URL

    # In test mode:
    is_explicit_test_flag = settings_obj.TESTING or (os.getenv("TESTING", "").strip().lower() in ("true", "1", "yes"))
    if not is_explicit_test_flag:
        raise RuntimeError(
            f"FAIL CLOSED: Test execution detected ({test_reason}), but explicit test mode "
            "(TESTING=true) is not set. Halting to protect the database."
        )

    # In test mode, candidate URL must come explicitly from TEST_IMAGE_STORAGE_DATABASE_URL.
    # Never silently fall back to IMAGE_STORAGE_DATABASE_URL.
    if not settings_obj.TEST_IMAGE_STORAGE_DATABASE_URL or not settings_obj.TEST_IMAGE_STORAGE_DATABASE_URL.strip():
        raise RuntimeError(
            "FAIL CLOSED: Test execution is active, but TEST_IMAGE_STORAGE_DATABASE_URL is not configured. "
            "Halting to protect the database."
        )
    candidate_url = settings_obj.TEST_IMAGE_STORAGE_DATABASE_URL.strip()

    if not settings_obj.REQUIRE_TEST_DB_EXPLICIT_AUTHORIZATION:
        raise RuntimeError(
            "FAIL CLOSED: REQUIRE_TEST_DB_EXPLICIT_AUTHORIZATION must be True to run tests. "
            "Halting before image storage database initialization."
        )

    # Collect approved image storage identities strictly from dedicated image storage settings
    approved_urls: List[str] = []
    if getattr(settings_obj, "APPROVED_TEST_IMAGE_STORAGE_DATABASE_URL", None) and settings_obj.APPROVED_TEST_IMAGE_STORAGE_DATABASE_URL.strip():
        approved_urls.append(settings_obj.APPROVED_TEST_IMAGE_STORAGE_DATABASE_URL.strip())
    if getattr(settings_obj, "ALLOWED_TEST_IMAGE_STORAGE_DATABASE_URLS", None):
        for u in settings_obj.ALLOWED_TEST_IMAGE_STORAGE_DATABASE_URLS:
            if u and isinstance(u, str) and u.strip():
                approved_urls.append(u.strip())

    if not approved_urls:
        raise RuntimeError(
            "FAIL CLOSED: No approved test image database identities configured "
            "(APPROVED_TEST_IMAGE_STORAGE_DATABASE_URL or ALLOWED_TEST_IMAGE_STORAGE_DATABASE_URLS required). "
            "Full-identity authorization is required before initializing image storage in tests."
        )

    img_test_id = normalize_db_identity(candidate_url, "TEST_IMAGE_STORAGE_DATABASE_URL")
    dev_primary_id = normalize_db_identity(settings_obj.DATABASE_URL, "DATABASE_URL")
    dev_img_id = (
        normalize_db_identity(settings_obj.IMAGE_STORAGE_DATABASE_URL, "IMAGE_STORAGE_DATABASE_URL")
        if settings_obj.IMAGE_STORAGE_DATABASE_URL
        else None
    )
    approved_identities = [
        normalize_db_identity(u, "APPROVED_TEST_IMAGE_STORAGE_DATABASE_URL") for u in approved_urls
    ]

    # Explicit protection against targeting production Supabase reference
    assert_not_production_target(candidate_url, img_test_id, "TEST_IMAGE_STORAGE_DATABASE_URL")
    for app_id, app_url in zip(approved_identities, approved_urls):
        assert_not_production_target(app_url, app_id, "Approved test image target")

    # Reject if candidate matches development image storage database
    if dev_img_id:
        if img_test_id.database == dev_img_id.database:
            raise RuntimeError(
                f"FAIL CLOSED: TEST_IMAGE_STORAGE_DATABASE_URL target database '{img_test_id.database}' matches "
                f"development image storage database name '{dev_img_id.database}'. Halting to protect the development database."
            )
        if are_same_physical_target(img_test_id, dev_img_id):
            raise RuntimeError(
                "FAIL CLOSED: TEST_IMAGE_STORAGE_DATABASE_URL resolves to the same host, port, and database as IMAGE_STORAGE_DATABASE_URL. "
                "Halting to protect the development database."
            )

    # Reject if candidate matches primary development database
    if img_test_id.database == dev_primary_id.database:
        raise RuntimeError(
            f"FAIL CLOSED: TEST_IMAGE_STORAGE_DATABASE_URL target database '{img_test_id.database}' matches "
            f"primary development database name '{dev_primary_id.database}'. Halting to protect the development database."
        )
    if are_same_physical_target(img_test_id, dev_primary_id):
        raise RuntimeError(
            "FAIL CLOSED: TEST_IMAGE_STORAGE_DATABASE_URL resolves to the same host, port, and database as primary DATABASE_URL. "
            "Halting to protect the development database."
        )

    # Reject if any approved identity resolves to development databases
    for app_id in approved_identities:
        if dev_img_id and (app_id.database == dev_img_id.database or are_same_physical_target(app_id, dev_img_id)):
            raise RuntimeError(
                f"FAIL CLOSED: Approved test image target ({app_id.sanitized_endpoint}) resolves to the "
                "development image storage database target. The development database cannot be authorized."
            )
        if app_id.database == dev_primary_id.database or are_same_physical_target(app_id, dev_primary_id):
            raise RuntimeError(
                f"FAIL CLOSED: Approved test image target ({app_id.sanitized_endpoint}) resolves to the "
                "primary development database target. The development database cannot be authorized."
            )

    # Full-identity match against approved image identities
    matched = any(
        img_test_id.dialect == app_id.dialect
        and img_test_id.driver == app_id.driver
        and img_test_id.host == app_id.host
        and img_test_id.port == app_id.port
        and img_test_id.database == app_id.database
        and img_test_id.query_params == app_id.query_params
        for app_id in approved_identities
    )

    if not matched:
        db_match = any(app_id.database == img_test_id.database for app_id in approved_identities)
        host_port_match = any(app_id.host == img_test_id.host and app_id.port == img_test_id.port for app_id in approved_identities)
        if db_match:
            raise RuntimeError(
                f"FAIL CLOSED: Image storage target database '{img_test_id.database}' matches approved target, but endpoint "
                f"'{img_test_id.host}:{img_test_id.port}' is not authorized. Halting before database initialization."
            )
        elif host_port_match:
            raise RuntimeError(
                f"FAIL CLOSED: Image storage host and port '{img_test_id.host}:{img_test_id.port}' match approved target, but database "
                f"'{img_test_id.database}' is not authorized. Halting before database initialization."
            )
        else:
            raise RuntimeError(
                f"FAIL CLOSED: TEST_IMAGE_STORAGE_DATABASE_URL identity ({img_test_id.sanitized_endpoint}) does not "
                "match any explicitly approved test image database identity. Halting before database initialization."
            )

    return candidate_url


def resolve_image_storage_database_url(settings_obj=None) -> str:
    """
    Entry point invoked by PostgresStorageService to validate and resolve image storage URL.
    """
    if settings_obj is None:
        from .config import get_settings
        settings_obj = get_settings()
    is_test_active, test_reason = detect_test_execution()
    return validate_image_storage_isolation(settings_obj, is_test_active, test_reason)
