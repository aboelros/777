import pytest
from uuid import uuid4
from datetime import datetime
from sqlalchemy import text
from app.core.database import AsyncSessionLocal
from app.core.context import TenantContext
from app.services.payment_service import PaymentService

pytestmark = pytest.mark.asyncio

async def test_payment_cross_tenant_read_and_mutation():
    async with AsyncSessionLocal() as db:
        from app.db.models import User, Project
        from app.domains.billing.models import Invoice, PaymentLink
        from app.domains.customers.models import CustomerProfile
        
        user1 = uuid4()
        user2 = uuid4()
        proj_a_id = uuid4()
        proj_b_id = uuid4()
        
        # Create user 1 and user 2
        u1 = User(id=user1, email=f"{user1}@example.com", password_hash="hash")
        u2 = User(id=user2, email=f"{user2}@example.com", password_hash="hash")
        db.add_all([u1, u2])
        await db.flush()
        
        # Create projects
        p1 = Project(id=proj_a_id, name="Project A", owner_id=user1, project_code=str(uuid4())[:8])
        p2 = Project(id=proj_b_id, name="Project B", owner_id=user2, project_code=str(uuid4())[:8])
        db.add_all([p1, p2])
        await db.flush()

        # Create customers
        cust_a = CustomerProfile(id=uuid4(), project_id=proj_a_id, name="Cust A", customer_id="ext1")
        cust_b = CustomerProfile(id=uuid4(), project_id=proj_b_id, name="Cust B", customer_id="ext2")
        db.add_all([cust_a, cust_b])
        await db.flush()
        
        # Create an invoice in Project A
        inv_a = Invoice(
            id=uuid4(),
            project_id=proj_a_id,
            customer_id=cust_a.id,
            invoice_number=f"INV-{int(datetime.now().timestamp())}",
            items=[{"name": "test", "price": 100, "quantity": 1}],
            amount=100.0,
            total_amount=100.0,
            status="draft"
        )
        db.add(inv_a)
        await db.flush()

        # Context for User 2 / Project B
        context_b = TenantContext(
            user_id=user2,
            project_id=proj_b_id,
            role="owner",
            permissions=frozenset(["*"]),
            membership_id=None
        )

        service_b = PaymentService(db, context_b)
        
        # 1. Test read isolation: User 2 fetching invoices for Project B should NOT see Project A's invoice
        b_invoices = await service_b.get_project_invoices()
        assert len(b_invoices) == 0, "User B should not see User A's invoices"

        # 2. Test create isolation: User 2 creates an invoice in Project B
        inv_b = await service_b.create_invoice(
            customer_id=cust_b.id,
            items=[{"name": "test2", "price": 200, "quantity": 1}],
            notes="For Project B"
        )
        
        # Ensure the invoice is tied to Project B
        assert inv_b.project_id == proj_b_id, "Invoice must be created under context project_id"
        
        # 3. Test payment link creation isolation: User 2 creates a payment link
        link_b = await service_b.create_payment_link(amount=50.0)
        assert link_b.project_id == proj_b_id, "Payment link must be created under context project_id"
        
        await db.rollback()
