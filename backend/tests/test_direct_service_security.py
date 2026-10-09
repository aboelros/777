import pytest
import uuid
from sqlalchemy import select
from app.db.models import Project, User
from app.domains.integrations.models import Integration, IntegrationStatus
from app.domains.integrations.repository import IntegrationRepository
from app.domains.integrations.service import IntegrationService
from app.core.database import AsyncSessionLocal
from app.core.context import TenantContext
from fastapi import HTTPException
from app.core.uow import UnitOfWork

pytestmark = pytest.mark.asyncio

async def test_direct_service_and_repo_security():
    async with AsyncSessionLocal() as db:
        user_a = User(id=uuid.uuid4(), email=f"a_{uuid.uuid4()}@ex.com", is_active=True, password_hash="hash")
        project_a = Project(id=uuid.uuid4(), name="Project A", owner_id=user_a.id, project_code=str(uuid.uuid4())[:8])
        
        user_b = User(id=uuid.uuid4(), email=f"b_{uuid.uuid4()}@ex.com", is_active=True, password_hash="hash")
        project_b = Project(id=uuid.uuid4(), name="Project B", owner_id=user_b.id, project_code=str(uuid.uuid4())[:8])
        
        db.add_all([user_a, project_a, user_b, project_b])
        await db.commit()
        
        int_a = Integration(
            project_id=project_a.id,
            provider="whatsapp",
            status=IntegrationStatus.CONNECTED,
            config={"api_key": "secret_key_a"}
        )
        db.add(int_a)
        await db.commit()
        
        # User B context
        context_b = TenantContext(
            user_id=user_b.id,
            project_id=project_b.id,
            role="owner"
        )
        
        # Test 1: Direct Repository Access
        repo = IntegrationRepository(db)
        result = await repo.get_tenant_integration(project_b.id, int_a.id)
        assert result is None, "Repo returned a cross-tenant integration!"
        
        # Test 2: Direct Service Read
        service = IntegrationService(UnitOfWork(AsyncSessionLocal()))
        with pytest.raises(HTTPException) as exc:
            await service.get_integration(context_b, str(int_a.id))
        assert exc.value.status_code == 404
        
        # Test 3: Direct Service Update
        with pytest.raises(HTTPException) as exc:
            await service.update_integration(context_b, str(int_a.id), {"status": "disconnected"})
        assert exc.value.status_code == 404
        
        # Verify no mutation
        await db.refresh(int_a)
        assert int_a.status == IntegrationStatus.CONNECTED
        
        # Test 4: Direct Service Delete
        with pytest.raises(HTTPException) as exc:
            await service.delete_integration(context_b, str(int_a.id))
        assert exc.value.status_code == 404
        
        # Verify no deletion
        await db.refresh(int_a)
        assert int_a is not None

