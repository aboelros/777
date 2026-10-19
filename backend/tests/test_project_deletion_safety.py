"""
Dedicated Safety Audit Tests for Project Deletion.
Verifies RBAC enforcement (owner-only), 404 handling,
cascade deletion of child entities, and session synchronization.
"""

import pytest
from uuid import uuid4, UUID
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from fastapi import status

from app.main import app
from app.domains.auth.models import User
from app.domains.projects.models import Project
from app.domains.projects.repository import ProjectRepository
from app.core.security import create_access_token
from app.core.database import AsyncSessionLocal
import pytest_asyncio


@pytest_asyncio.fixture
async def db_session():
    async with AsyncSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def deletion_users(db_session: AsyncSession):
    owner = User(email=f"owner_{uuid4().hex[:6]}@example.com", name="Owner", password_hash="hash")
    worker = User(email=f"worker_{uuid4().hex[:6]}@example.com", name="Worker", password_hash="hash")
    intruder = User(email=f"intruder_{uuid4().hex[:6]}@example.com", name="Intruder", password_hash="hash")
    db_session.add_all([owner, worker, intruder])
    await db_session.commit()
    for u in [owner, worker, intruder]:
        await db_session.refresh(u)
    return {"owner": owner, "worker": worker, "intruder": intruder}


@pytest.fixture
def deletion_tokens(deletion_users):
    return {
        "owner": create_access_token({"sub": str(deletion_users["owner"].id)}),
        "worker": create_access_token({"sub": str(deletion_users["worker"].id)}),
        "intruder": create_access_token({"sub": str(deletion_users["intruder"].id)}),
    }


@pytest.mark.asyncio
async def test_deletion_non_existent_project_returns_404(deletion_tokens):
    """Deleting a non-existent project returns 404 Not Found."""
    random_id = uuid4()
    async with AsyncClient(transport=ASGITransport(app=app, raise_app_exceptions=False), base_url="http://test") as client:
        resp = await client.delete(
            f"/api/v1/projects/{random_id}",
            headers={"Authorization": f"Bearer {deletion_tokens['owner']}"}
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_deletion_non_owner_member_rejected_403(deletion_tokens, deletion_users):
    """A member with 'worker' role cannot delete the project and receives 403 Forbidden."""
    code = f"RBAC-{uuid4().hex[:6].upper()}"
    async with AsyncClient(transport=ASGITransport(app=app, raise_app_exceptions=False), base_url="http://test") as client:
        # Owner creates project
        create_resp = await client.post(
            "/api/v1/projects",
            json={"project_code": code, "name": "Worker RBAC Test"},
            headers={"Authorization": f"Bearer {deletion_tokens['owner']}"}
        )
        assert create_resp.status_code == status.HTTP_201_CREATED
        project_id = create_resp.json()["id"]

        # Owner adds worker
        add_resp = await client.post(
            f"/api/v1/projects/{project_id}/members?member_email={deletion_users['worker'].email}&role=worker",
            headers={"Authorization": f"Bearer {deletion_tokens['owner']}"}
        )
        assert add_resp.status_code == status.HTTP_201_CREATED

        # Worker attempts to delete project -> 403 Forbidden
        worker_del = await client.delete(
            f"/api/v1/projects/{project_id}",
            headers={"Authorization": f"Bearer {deletion_tokens['worker']}"}
        )
        assert worker_del.status_code == status.HTTP_403_FORBIDDEN

        # Clean up by owner -> 204
        cleanup_resp = await client.delete(
            f"/api/v1/projects/{project_id}",
            headers={"Authorization": f"Bearer {deletion_tokens['owner']}"}
        )
        assert cleanup_resp.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_deletion_cascades_and_cleans_children(deletion_tokens, db_session: AsyncSession):
    """Deleting a project cascades cleanly to dependent records in the database."""
    code = f"CAS-{uuid4().hex[:6].upper()}"
    async with AsyncClient(transport=ASGITransport(app=app, raise_app_exceptions=False), base_url="http://test") as client:
        create_resp = await client.post(
            "/api/v1/projects",
            json={"project_code": code, "name": "Cascade Test"},
            headers={"Authorization": f"Bearer {deletion_tokens['owner']}"}
        )
        assert create_resp.status_code == status.HTTP_201_CREATED
        project_id = create_resp.json()["id"]

        # Create a product in project
        prod_resp = await client.post(
            f"/api/v1/products/{project_id}",
            json={"name": "Cascade Item", "price": 10.0, "currency": "USD", "project_id": project_id},
            headers={"Authorization": f"Bearer {deletion_tokens['owner']}"}
        )
        assert prod_resp.status_code in (200, 201)

        # Delete project as owner
        del_resp = await client.delete(
            f"/api/v1/projects/{project_id}",
            headers={"Authorization": f"Bearer {deletion_tokens['owner']}"}
        )
        assert del_resp.status_code == status.HTTP_204_NO_CONTENT

        # Direct DB verification: both project and products rows are gone
        p_cnt = (await db_session.execute(text("SELECT count(*) FROM projects WHERE id = :id"), {"id": UUID(project_id)})).scalar()
        prod_cnt = (await db_session.execute(text("SELECT count(*) FROM products WHERE project_id = :id"), {"id": UUID(project_id)})).scalar()
        assert p_cnt == 0
        assert prod_cnt == 0


@pytest.mark.asyncio
async def test_deletion_expunges_from_session_identity_map(deletion_users, db_session: AsyncSession):
    """Verifies ProjectRepository.delete removes the entity from session identity map."""
    project = Project(
        project_code=f"EXP-{uuid4().hex[:6].upper()}",
        name="Expunge Test",
        owner_id=deletion_users["owner"].id
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    repo = ProjectRepository(db_session)
    deleted_proj = await repo.delete(id=project.id)
    await db_session.commit()

    assert deleted_proj is not None
    # Verify entity is no longer in session identity map
    assert project not in db_session
