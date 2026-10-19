"""
Tests for Read-Only Staging Preflight Inspection Tool.
Verifies fail-closed environment validation, production rejection,
credential redaction, and accurate read-only schema reporting.
"""

import os
import pytest
from app.core.staging_preflight import (
    validate_preflight_environment,
    inspect_staging_database,
    format_preflight_report
)

LOCAL_STAGING_TEST_URL = "postgresql+asyncpg://postgres:postgres@localhost:5434/automind_staging"


def test_preflight_fails_without_staging_env(monkeypatch):
    """Refuses execution if ENVIRONMENT is not 'staging'."""
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.setenv("CONFIRM_READONLY_STAGING_PREFLIGHT", "true")
    monkeypatch.setenv("STAGING_DATABASE_URL", LOCAL_STAGING_TEST_URL)

    with pytest.raises(RuntimeError, match="ENVIRONMENT must be explicitly set to 'staging'"):
        validate_preflight_environment()


def test_preflight_fails_without_operator_confirmation(monkeypatch):
    """Refuses execution if CONFIRM_READONLY_STAGING_PREFLIGHT is not 'true'."""
    monkeypatch.setenv("ENVIRONMENT", "staging")
    monkeypatch.delenv("CONFIRM_READONLY_STAGING_PREFLIGHT", raising=False)
    monkeypatch.setenv("STAGING_DATABASE_URL", LOCAL_STAGING_TEST_URL)

    with pytest.raises(RuntimeError, match="CONFIRM_READONLY_STAGING_PREFLIGHT must be explicitly set to 'true'"):
        validate_preflight_environment()


def test_preflight_fails_on_missing_url(monkeypatch):
    """Refuses execution if STAGING_DATABASE_URL is missing or empty."""
    monkeypatch.setenv("ENVIRONMENT", "staging")
    monkeypatch.setenv("CONFIRM_READONLY_STAGING_PREFLIGHT", "true")
    monkeypatch.delenv("STAGING_DATABASE_URL", raising=False)

    with pytest.raises(RuntimeError, match="STAGING_DATABASE_URL is missing or empty"):
        validate_preflight_environment()


def test_preflight_fails_closed_on_production_url(monkeypatch):
    """Strictly refuses to run if URL points to known production Supabase project."""
    monkeypatch.setenv("ENVIRONMENT", "staging")
    monkeypatch.setenv("CONFIRM_READONLY_STAGING_PREFLIGHT", "true")
    prod_url = "postgresql+asyncpg://user:pass@aws-0-eu-central-1.pooler.supabase.com:6543/ccejhzadokkjssjiwmxt"
    monkeypatch.setenv("STAGING_DATABASE_URL", prod_url)

    with pytest.raises(RuntimeError, match="Target matches production Supabase reference"):
        validate_preflight_environment()


@pytest.mark.asyncio
async def test_preflight_read_only_inspection_success(monkeypatch):
    """Connects in read-only mode to local test DB and generates accurate report with redacted credentials."""
    monkeypatch.setenv("ENVIRONMENT", "staging")
    monkeypatch.setenv("CONFIRM_READONLY_STAGING_PREFLIGHT", "true")
    monkeypatch.setenv("STAGING_DATABASE_URL", LOCAL_STAGING_TEST_URL)

    report = await inspect_staging_database()

    # Redacted target identity
    assert "postgres:postgres" not in report["target_endpoint"]
    assert report["database_name"] == "automind_staging"
    assert report["host"] == "localhost"
    assert report["port"] == 5434
    assert report["is_production"] is False

    # Server info
    assert "automind_staging" in report["server_database"]
    assert "PostgreSQL" in report["server_version"]

    # Target tables presence
    assert "business_context" in report["tables"]
    assert "product_images" in report["tables"]
    assert report["tables"]["business_context"]["exists"] is True
    assert report["tables"]["product_images"]["exists"] is True

    # RLS flags & columns checked
    bc_info = report["tables"]["business_context"]
    assert bc_info["rls_enabled"] is True
    assert any(c["name"] == "context_key" for c in bc_info["columns"])
    assert any(c["name"] == "active_for_platforms" for c in bc_info["columns"])

    # Formatted report
    formatted = format_preflight_report(report)
    assert "AUTOMIND REMOTE STAGING READ-ONLY PREFLIGHT REPORT" in formatted
    assert "postgres:postgres" not in formatted
    assert report["classification"] == "MIGRATED_CANONICAL"


def test_verify_canonical_schema_rejects_missing_column():
    """Verifies that missing columns strictly prevent MIGRATED_CANONICAL classification."""
    from app.core.staging_preflight_queries import verify_canonical_schema
    # Mock report missing active_for_platforms
    mock_report = {
        "current_alembic_version": "d8f3a1e5c2b4",
        "tables": {
            "business_context": {
                "exists": True,
                "columns": [{"name": "id", "nullable": "NO"}, {"name": "project_id", "nullable": "NO"}],
                "indexes": [{"name": "idx_business_context_project"}],
                "constraints": [],
                "rls_enabled": True
            },
            "product_images": {
                "exists": True,
                "columns": [],
                "indexes": [],
                "constraints": [],
                "rls_enabled": True
            }
        }
    }
    is_canonical, issues = verify_canonical_schema(mock_report)
    assert is_canonical is False
    assert any("missing column" in i for i in issues)


def test_verify_canonical_schema_rejects_disabled_rls():
    """Verifies that disabled RLS on canonical tables is detected and flagged."""
    from app.core.staging_preflight_queries import verify_canonical_schema
    mock_report = {
        "current_alembic_version": "d8f3a1e5c2b4",
        "tables": {
            "business_context": {
                "exists": True,
                "columns": [],
                "indexes": [],
                "constraints": [],
                "rls_enabled": False  # Disabled RLS
            },
            "product_images": {
                "exists": True,
                "columns": [],
                "indexes": [],
                "constraints": [],
                "rls_enabled": True
            }
        }
    }
    is_canonical, issues = verify_canonical_schema(mock_report)
    assert is_canonical is False
    assert any("Row-Level Security (RLS)" in i for i in issues)


def test_verify_canonical_schema_rejects_wrong_alembic_head():
    """Verifies that an older revision is not classified as canonical head."""
    from app.core.staging_preflight_queries import verify_canonical_schema
    mock_report = {
        "current_alembic_version": "c1412562210a",  # Prior version
        "tables": {}
    }
    is_canonical, issues = verify_canonical_schema(mock_report)
    assert is_canonical is False
    assert any("Alembic revision mismatch" in i for i in issues)

