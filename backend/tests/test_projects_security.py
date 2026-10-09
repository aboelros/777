import pytest
from uuid import uuid4
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status

from app.main import app
from app.domains.projects.models import Project, ProjectMember, ProjectRole
from app.domains.auth.models import User
from app.core.security import create_access_token

from app.core.database import AsyncSessionLocal
import pytest_asyncio

@pytest_asyncio.fixture
async def db_session():
    async with AsyncSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def users(db_session: AsyncSession):
    user_a = User(email=f"user_a_{uuid4()}@example.com", name="User A", password_hash="hash")
    user_b = User(email=f"user_b_{uuid4()}@example.com", name="User B", password_hash="hash")
    user_c = User(email=f"user_c_{uuid4()}@example.com", name="User C", password_hash="hash")
    db_session.add_all([user_a, user_b, user_c])
    await db_session.commit()
    return {"A": user_a, "B": user_b, "C": user_c}

@pytest_asyncio.fixture
async def projects(db_session: AsyncSession, users):
    project_a = Project(name="Project A", owner_id=users["A"].id, project_code=f"PRJ_{uuid4()}")
    project_b = Project(name="Project B", owner_id=users["B"].id, project_code=f"PRJ_{uuid4()}")
    db_session.add_all([project_a, project_b])
    await db_session.commit()
    
    member_c = ProjectMember(project_id=project_a.id, user_id=users["C"].id, role=ProjectRole.WORKER)
    db_session.add(member_c)
    await db_session.commit()
    
    return {"A": project_a, "B": project_b}

@pytest.fixture
def tokens(users):
    return {
        "A": create_access_token({"sub": str(users["A"].id)}),
        "B": create_access_token({"sub": str(users["B"].id)}),
        "C": create_access_token({"sub": str(users["C"].id)})
    }

@pytest.mark.asyncio
async def test_same_tenant_project_access(projects, tokens):
    async with AsyncClient(transport=ASGITransport(app=app, raise_app_exceptions=False), base_url='http://test') as client:
        response = await client.get(
            f"/api/v1/projects/{projects['A'].id}",
            headers={"Authorization": f"Bearer {tokens['A']}"}
        )
        assert response.status_code == status.HTTP_200_OK

@pytest.mark.asyncio
async def test_cross_tenant_project_access_denied(projects, tokens):
    async with AsyncClient(transport=ASGITransport(app=app, raise_app_exceptions=False), base_url='http://test') as client:
        response = await client.get(
            f"/api/v1/projects/{projects['A'].id}",
            headers={"Authorization": f"Bearer {tokens['B']}"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_cross_tenant_membership_listing_denied(projects, tokens):
    async with AsyncClient(transport=ASGITransport(app=app, raise_app_exceptions=False), base_url='http://test') as client:
        response = await client.get(
            f"/api/v1/projects/{projects['A'].id}/members",
            headers={"Authorization": f"Bearer {tokens['B']}"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_cross_tenant_member_creation_denied(projects, tokens, users):
    async with AsyncClient(transport=ASGITransport(app=app, raise_app_exceptions=False), base_url='http://test') as client:
        response = await client.post(
            f"/api/v1/projects/{projects['A'].id}/members?member_email={users['B'].email}&role=worker",
            headers={"Authorization": f"Bearer {tokens['B']}"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_unauthorized_member_adding_denied(projects, tokens, users):
    async with AsyncClient(transport=ASGITransport(app=app, raise_app_exceptions=False), base_url='http://test') as client:
        new_user_email = f"new_{uuid4()}@example.com"
        response = await client.post(
            f"/api/v1/projects/{projects['A'].id}/members?member_email={new_user_email}&role=worker",
            headers={"Authorization": f"Bearer {tokens['C']}"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.asyncio
async def test_self_escalation_to_owner_denied(projects, tokens, users):
    async with AsyncClient(transport=ASGITransport(app=app, raise_app_exceptions=False), base_url='http://test') as client:
        response = await client.patch(
            f"/api/v1/projects/{projects['A'].id}/members/{users['C'].id}?role=owner",
            headers={"Authorization": f"Bearer {tokens['C']}"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.asyncio
async def test_owner_escalation_denied(projects, tokens, users):
    async with AsyncClient(transport=ASGITransport(app=app, raise_app_exceptions=False), base_url='http://test') as client:
        response = await client.patch(
            f"/api/v1/projects/{projects['A'].id}/members/{users['C'].id}?role=owner",
            headers={"Authorization": f"Bearer {tokens['A']}"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.asyncio
async def test_missing_tenant_context_fails_closed(projects):
    async with AsyncClient(transport=ASGITransport(app=app, raise_app_exceptions=False), base_url='http://test') as client:
        response = await client.get(f"/api/v1/projects/{projects['A'].id}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.asyncio
async def test_legitimate_owner_operations(projects, tokens, users):
    async with AsyncClient(transport=ASGITransport(app=app, raise_app_exceptions=False), base_url='http://test') as client:
        response = await client.post(
            f"/api/v1/projects/{projects['A'].id}/members?member_email={users['B'].email}&role=worker",
            headers={"Authorization": f"Bearer {tokens['A']}"}
        )
        assert response.status_code == status.HTTP_201_CREATED

        response = await client.patch(
            f"/api/v1/projects/{projects['A'].id}/members/{users['B'].id}?role=moderator",
            headers={"Authorization": f"Bearer {tokens['A']}"}
        )
        assert response.status_code == status.HTTP_200_OK

        response = await client.delete(
            f"/api/v1/projects/{projects['A'].id}/members/{users['B'].id}",
            headers={"Authorization": f"Bearer {tokens['A']}"}
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
