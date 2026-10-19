"""
Pure unit tests for database and image-storage isolation guards.
Tests all fail-closed rejection boundaries in-memory without opening database connections.
Does not import app.core.database or instantiate engines.
"""

from types import SimpleNamespace
import pytest
from app.core.db_identity import normalize_db_identity
from app.core.database_guard import validate_test_database_isolation
from app.core.image_storage_guard import validate_image_storage_isolation


def _make_mock_settings(**kwargs):
    """Creates a mock settings object for pure validation testing."""
    defaults = {
        "is_production": False,
        "ENVIRONMENT": "development",
        "TESTING": True,
        "TESTING_MODE": False,
        "DATABASE_URL": "postgresql+asyncpg://aisales:secret@localhost:5432/aisales",
        "TEST_DATABASE_URL": "postgresql+asyncpg://aisales:secret@localhost:5432/aisales_test",
        "REQUIRE_TEST_DB_EXPLICIT_AUTHORIZATION": True,
        "APPROVED_TEST_DATABASE_URL": "postgresql+asyncpg://aisales:secret@localhost:5432/aisales_test",
        "ALLOWED_TEST_DATABASE_URLS": [],
        "ALLOWED_TEST_DATABASES": ["aisales_test"],
        "IMAGE_STORAGE_DATABASE_URL": "postgresql+asyncpg://aisales:secret@localhost:5432/aisales_img",
        "TEST_IMAGE_STORAGE_DATABASE_URL": "postgresql+asyncpg://aisales:secret@localhost:5432/aisales_img_test",
        "APPROVED_TEST_IMAGE_STORAGE_DATABASE_URL": "postgresql+asyncpg://aisales:secret@localhost:5432/aisales_img_test",
        "ALLOWED_TEST_IMAGE_STORAGE_DATABASE_URLS": [],
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_primary_case_1_rejects_missing_test_url():
    settings = _make_mock_settings(TEST_DATABASE_URL="")
    with pytest.raises(RuntimeError, match="TEST_DATABASE_URL is not configured"):
        validate_test_database_isolation(settings, is_test_active=True, test_reason="test")


def test_primary_case_2_rejects_missing_authorization():
    settings = _make_mock_settings(REQUIRE_TEST_DB_EXPLICIT_AUTHORIZATION=False)
    with pytest.raises(RuntimeError, match="REQUIRE_TEST_DB_EXPLICIT_AUTHORIZATION must be True"):
        validate_test_database_isolation(settings, is_test_active=True, test_reason="test")

    settings2 = _make_mock_settings(APPROVED_TEST_DATABASE_URL=None, ALLOWED_TEST_DATABASE_URLS=[])
    with pytest.raises(RuntimeError, match="No approved test database identities configured"):
        validate_test_database_isolation(settings2, is_test_active=True, test_reason="test")


def test_primary_case_3_rejects_identical_to_dev_database():
    dev_url = "postgresql+asyncpg://aisales:secret@localhost:5432/aisales"
    settings = _make_mock_settings(DATABASE_URL=dev_url, TEST_DATABASE_URL=dev_url, APPROVED_TEST_DATABASE_URL=dev_url)
    with pytest.raises(RuntimeError, match="matches development database name|resolves to the same host"):
        validate_test_database_isolation(settings, is_test_active=True, test_reason="test")


def test_primary_case_4_rejects_approved_name_with_unapproved_host_port():
    settings = _make_mock_settings(
        TEST_DATABASE_URL="postgresql+asyncpg://aisales:secret@remote-host:5432/aisales_test",
        APPROVED_TEST_DATABASE_URL="postgresql+asyncpg://aisales:secret@localhost:5432/aisales_test",
    )
    with pytest.raises(RuntimeError, match="matches approved target, but endpoint 'remote-host:5432' is not authorized"):
        validate_test_database_isolation(settings, is_test_active=True, test_reason="test")


def test_primary_case_5_rejects_approved_host_with_unapproved_db_name():
    settings = _make_mock_settings(
        TEST_DATABASE_URL="postgresql+asyncpg://aisales:secret@localhost:5432/unapproved_db",
        APPROVED_TEST_DATABASE_URL="postgresql+asyncpg://aisales:secret@localhost:5432/aisales_test",
    )
    with pytest.raises(RuntimeError, match="Host and port 'localhost:5432' match approved target, but database 'unapproved_db' is not authorized"):
        validate_test_database_isolation(settings, is_test_active=True, test_reason="test")


def test_primary_case_6_rejects_malformed_or_ambiguous_urls():
    settings = _make_mock_settings(TEST_DATABASE_URL="postgresql+asyncpg://aisales:secret@0.0.0.0:5432/aisales_test")
    with pytest.raises(RuntimeError, match="specifies ambiguous host '0.0.0.0'"):
        validate_test_database_isolation(settings, is_test_active=True, test_reason="test")

    with pytest.raises(RuntimeError, match="has no database name specified"):
        normalize_db_identity("postgresql+asyncpg://aisales:secret@localhost:5432/", "TEST_DATABASE_URL")

    with pytest.raises(RuntimeError, match="specifies invalid port 99999"):
        normalize_db_identity("postgresql+asyncpg://aisales:secret@localhost:99999/test", "TEST_DATABASE_URL")


def test_primary_case_7_never_falls_back_to_dev_database():
    settings = _make_mock_settings(TEST_DATABASE_URL="")
    try:
        res = validate_test_database_isolation(settings, is_test_active=True, test_reason="test")
        pytest.fail(f"Silently returned: {res}")
    except RuntimeError:
        pass


def test_primary_case_8_rejects_test_mode_in_production():
    settings = _make_mock_settings(is_production=True, ENVIRONMENT="production")
    with pytest.raises(RuntimeError, match="Test mode is strictly prohibited in production"):
        validate_test_database_isolation(settings, is_test_active=True, test_reason="test")


def test_verify_case_1_only_primary_approved_rejects_unapproved_image_storage():
    """Case 1: Only the primary test DB is approved; image storage must be rejected."""
    settings = _make_mock_settings(
        APPROVED_TEST_DATABASE_URL="postgresql+asyncpg://aisales:secret@localhost:5432/aisales_test",
        APPROVED_TEST_IMAGE_STORAGE_DATABASE_URL=None,
        ALLOWED_TEST_IMAGE_STORAGE_DATABASE_URLS=[],
        TEST_IMAGE_STORAGE_DATABASE_URL="postgresql+asyncpg://aisales:secret@localhost:5432/aisales_img_test",
    )
    with pytest.raises(RuntimeError, match="No approved test image database identities configured"):
        validate_image_storage_isolation(settings, is_test_active=True, test_reason="test")


def test_verify_case_2_only_image_approved_rejects_unapproved_primary():
    """Case 2: Only the image test DB is approved; primary target must be rejected."""
    settings = _make_mock_settings(
        APPROVED_TEST_DATABASE_URL=None,
        ALLOWED_TEST_DATABASE_URLS=[],
        APPROVED_TEST_IMAGE_STORAGE_DATABASE_URL="postgresql+asyncpg://aisales:secret@localhost:5432/aisales_img_test",
        TEST_DATABASE_URL="postgresql+asyncpg://aisales:secret@localhost:5432/aisales_test",
    )
    with pytest.raises(RuntimeError, match="No approved test database identities configured"):
        validate_test_database_isolation(settings, is_test_active=True, test_reason="test")


def test_verify_case_3_image_url_equals_dev_image_storage_url_rejects():
    """Case 3: Image-storage test URL equals development image-storage URL; reject it."""
    dev_img_url = "postgresql+asyncpg://aisales:secret@localhost:5432/aisales_images_dev"
    settings = _make_mock_settings(
        IMAGE_STORAGE_DATABASE_URL=dev_img_url,
        TEST_IMAGE_STORAGE_DATABASE_URL=dev_img_url,
        APPROVED_TEST_IMAGE_STORAGE_DATABASE_URL=dev_img_url,
    )
    with pytest.raises(RuntimeError, match="matches development image storage database name|resolves to the same host"):
        validate_image_storage_isolation(settings, is_test_active=True, test_reason="test")


def test_verify_case_4_image_url_equals_primary_dev_database_rejects():
    """Case 4: Image-storage test URL equals primary development database; reject it."""
    dev_primary_url = "postgresql+asyncpg://aisales:secret@localhost:5432/aisales_primary_dev"
    settings = _make_mock_settings(
        DATABASE_URL=dev_primary_url,
        IMAGE_STORAGE_DATABASE_URL="postgresql+asyncpg://aisales:secret@localhost:5432/aisales_img_dev",
        TEST_IMAGE_STORAGE_DATABASE_URL=dev_primary_url,
        APPROVED_TEST_IMAGE_STORAGE_DATABASE_URL=dev_primary_url,
    )
    with pytest.raises(RuntimeError, match="matches primary development database name|resolves to the same host"):
        validate_image_storage_isolation(settings, is_test_active=True, test_reason="test")


def test_verify_case_5_image_url_unapproved_host_or_port_rejects():
    """Case 5: A test image URL matches database name on an unapproved host or port; reject it."""
    settings = _make_mock_settings(
        TEST_IMAGE_STORAGE_DATABASE_URL="postgresql+asyncpg://aisales:secret@unapproved-host:5432/aisales_img_test",
        APPROVED_TEST_IMAGE_STORAGE_DATABASE_URL="postgresql+asyncpg://aisales:secret@localhost:5432/aisales_img_test",
    )
    with pytest.raises(RuntimeError, match="matches approved target, but endpoint 'unapproved-host:5432' is not authorized"):
        validate_image_storage_isolation(settings, is_test_active=True, test_reason="test")


def test_verify_case_6_both_separately_approved_distinct_accepts_without_connection():
    """Case 6: Both targets separately approved & distinct from dev targets; accepts without connection."""
    settings = _make_mock_settings(
        DATABASE_URL="postgresql+asyncpg://aisales:secret@localhost:5432/aisales_dev",
        TEST_DATABASE_URL="postgresql+asyncpg://aisales:secret@localhost:5432/aisales_test",
        APPROVED_TEST_DATABASE_URL="postgresql+asyncpg://aisales:secret@localhost:5432/aisales_test",
        ALLOWED_TEST_DATABASES=["aisales_test"],
        IMAGE_STORAGE_DATABASE_URL="postgresql+asyncpg://aisales:secret@localhost:5432/aisales_img_dev",
        TEST_IMAGE_STORAGE_DATABASE_URL="postgresql+asyncpg://aisales:secret@localhost:5432/aisales_img_test",
        APPROVED_TEST_IMAGE_STORAGE_DATABASE_URL="postgresql+asyncpg://aisales:secret@localhost:5432/aisales_img_test",
    )
    res_primary = validate_test_database_isolation(settings, is_test_active=True, test_reason="test")
    res_image = validate_image_storage_isolation(settings, is_test_active=True, test_reason="test")
    assert res_primary == settings.TEST_DATABASE_URL
    assert res_image == settings.TEST_IMAGE_STORAGE_DATABASE_URL


def test_verify_case_7_test_url_targeting_prod_supabase_reference_rejects():
    """Case 7: Candidate or approved test URL pointing to production Supabase project fails closed."""
    prod_test_url = "postgresql+asyncpg://postgres:secret@db.ccejhzadokkjssjiwmxt.supabase.co:5432/postgres"
    settings = _make_mock_settings(
        TEST_DATABASE_URL=prod_test_url,
        APPROVED_TEST_DATABASE_URL=prod_test_url,
    )
    with pytest.raises(RuntimeError, match="targets the production Supabase reference \\(ccejhzadokkjssjiwmxt\\)"):
        validate_test_database_isolation(settings, is_test_active=True, test_reason="test")


def test_verify_case_8_image_url_targeting_prod_supabase_reference_rejects():
    """Case 8: Candidate or approved test image storage URL pointing to production Supabase project fails closed."""
    prod_img_url = "postgresql+asyncpg://postgres:secret@db.ccejhzadokkjssjiwmxt.supabase.co:5432/postgres"
    settings = _make_mock_settings(
        TEST_IMAGE_STORAGE_DATABASE_URL=prod_img_url,
        APPROVED_TEST_IMAGE_STORAGE_DATABASE_URL=prod_img_url,
    )
    with pytest.raises(RuntimeError, match="targets the production Supabase reference \\(ccejhzadokkjssjiwmxt\\)"):
        validate_image_storage_isolation(settings, is_test_active=True, test_reason="test")

