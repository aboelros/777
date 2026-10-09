import pytest
from uuid import uuid4
from fastapi import HTTPException
from httpx import AsyncClient, ASGITransport

import app.main
from app.main import app
from app.db.models import User
from app.domains.projects.models import Project
from app.domains.crm.models import PipelineStage, Deal
from app.core.database import AsyncSessionLocal
from app.core.security import create_access_token

@pytest.mark.asyncio
async def test_crm_deal_pipeline_security():
    user_a_id = uuid4()
    project_a_id = uuid4()
    
    user_b_id = uuid4()
    project_b_id = uuid4()
    
    stage_a_id = uuid4()
    deal_a_id = uuid4()
    
    stage_b_id = uuid4()
    deal_b_id = uuid4()

    async with AsyncSessionLocal() as db:
        user_a = User(id=user_a_id, email=f"test_a_{user_a_id}@example.com", password_hash="hash", role="admin")
        project_a = Project(id=project_a_id, owner_id=user_a_id, project_code=f"PRJ_A_{project_a_id}", name="Project A", timezone="UTC")
        stage_a = PipelineStage(id=stage_a_id, project_id=project_a_id, name="Stage A", index=0)
        deal_a = Deal(id=deal_a_id, project_id=project_a_id, stage_id=stage_a_id, title="Deal A", value=100)

        user_b = User(id=user_b_id, email=f"test_b_{user_b_id}@example.com", password_hash="hash", role="admin")
        project_b = Project(id=project_b_id, owner_id=user_b_id, project_code=f"PRJ_B_{project_b_id}", name="Project B", timezone="UTC")
        stage_b = PipelineStage(id=stage_b_id, project_id=project_b_id, name="Stage B", index=0)
        deal_b = Deal(id=deal_b_id, project_id=project_b_id, stage_id=stage_b_id, title="Deal B", value=200)

        db.add_all([user_a, project_a, stage_a, deal_a, user_b, project_b, stage_b, deal_b])
        await db.commit()

    token_a = create_access_token({'sub': str(user_a_id)})
    headers_a = {'Authorization': f'Bearer {token_a}'}

    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        # Case A: Authorized access & Case E: List isolation
        r = await client.get(f'/api/v1/deals/{project_a_id}/stages', headers=headers_a)
        assert r.status_code == 200, r.text
        stages = r.json()
        assert len(stages) == 1
        assert stages[0]["id"] == str(stage_a_id)

        r = await client.get(f'/api/v1/deals/{project_a_id}/deals', headers=headers_a)
        assert r.status_code == 200
        deals = r.json()
        assert len(deals) == 1
        assert deals[0]["id"] == str(deal_a_id)
        
        # Case B: Cross-tenant read / Case C: Forged project ID
        # If A tries to read B's list by passing B's project_id, TenantContext dependency should reject it (403/404 based on context resolution)
        r = await client.get(f'/api/v1/deals/{project_b_id}/deals', headers=headers_a)
        # It should be 403 or 404 depending on how get_tenant_context fails
        assert r.status_code in (403, 404)

        # Case C: Forged project ID / Cross-tenant mutation (create)
        # A tries to create a deal in Project A, but assigning it to Project B's stage
        r = await client.post(
            f'/api/v1/deals/{project_a_id}/deals',
            headers=headers_a,
            params={"title": "Hacked Deal", "stage_id": str(stage_b_id), "value": 500}
        )
        assert r.status_code == 404  # Stage not found in context A

        # Case D: Cross-tenant mutation (update)
        # A tries to update B's deal, sending the request to project_a
        r = await client.patch(
            f'/api/v1/deals/{project_a_id}/deals/{deal_b_id}',
            headers=headers_a,
            params={"value": 9999}
        )
        assert r.status_code == 404  # Deal not found in context A
        
        # Verify db state didn't change (Case D confirmation)
        from sqlalchemy import select
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Deal).where(Deal.id == deal_b_id))
            deal_b_check = result.scalar_one()
            assert deal_b_check.value == 200

        # Case F: Missing or invalid tenant context (No Auth)
        r = await client.get(f'/api/v1/deals/{project_a_id}/deals')
        assert r.status_code == 401

@pytest.mark.asyncio
async def test_crm_repository_predicates():
    from app.core.context import TenantContext
    from app.domains.crm.repository import DealRepository, PipelineStageRepository
    from app.core.uow import UnitOfWork
    
    user_id = uuid4()
    project_id = uuid4()
    project_b_id = uuid4()
    deal_b_id = uuid4()
    
    async with AsyncSessionLocal() as db:
        user = User(id=user_id, email=f"test_repo_{user_id}@example.com", password_hash="hash", role="admin")
        project = Project(id=project_id, owner_id=user_id, project_code=f"PRJ_C_{project_id}", name="Project C", timezone="UTC")
        project_b = Project(id=project_b_id, owner_id=user_id, project_code=f"PRJ_D_{project_b_id}", name="Project D", timezone="UTC")
        stage_b = PipelineStage(id=uuid4(), project_id=project_b_id, name="Stage D", index=0)
        deal_b = Deal(id=deal_b_id, project_id=project_b_id, stage_id=stage_b.id, title="Deal D", value=100)
        
        db.add_all([user, project, project_b, stage_b, deal_b])
        await db.commit()
        
    # Test repo directly (Case G - Repository predicate verification)
    async with AsyncSessionLocal() as db:
        ctx = TenantContext(user_id=user_id, project_id=project_id, role="admin")
        
        repo = DealRepository(db, ctx)
        fetched = await repo.get_deal_by_context(deal_b_id, context=ctx)
        assert fetched is None  # Should return None because context.project_id != deal_b.project_id

        # Missing context simulation
        with pytest.raises(ValueError):
            repo = DealRepository(db)
            await repo.list_by_context()

