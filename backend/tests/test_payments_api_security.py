import pytest
from httpx import AsyncClient
from uuid import uuid4, UUID
from fastapi import status
from sqlalchemy import text, delete
from app.main import app
from app.core.database import AsyncSessionLocal
from app.core.security import create_access_token

pytestmark = pytest.mark.asyncio

async def get_auth_headers(user_id: str):
    token = create_access_token(data={"sub": str(user_id)})
    return {"Authorization": f"Bearer {token}"}

async def test_payment_endpoints_tenant_isolation():
    from app.db.models import User, Project
    from app.domains.customers.models import CustomerProfile
    from app.domains.projects.models import ProjectMember
    from app.domains.billing.models import Invoice, PaymentLink

    user1 = uuid4()
    user2 = uuid4()
    proj_a_id = uuid4()
    proj_b_id = uuid4()
    
    async with AsyncSessionLocal() as db:
        # Setup Users
        u1 = User(id=user1, email=f"{user1}@example.com", password_hash="hash")
        u2 = User(id=user2, email=f"{user2}@example.com", password_hash="hash")
        db.add_all([u1, u2])
        
        # Setup Projects
        p1 = Project(id=proj_a_id, name="Project A", owner_id=user1, project_code=str(uuid4())[:8])
        p2 = Project(id=proj_b_id, name="Project B", owner_id=user2, project_code=str(uuid4())[:8])
        db.add_all([p1, p2])
        await db.flush()
        
        m1 = ProjectMember(project_id=proj_a_id, user_id=user1, role="owner")
        m2 = ProjectMember(project_id=proj_b_id, user_id=user2, role="owner")
        db.add_all([m1, m2])
        
        # Setup Customers
        cust_a = CustomerProfile(id=uuid4(), project_id=proj_a_id, name="Cust A", customer_id="ext1")
        cust_b = CustomerProfile(id=uuid4(), project_id=proj_b_id, name="Cust B", customer_id="ext2")
        db.add_all([cust_a, cust_b])
        await db.commit()

    try:
        headers_u1 = await get_auth_headers(str(user1))
        headers_u2 = await get_auth_headers(str(user2))

        async with AsyncClient(transport=pytest.importorskip("httpx").ASGITransport(app=app), base_url="http://test") as client:
            
            # Case A - Valid customer
            # Caller belongs to Project A. Customer A belongs to Project A.
            resp = await client.post(
                f"/api/v1/payments/{proj_a_id}/invoices",
                headers=headers_u1,
                json={
                    "customer_id": str(cust_a.id),
                    "items": [{"name": "item", "price": 100, "quantity": 1}]
                }
            )
            assert resp.status_code == status.HTTP_200_OK, resp.text
            data = resp.json()
            assert data["project_id"] == str(proj_a_id)
            assert data["customer_id"] == str(cust_a.id)
            
            # Case B - Foreign-tenant customer
            # Caller belongs to Project A. Caller attempts to use Customer B's ID.
            resp = await client.post(
                f"/api/v1/payments/{proj_a_id}/invoices",
                headers=headers_u1,
                json={
                    "customer_id": str(cust_b.id),
                    "items": [{"name": "item", "price": 100, "quantity": 1}]
                }
            )
            assert resp.status_code == status.HTTP_404_NOT_FOUND, "User 1 cannot use User 2's customer"

            # Case C - Nonexistent customer
            # Caller belongs to Project A. Customer ID does not exist.
            resp = await client.post(
                f"/api/v1/payments/{proj_a_id}/invoices",
                headers=headers_u1,
                json={
                    "customer_id": str(uuid4()),
                    "items": [{"name": "item", "price": 100, "quantity": 1}]
                }
            )
            assert resp.status_code == status.HTTP_404_NOT_FOUND, "Cannot use nonexistent customer"

            # Test general read isolation
            resp = await client.get(
                f"/api/v1/payments/{proj_a_id}/invoices",
                headers=headers_u2
            )
            assert resp.status_code == status.HTTP_404_NOT_FOUND, "User 2 cannot list User 1's invoices"

            # Test general write isolation
            resp = await client.post(
                f"/api/v1/payments/{proj_a_id}/invoices",
                headers=headers_u2,
                json={
                    "customer_id": str(cust_a.id),
                    "items": [{"name": "item", "price": 100, "quantity": 1}]
                }
            )
            assert resp.status_code == status.HTTP_404_NOT_FOUND, "User 2 cannot create invoice in User 1's project"

    finally:
        # Strict scoped cleanup
        async with AsyncSessionLocal() as db:
            await db.execute(delete(Invoice).where(Invoice.project_id.in_([proj_a_id, proj_b_id])))
            await db.execute(delete(PaymentLink).where(PaymentLink.project_id.in_([proj_a_id, proj_b_id])))
            await db.execute(delete(CustomerProfile).where(CustomerProfile.project_id.in_([proj_a_id, proj_b_id])))
            await db.execute(delete(ProjectMember).where(ProjectMember.project_id.in_([proj_a_id, proj_b_id])))
            await db.execute(delete(Project).where(Project.id.in_([proj_a_id, proj_b_id])))
            await db.execute(delete(User).where(User.id.in_([user1, user2])))
            await db.commit()
