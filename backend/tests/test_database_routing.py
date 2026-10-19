"""
Regression and verification tests for test database routing and isolation.
Validates that application engines, Alembic migrations, and image storage
can never accidentally route to development or production databases.
All tests execute purely in-memory without opening network sockets.
"""

from types import SimpleNamespace
import inspect
import pytest
from app.core.database_guard import (
    validate_test_database_isolation,
    resolve_alembic_database_url,
)
from app.core.image_storage_guard import validate_image_storage_isolation
from app.core.db_identity import PROD_SUPABASE_PROJECT_REF


def _build_test_routing_settings(**overrides):
    """Build mock settings specifically configured for isolated test routing."""
    config = {
        "is_production": False,
        "ENVIRONMENT": "development",
        "TESTING": True,
        "TESTING_MODE": False,
        "DATABASE_URL": "postgresql+asyncpg://aisales:devpass@localhost:5432/aisales_dev",
        "TEST_DATABASE_URL": "postgresql+asyncpg://aisales:testpass@localhost:5432/automind_test",
        "REQUIRE_TEST_DB_EXPLICIT_AUTHORIZATION": True,
        "APPROVED_TEST_DATABASE_URL": "postgresql+asyncpg://aisales:testpass@localhost:5432/automind_test",
        "ALLOWED_TEST_DATABASE_URLS": [],
        "ALLOWED_TEST_DATABASES": ["automind_test"],
        "IMAGE_STORAGE_DATABASE_URL": "postgresql+asyncpg://aisales:devpass@localhost:5432/automind_img_dev",
        "TEST_IMAGE_STORAGE_DATABASE_URL": "postgresql+asyncpg://aisales:testpass@localhost:5432/automind_img_test",
        "APPROVED_TEST_IMAGE_STORAGE_DATABASE_URL": "postgresql+asyncpg://aisales:testpass@localhost:5432/automind_img_test",
        "ALLOWED_TEST_IMAGE_STORAGE_DATABASE_URLS": [],
    }
    config.update(overrides)
    return SimpleNamespace(**config)


def test_application_url_routing_selects_test_database_url_not_dev_database_url():
    """Verify application engine in test mode routes to TEST_DATABASE_URL and not DATABASE_URL."""
    settings = _build_test_routing_settings()
    routed_url = validate_test_database_isolation(settings, is_test_active=True, test_reason="pytest")
    assert routed_url == settings.TEST_DATABASE_URL
    assert routed_url != settings.DATABASE_URL
    assert "automind_test" in routed_url
    assert "aisales_dev" not in routed_url


def test_env_development_url_cannot_override_test_database_url():
    """Verify development URL from .env cannot override or be selected as the test URL."""
    # When TEST_DATABASE_URL is missing, it must fail closed and never fall back to DATABASE_URL
    settings_missing_test = _build_test_routing_settings(TEST_DATABASE_URL="")
    with pytest.raises(RuntimeError, match="TEST_DATABASE_URL is not configured"):
        validate_test_database_isolation(settings_missing_test, is_test_active=True, test_reason="pytest")

    # When TEST_DATABASE_URL is mistakenly pointed to DATABASE_URL, it must fail closed
    settings_same = _build_test_routing_settings(
        TEST_DATABASE_URL="postgresql+asyncpg://aisales:devpass@localhost:5432/aisales_dev",
        APPROVED_TEST_DATABASE_URL="postgresql+asyncpg://aisales:devpass@localhost:5432/aisales_dev",
    )
    with pytest.raises(RuntimeError, match="matches development database name|resolves to the same host"):
        validate_test_database_isolation(settings_same, is_test_active=True, test_reason="pytest")


def test_alembic_online_migration_routes_strictly_to_test_database():
    """Verify Alembic online migrations route strictly to TEST_DATABASE_URL during tests."""
    settings = _build_test_routing_settings()
    alembic_url = resolve_alembic_database_url(
        settings_obj=settings,
        is_offline=False,
        is_test_active=True,
        test_reason="pytest",
    )
    assert alembic_url == settings.TEST_DATABASE_URL
    assert "automind_test" in alembic_url
    assert "aisales_dev" not in alembic_url


def test_image_storage_routes_strictly_to_test_image_storage_database():
    """Verify image storage routes strictly to TEST_IMAGE_STORAGE_DATABASE_URL."""
    settings = _build_test_routing_settings()
    img_url = validate_image_storage_isolation(settings, is_test_active=True, test_reason="pytest")
    assert img_url == settings.TEST_IMAGE_STORAGE_DATABASE_URL
    assert img_url != settings.IMAGE_STORAGE_DATABASE_URL
    assert "automind_img_test" in img_url
    assert "automind_img_dev" not in img_url


def test_missing_or_invalid_authorization_fails_closed_before_network():
    """Verify missing authorization flags or mismatched approval fail closed without network."""
    # Missing explicit authorization flag
    settings_no_auth = _build_test_routing_settings(REQUIRE_TEST_DB_EXPLICIT_AUTHORIZATION=False)
    with pytest.raises(RuntimeError, match="REQUIRE_TEST_DB_EXPLICIT_AUTHORIZATION must be True"):
        validate_test_database_isolation(settings_no_auth, is_test_active=True, test_reason="pytest")

    # Mismatched approved test URL (approved host/port with unapproved db name)
    settings_mismatch = _build_test_routing_settings(
        APPROVED_TEST_DATABASE_URL="postgresql+asyncpg://aisales:testpass@localhost:5432/other_db",
        ALLOWED_TEST_DATABASES=[],
    )
    with pytest.raises(RuntimeError, match="is not authorized|does not match any explicitly approved"):
        validate_test_database_isolation(settings_mismatch, is_test_active=True, test_reason="pytest")


def test_prod_supabase_target_rejected_across_primary_and_image_routing():
    """Verify any URL referencing the production Supabase project is rejected across all routing channels."""
    prod_url = f"postgresql+asyncpg://postgres:pass@db.{PROD_SUPABASE_PROJECT_REF}.supabase.co:5432/postgres"

    # Primary database routing rejection
    settings_prod_primary = _build_test_routing_settings(
        TEST_DATABASE_URL=prod_url,
        APPROVED_TEST_DATABASE_URL=prod_url,
    )
    with pytest.raises(RuntimeError, match=f"targets the production Supabase reference \\({PROD_SUPABASE_PROJECT_REF}\\)"):
        validate_test_database_isolation(settings_prod_primary, is_test_active=True, test_reason="pytest")

    # Image storage routing rejection
    settings_prod_img = _build_test_routing_settings(
        TEST_IMAGE_STORAGE_DATABASE_URL=prod_url,
        APPROVED_TEST_IMAGE_STORAGE_DATABASE_URL=prod_url,
    )
    with pytest.raises(RuntimeError, match=f"targets the production Supabase reference \\({PROD_SUPABASE_PROJECT_REF}\\)"):
        validate_image_storage_isolation(settings_prod_img, is_test_active=True, test_reason="pytest")


def test_destructive_teardown_is_tenant_scoped_in_webhook_security():
    """Verify that test_webhook_security.py teardown does not execute unscoped table deletions."""
    from pathlib import Path
    file_path = Path(__file__).parent / "test_webhook_security.py"
    with open(file_path, "r", encoding="utf-8") as f:
        teardown_src = f.read()

    # Must contain where filter on project_id and not delete the entire table
    assert ".where(Integration.project_id.in_(project_ids))" in teardown_src
    assert ".where(Project.id.in_(project_ids))" in teardown_src
    assert "await db.execute(delete(Project))\n" not in teardown_src
    assert "await db.execute(delete(Integration))\n" not in teardown_src
