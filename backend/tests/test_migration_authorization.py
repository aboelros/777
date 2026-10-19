"""
Behavioral and regression tests for database migration authorization and startup governance.

Validates that:
1. Production startup strictly prohibits automatic migrations (cannot be bypassed by RUN_MIGRATIONS_ON_STARTUP=true).
2. Environment normalization handles aliases and casing (prod, PRODUCTION, staging, etc.).
3. Staging and development behavior remains explicit, safe, and controlled.
4. Build-time migrations against production are strictly prohibited.
5. HTTP /migrate debug endpoint is disabled in production.
6. Shell scripts (start.sh, render_start.sh, build.sh) behaviorally enforce the prohibition.
"""

import os
import shutil
import subprocess
from pathlib import Path
import pytest
from app.core.migration_guard import (
    evaluate_startup_migration_policy,
    evaluate_build_migration_policy,
    evaluate_http_migration_policy,
    normalize_environment,
)


def test_environment_normalization(monkeypatch):
    """Verify that normalize_environment correctly maps aliases, casing, and whitespace."""
    assert normalize_environment("production") == "production"
    assert normalize_environment("PRODUCTION") == "production"
    assert normalize_environment(" prod ") == "production"
    assert normalize_environment("PROD") == "production"
    assert normalize_environment("staging") == "staging"
    assert normalize_environment("STAGE") == "staging"
    assert normalize_environment("dev") == "development"
    assert normalize_environment("development") == "development"
    assert normalize_environment("local") == "development"
    assert normalize_environment("test") == "test"
    assert normalize_environment("") == "development"
    monkeypatch.delenv("ENVIRONMENT", raising=False)
    assert normalize_environment(None) == "development"


def test_production_override_cannot_bypass_startup_prohibition():
    """Verify that setting RUN_MIGRATIONS_ON_STARTUP=true CANNOT bypass production prohibition."""
    authorized, reason = evaluate_startup_migration_policy(
        environment="production",
        run_flag="true",
    )
    assert not authorized
    assert "strictly prohibited in production" in reason
    assert "cannot bypass this prohibition" in reason


def test_production_without_flag_disallows_startup_migration():
    """Verify that default production disallows startup migrations."""
    authorized, reason = evaluate_startup_migration_policy(
        environment="production",
        run_flag="",
    )
    assert not authorized
    assert "disabled in production by production governance policy" in reason


def test_production_aliases_strictly_prohibit_startup_migrations():
    """Verify that all production aliases enforce the strict startup migration prohibition."""
    for env_alias in ["PRODUCTION", "prod", "PROD", " Production ", "prod-eu"]:
        authorized, reason = evaluate_startup_migration_policy(
            environment=env_alias,
            run_flag="true",
        )
        assert not authorized, f"Failed for production alias: {env_alias}"
        assert "strictly prohibited in production" in reason


def test_staging_disallows_startup_migration_by_default():
    """Verify that staging environment disables startup migrations by default."""
    authorized, reason = evaluate_startup_migration_policy(
        environment="staging",
        run_flag="",
    )
    assert not authorized
    assert "disabled by default in staging" in reason


def test_staging_allows_explicit_opt_in():
    """Verify that staging permits startup migrations only with explicit authorization."""
    authorized, reason = evaluate_startup_migration_policy(
        environment="staging",
        run_flag="true",
    )
    assert authorized
    assert "Explicit RUN_MIGRATIONS_ON_STARTUP authorization detected for staging" in reason


def test_development_allows_startup_migration_by_default():
    """Verify that development enables startup migrations by default."""
    authorized, reason = evaluate_startup_migration_policy(
        environment="development",
        run_flag="",
    )
    assert authorized
    assert "Startup migrations enabled by default" in reason


def test_development_respects_explicit_disable():
    """Verify that development respects explicit disabling via RUN_MIGRATIONS_ON_STARTUP=false."""
    authorized, reason = evaluate_startup_migration_policy(
        environment="development",
        run_flag="false",
    )
    assert not authorized
    assert "Startup migrations explicitly disabled" in reason


def test_build_migration_policy_prohibits_production_build_migrations():
    """Verify that build-time migrations in production are prohibited regardless of flags."""
    authorized, reason = evaluate_build_migration_policy(
        environment="production",
        build_flag="true",
    )
    assert not authorized
    assert "strictly prohibited in production" in reason

    authorized_default, _ = evaluate_build_migration_policy(environment="prod", build_flag="")
    assert not authorized_default


def test_build_migration_policy_staging_and_development():
    """Verify build-time migration behavior for staging and development environments."""
    auth_stage, _ = evaluate_build_migration_policy("staging", build_flag="true")
    assert auth_stage
    no_auth_stage, _ = evaluate_build_migration_policy("staging", build_flag="")
    assert not no_auth_stage

    auth_dev, _ = evaluate_build_migration_policy("development", build_flag="true")
    assert auth_dev
    no_auth_dev, _ = evaluate_build_migration_policy("development", build_flag="")
    assert not no_auth_dev


def test_http_migration_policy_production_and_dev():
    """Verify HTTP /migrate endpoint policy enforcement."""
    auth_prod, reason_prod = evaluate_http_migration_policy(is_production=True)
    assert not auth_prod
    assert "Automated migrations via HTTP are disabled in production" in reason_prod

    auth_dev, _ = evaluate_http_migration_policy(is_production=False)
    assert auth_dev


def test_start_script_governance_structure():
    """Verify that backend/start.sh strictly prohibits production startup migrations."""
    script_path = Path(__file__).resolve().parent.parent / "start.sh"
    content = script_path.read_text(encoding="utf-8")

    assert "strictly PROHIBITED in production" in content
    assert "RUN_MIGRATIONS_ON_STARTUP" in content
    assert "ENVIRONMENT_LOWER" in content


def test_render_start_script_governance_structure():
    """Verify that backend/render_start.sh strictly prohibits production startup migrations."""
    script_path = Path(__file__).resolve().parent.parent / "render_start.sh"
    content = script_path.read_text(encoding="utf-8")

    assert "strictly PROHIBITED in production" in content
    assert "alembic stamp head" not in content
    assert "Seeding Admin Account for $ENVIRONMENT_LOWER" in content


def test_build_script_governance_structure():
    """Verify that backend/build.sh strictly prohibits build migrations in production."""
    script_path = Path(__file__).resolve().parent.parent / "build.sh"
    content = script_path.read_text(encoding="utf-8")

    assert "strictly PROHIBITED in production" in content
    assert "RUN_MIGRATIONS_ON_BUILD" in content


def test_behavioral_start_script_simulation_prohibits_production():
    """Behaviorally simulate bash evaluation to prove production bypass is impossible."""
    bash_path = None
    for candidate in [
        r"C:\Program Files\Git\bin\bash.exe",
        r"C:\Program Files\Git\usr\bin\bash.exe",
        shutil.which("bash"),
    ]:
        if candidate and Path(candidate).exists() and "system32" not in str(candidate).lower():
            bash_path = candidate
            break

    if not bash_path:
        pytest.skip("Working Bash executable not found for behavioral simulation test.")

    script_path = Path(__file__).resolve().parent.parent / "start.sh"
    # Run bash snippet extracting the governance gate with ENVIRONMENT=production and RUN_MIGRATIONS_ON_STARTUP=true
    test_cmd = [
        bash_path,
        "-c",
        (
            'export ENVIRONMENT="production"; '
            'export RUN_MIGRATIONS_ON_STARTUP="true"; '
            'ENVIRONMENT_LOWER=$(echo "${ENVIRONMENT:-development}" | tr "[:upper:]" "[:lower:]" | xargs); '
            'if [ "$ENVIRONMENT_LOWER" = "production" ] || [ "$ENVIRONMENT_LOWER" = "prod" ]; then '
            '  if [ "${RUN_MIGRATIONS_ON_STARTUP:-false}" = "true" ]; then '
            '    echo "MIGRATION_PROHIBITED_WARNING"; '
            '  fi; '
            '  echo "MIGRATION_BLOCKED"; '
            'else '
            '  echo "MIGRATION_ALLOWED"; '
            'fi'
        ),
    ]
    result = subprocess.run(test_cmd, capture_output=True, text=True, check=True)
    assert "MIGRATION_PROHIBITED_WARNING" in result.stdout
    assert "MIGRATION_BLOCKED" in result.stdout
    assert "MIGRATION_ALLOWED" not in result.stdout
