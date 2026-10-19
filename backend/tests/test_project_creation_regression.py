"""
Regression tests for Project creation fixes in Task 6 / 6B.
Verifies project_code population, schema response defaults,
and tenant isolation on newly created projects.
"""

import pytest
from uuid import uuid4
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status

from app.main import app
from app.domains.auth.models import User
from app.core.security import create_access_token
from app.core.database import AsyncSessionLocal
import pytest_asyncio


@pytest_asyncio.fixture
async def db_session():
    async with AsyncSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def test_users(db_session: AsyncSession):
    user_1 = User(email=f"owner_{uuid4().hex[:6]}@example.com", name="Owner 1", password_hash="hash")
    user_2 = User(email=f"intruder_{uuid4().hex[:6]}@example.com", name="Intruder 2", password_hash="hash")
    db_session.add_all([user_1, user_2])
    await db_session.commit()
    await db_session.refresh(user_1)
    await db_session.refresh(user_2)
    return {"owner": user_1, "intruder": user_2}


@pytest.fixture
def auth_tokens(test_users):
    return {
        "owner": create_access_token({"sub": str(test_users["owner"].id)}),
        "intruder": create_access_token({"sub": str(test_users["intruder"].id)}),
    }


@pytest.mark.asyncio
async def test_project_creation_success(auth_tokens, test_users):
    """Verify project creation properly populates project_code, settings, and response defaults."""
    code = f"PRJ-{uuid4().hex[:6].upper()}"
    async with AsyncClient(transport=ASGITransport(app=app, raise_app_exceptions=False), base_url="http://test") as client:
        payload = {
            "project_code": code,
            "name": "Alpha Staging Brand",
            "description": "Staging environment project",
            "timezone": "America/New_York",
            "settings": {"auto_reply": True, "theme": "dark"}
        }
        resp = await client.post(
            "/api/v1/projects",
            json=payload,
            headers={"Authorization": f"Bearer {auth_tokens['owner']}"}
        )
        assert resp.status_code == status.HTTP_201_CREATED, f"Failed: {resp.text}"
        data = resp.json()
        assert data["project_code"] == code
        assert data["name"] == "Alpha Staging Brand"
        assert data["description"] == "Staging environment project"
        assert data["timezone"] == "America/New_York"
        assert data["settings"] == {"auto_reply": True, "theme": "dark"}
        assert data["owner_id"] == str(test_users["owner"].id)
        assert data["is_active"] is True
        assert data["role"] == "owner"
        assert "created_at" in data
        assert data["updated_at"] is None  # Verifies Optional default works cleanly


@pytest.mark.asyncio
async def test_project_creation_missing_project_code(auth_tokens):
    """Verify request validation rejects missing project_code with 422."""
    async with AsyncClient(transport=ASGITransport(app=app, raise_app_exceptions=False), base_url="http://test") as client:
        payload = {
            "name": "Invalid Project Without Code",
            "description": "Should fail validation"
        }
        resp = await client.post(
            "/api/v1/projects",
            json=payload,
            headers={"Authorization": f"Bearer {auth_tokens['owner']}"}
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_project_creation_duplicate_code_fails(auth_tokens):
    """Verify unique constraint on project_code is enforced fail-closed."""
    code = f"DUP-{uuid4().hex[:6].upper()}"
    async with AsyncClient(transport=ASGITransport(app=app, raise_app_exceptions=False), base_url="http://test") as client:
        payload = {"project_code": code, "name": "Brand First"}
        resp1 = await client.post(
            "/api/v1/projects",
            json=payload,
            headers={"Authorization": f"Bearer {auth_tokens['owner']}"}
        )
        assert resp1.status_code == status.HTTP_201_CREATED

        # Second creation with identical project_code
        resp2 = await client.post(
            "/api/v1/projects",
            json=payload,
            headers={"Authorization": f"Bearer {auth_tokens['owner']}"}
        )
        assert resp2.status_code in (status.HTTP_400_BAD_REQUEST, status.HTTP_409_CONFLICT, status.HTTP_500_INTERNAL_SERVER_ERROR)


@pytest.mark.asyncio
async def test_created_project_tenant_isolation(auth_tokens):
    """Verify newly created project cannot be read by another tenant."""
    code = f"ISO-{uuid4().hex[:6].upper()}"
    async with AsyncClient(transport=ASGITransport(app=app, raise_app_exceptions=False), base_url="http://test") as client:
        create_resp = await client.post(
            "/api/v1/projects",
            json={"project_code": code, "name": "Isolated Brand"},
            headers={"Authorization": f"Bearer {auth_tokens['owner']}"}
        )
        assert create_resp.status_code == status.HTTP_201_CREATED
        project_id = create_resp.json()["id"]

        # Owner has access
        owner_resp = await client.get(
            f"/api/v1/projects/{project_id}",
            headers={"Authorization": f"Bearer {auth_tokens['owner']}"}
        )
        assert owner_resp.status_code == status.HTTP_200_OK

        # Intruder is denied with 404 (anti-enumeration)
        intruder_resp = await client.get(
            f"/api/v1/projects/{project_id}",
            headers={"Authorization": f"Bearer {auth_tokens['intruder']}"}
        )
        assert intruder_resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_project_deletion_lifecycle(auth_tokens):
    """Verify owner can delete project (HTTP 204) and intruder cannot."""
    code = f"DEL-{uuid4().hex[:6].upper()}"
    async with AsyncClient(transport=ASGITransport(app=app, raise_app_exceptions=False), base_url="http://test") as client:
        create_resp = await client.post(
            "/api/v1/projects",
            json={"project_code": code, "name": "Deletion Test Brand"},
            headers={"Authorization": f"Bearer {auth_tokens['owner']}"}
        )
        assert create_resp.status_code == status.HTTP_201_CREATED
        project_id = create_resp.json()["id"]

        # Intruder cannot delete project (fails 403/404)
        intruder_del = await client.delete(
            f"/api/v1/projects/{project_id}",
            headers={"Authorization": f"Bearer {auth_tokens['intruder']}"}
        )
        assert intruder_del.status_code in (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND)

        # Owner successfully deletes project
        owner_del = await client.delete(
            f"/api/v1/projects/{project_id}",
            headers={"Authorization": f"Bearer {auth_tokens['owner']}"}
        )
        assert owner_del.status_code == status.HTTP_204_NO_CONTENT

        # Project no longer exists
        get_resp = await client.get(
            f"/api/v1/projects/{project_id}",
            headers={"Authorization": f"Bearer {auth_tokens['owner']}"}
        )
        assert get_resp.status_code == status.HTTP_404_NOT_FOUND

