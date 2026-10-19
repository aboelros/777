"""
Pure unit tests for Alembic database isolation and safety guard.
Ensures Alembic cannot bypass database isolation during tests or offline generation.
Does not establish network connections or open databases.
"""

import importlib.util
from types import ModuleType, SimpleNamespace
from typing import Optional
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from alembic.config import Config
from app.core.database_guard import resolve_alembic_database_url

_ALEMBIC_ENV_MOD: Optional[ModuleType] = None


def _get_loaded_alembic_env() -> ModuleType:
    """Loads and caches alembic/env.py safely with mock database isolation."""
    global _ALEMBIC_ENV_MOD
    if _ALEMBIC_ENV_MOD is None:
        mock_db = MagicMock(Base=MagicMock(metadata=MagicMock()))
        with patch.dict("sys.modules", {"app.core.database": mock_db}):
            spec = importlib.util.spec_from_file_location("alembic_env", "alembic/env.py")
            assert spec is not None and spec.loader is not None
            _ALEMBIC_ENV_MOD = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(_ALEMBIC_ENV_MOD)
    return _ALEMBIC_ENV_MOD


def _make_mock_settings(**kwargs) -> SimpleNamespace:
    """Creates a mock settings object for Alembic isolation testing."""
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
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_case_1_test_mode_missing_test_database_url_fails_closed() -> None:
    """Security Case 1: Test mode with missing TEST_DATABASE_URL fails closed."""
    settings = _make_mock_settings(TEST_DATABASE_URL="")
    with pytest.raises(RuntimeError, match="TEST_DATABASE_URL is not configured"):
        resolve_alembic_database_url(settings, is_offline=False)


def test_case_2_test_mode_missing_explicit_authorization_fails_closed() -> None:
    """Security Case 2: Test mode without explicit authorization fails closed."""
    # Subcase A: Authorization flag is False
    settings_no_flag = _make_mock_settings(REQUIRE_TEST_DB_EXPLICIT_AUTHORIZATION=False)
    with pytest.raises(RuntimeError, match="REQUIRE_TEST_DB_EXPLICIT_AUTHORIZATION must be True"):
        resolve_alembic_database_url(settings_no_flag, is_offline=False)

    # Subcase B: Approved URL whitelist is empty
    settings_no_approved = _make_mock_settings(
        APPROVED_TEST_DATABASE_URL="",
        ALLOWED_TEST_DATABASE_URLS=[],
    )
    with pytest.raises(RuntimeError, match="No approved test database identities configured"):
        resolve_alembic_database_url(settings_no_approved, is_offline=False)


def test_case_3_test_mode_unauthorized_target_rejected() -> None:
    """Security Case 3: An unauthorized host, port, or database name is rejected."""
    # Subcase A: Unauthorized host/port
    settings_bad_host = _make_mock_settings(
        TEST_DATABASE_URL="postgresql+asyncpg://aisales:secret@remote-unauthorized:5432/aisales_test",
        APPROVED_TEST_DATABASE_URL="postgresql+asyncpg://aisales:secret@localhost:5432/aisales_test",
    )
    with pytest.raises(RuntimeError, match="matches approved target, but endpoint.*is not authorized"):
        resolve_alembic_database_url(settings_bad_host, is_offline=False)

    # Subcase B: Unauthorized database name
    settings_bad_db = _make_mock_settings(
        TEST_DATABASE_URL="postgresql+asyncpg://aisales:secret@localhost:5432/unauthorized_db",
        APPROVED_TEST_DATABASE_URL="postgresql+asyncpg://aisales:secret@localhost:5432/aisales_test",
    )
    with pytest.raises(RuntimeError, match="match approved target, but database.*is not authorized"):
        resolve_alembic_database_url(settings_bad_db, is_offline=False)


def test_case_4_test_mode_valid_approved_target_accepted() -> None:
    """Security Case 4: An explicitly approved isolated test database is accepted."""
    settings = _make_mock_settings()
    resolved = resolve_alembic_database_url(settings, is_offline=False)
    assert resolved == settings.TEST_DATABASE_URL
    assert resolved != settings.DATABASE_URL


def test_case_5_offline_sql_generation_without_connection() -> None:
    """Security Case 5: Offline SQL generation works without opening a database connection."""
    # Even if TEST_DATABASE_URL is unconfigured, offline compilation succeeds safely
    settings = _make_mock_settings(TEST_DATABASE_URL="")
    resolved = resolve_alembic_database_url(settings, is_offline=True)
    assert resolved == settings.DATABASE_URL


@pytest.mark.asyncio
async def test_case_6_online_alembic_execution_cannot_bypass_resolver() -> None:
    """Security Case 6: Online Alembic execution cannot bypass the approved resolver."""
    env_mod = _get_loaded_alembic_env()

    # Prepare mock config pointing initially to a spoofed URL
    mock_cfg = MagicMock()
    mock_cfg.config_ini_section = "alembic"
    mock_cfg.get_section.return_value = {"sqlalchemy.url": "postgresql://spoofed:5432/spoofed_db"}
    orig_config = env_mod.config

    try:
        env_mod.config = mock_cfg

        # Mock engine creation and connection without opening network sockets
        mock_engine = MagicMock()
        mock_conn = AsyncMock()
        mock_engine.connect.return_value.__aenter__.return_value = mock_conn
        mock_engine.connect.return_value.__aexit__.return_value = None
        mock_engine.dispose = AsyncMock()

        with patch.object(env_mod, "async_engine_from_config", return_value=mock_engine) as mock_create_engine:
            # Scenario A: Approved isolated test database URL is resolved and passed to engine
            test_settings = _make_mock_settings()
            with patch.object(env_mod, "get_target_database_url", return_value=test_settings.TEST_DATABASE_URL):
                await env_mod.run_async_migrations()
                mock_create_engine.assert_called_once()
                passed_cfg = mock_create_engine.call_args[0][0]
                # Verify the spoofed URL was overwritten with the approved test URL
                assert passed_cfg["sqlalchemy.url"] == test_settings.TEST_DATABASE_URL
                assert passed_cfg["sqlalchemy.url"] != "postgresql://spoofed:5432/spoofed_db"

            mock_create_engine.reset_mock()

            # Scenario B: Resolver throws RuntimeError when unisolated; engine creation is aborted
            with patch.object(env_mod, "get_target_database_url", side_effect=RuntimeError("FAIL CLOSED")):
                with pytest.raises(RuntimeError, match="FAIL CLOSED"):
                    await env_mod.run_async_migrations()
                # Engine creation was halted before any connection could be initiated
                mock_create_engine.assert_not_called()
    finally:
        env_mod.config = orig_config


def test_case_7_resolver_never_silently_selects_dev_or_prod_in_test() -> None:
    """Security Case 7: The resolver does not silently select a production/development URL in test execution."""
    dev_url = "postgresql+asyncpg://aisales:secret@localhost:5432/aisales"
    settings_same_as_dev = _make_mock_settings(
        DATABASE_URL=dev_url,
        TEST_DATABASE_URL=dev_url,
        APPROVED_TEST_DATABASE_URL=dev_url,
    )
    with pytest.raises(RuntimeError, match="matches development database name|resolves to the same host"):
        resolve_alembic_database_url(settings_same_as_dev, is_offline=False)


def test_case_8_normal_non_test_execution_and_production_policy() -> None:
    """Security Case 8: Normal non-test online execution follows the project's baseline authorization policy."""
    # Subcase A: Development non-test execution returns development DATABASE_URL
    dev_settings = _make_mock_settings(
        ENVIRONMENT="development",
        TESTING=False,
        TESTING_MODE=False,
        DATABASE_URL="postgresql+asyncpg://aisales:secret@localhost:5432/aisales",
    )
    resolved_dev = resolve_alembic_database_url(
        dev_settings,
        is_offline=False,
        is_test_active=False,
        test_reason="Not in test mode",
    )
    assert resolved_dev == dev_settings.DATABASE_URL

    # Subcase B: Production settings in test mode are strictly prohibited (fails closed)
    prod_test_settings = _make_mock_settings(
        is_production=True,
        ENVIRONMENT="production",
        TESTING=True,
    )
    with pytest.raises(RuntimeError, match="Test mode is strictly prohibited in production"):
        resolve_alembic_database_url(prod_test_settings, is_offline=False, is_test_active=True)

    # Subcase C: Production settings in non-test mode return DATABASE_URL under current repository baseline
    prod_nontest_settings = _make_mock_settings(
        is_production=True,
        ENVIRONMENT="production",
        TESTING=False,
        TESTING_MODE=False,
        DATABASE_URL="postgresql+asyncpg://postgres:secret@prod.supabase.co:6543/postgres",
    )
    resolved_prod = resolve_alembic_database_url(
        prod_nontest_settings,
        is_offline=False,
        is_test_active=False,
        test_reason="Not in test mode",
    )
    assert resolved_prod == prod_nontest_settings.DATABASE_URL


def test_case_9_importing_alembic_env_outside_active_context_is_safe() -> None:
    """Security Case 9: Importing alembic/env.py outside an active Alembic context remains safe."""
    mod = _get_loaded_alembic_env()
    assert hasattr(mod, "get_target_database_url")
    assert hasattr(mod, "run_migrations_offline")
    assert hasattr(mod, "run_migrations_online")
    assert mod.config is None


def test_case_10_url_percent_escaping_preserved() -> None:
    """Security Case 10: URL percent escaping remains correct."""
    raw_url = "postgresql+asyncpg://aisales:p%40ssword@localhost:5432/aisales"
    escaped_url = raw_url.replace("%", "%%")
    assert "%%" in escaped_url
    assert "p%%40ssword" in escaped_url

    cfg = Config()
    cfg.set_main_option("sqlalchemy.url", escaped_url)
    retrieved = cfg.get_main_option("sqlalchemy.url")
    assert retrieved == raw_url
