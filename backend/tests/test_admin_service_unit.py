"""
Unit tests for AdminService and AdminTelemetryService.
Tests metrics processing, audit trails, and platform settings.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.services.admin_telemetry_service import AdminTelemetryService
from app.api.v1.admin_schemas import AdminUserCreate, PlatformSettingsUpdate


def test_admin_telemetry_audit_logging():
    """Verify that audit actions are recorded and retrievable."""
    AdminTelemetryService.record_audit_action(
        action="TEST_ACTION",
        performed_by="admin@example.com",
        details="Tested audit logging mechanism",
    )
    logs = AdminTelemetryService.get_audit_logs(page=1, page_size=10)
    assert logs["total"] > 0
    recent = logs["items"][0]
    assert recent["action"] == "TEST_ACTION"
    assert recent["performed_by"] == "admin@example.com"


def test_admin_platform_settings_updates():
    """Verify that platform settings can be fetched and modified."""
    initial = AdminTelemetryService.get_settings()
    assert "maintenance_mode" in initial
    assert "user_registration_enabled" in initial

    updated = AdminTelemetryService.update_settings(
        {"default_free_messages": 300, "maintenance_mode": True},
        admin_email="superadmin@example.com",
    )
    assert updated["default_free_messages"] == 300
    assert updated["maintenance_mode"] is True

    # Restore settings
    AdminTelemetryService.update_settings(
        {"default_free_messages": 100, "maintenance_mode": False},
        admin_email="superadmin@example.com",
    )


def test_admin_user_create_schema_validation():
    """Verify AdminUserCreate Pydantic schema validation."""
    valid_payload = AdminUserCreate(
        email="merchant@example.com",
        password="ValidPassword123!",
        name="Merchant Store",
    )
    assert valid_payload.email == "merchant@example.com"
    assert valid_payload.is_active is True

    with pytest.raises(Exception):
        # Password too short
        AdminUserCreate(
            email="merchant@example.com",
            password="short",
        )
