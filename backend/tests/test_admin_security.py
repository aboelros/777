"""
Unit and integration tests for platform admin endpoints and security enforcement.
"""

import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.database import get_db, get_auth_db
from app.core.security import create_access_token


@pytest.mark.asyncio
async def test_admin_rbac_unauthorized():
    """Verify unauthenticated requests to admin routes return 401."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/api/v1/admin/dashboard")
        assert res.status_code == 401


@pytest.mark.asyncio
async def test_admin_rbac_standard_user_forbidden():
    """Verify users with standard role are forbidden (403) from admin endpoints."""
    user_id = uuid4()
    token = create_access_token({"sub": str(user_id), "role": "user"})
    headers = {"Authorization": f"Bearer {token}"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/api/v1/admin/dashboard", headers=headers)
        assert res.status_code == 403


@pytest.mark.asyncio
async def test_admin_endpoints_authorized():
    """Verify administrator account can access dashboard, telemetry, and platform settings."""
    admin_id = uuid4()
    token = create_access_token({"sub": str(admin_id), "role": "admin"})
    headers = {"Authorization": f"Bearer {token}"}

    # Mock DB session for admin tests
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one.return_value = 0
    mock_result.one.return_value = (0, 0.0)
    mock_result.all.return_value = []
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result

    async def override_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_auth_db] = override_db

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Dashboard
            dash_res = await client.get("/api/v1/admin/dashboard", headers=headers)
            assert dash_res.status_code == 200
            dash_data = dash_res.json()
            assert "total_users" in dash_data
            assert "total_messages" in dash_data

            # Health
            health_res = await client.get("/api/v1/admin/health", headers=headers)
            assert health_res.status_code == 200
            health_data = health_res.json()
            assert "database" in health_data

            # Projects Fleet
            proj_res = await client.get("/api/v1/admin/projects", headers=headers)
            assert proj_res.status_code == 200
            proj_data = proj_res.json()
            assert "items" in proj_data

            # AI Telemetry
            ai_res = await client.get("/api/v1/admin/ai/telemetry", headers=headers)
            assert ai_res.status_code == 200
            ai_data = ai_res.json()
            assert "primary_model" in ai_data

            # Webhook Logs
            wh_res = await client.get("/api/v1/admin/webhooks/logs", headers=headers)
            assert wh_res.status_code == 200

            # Platform Settings GET & PATCH
            settings_res = await client.get("/api/v1/admin/settings", headers=headers)
            assert settings_res.status_code == 200

            patch_res = await client.patch(
                "/api/v1/admin/settings",
                headers=headers,
                json={"default_free_messages": 250},
            )
            assert patch_res.status_code == 200
            assert patch_res.json()["default_free_messages"] == 250
    finally:
        app.dependency_overrides.clear()
