import pytest
from uuid import uuid4
from datetime import datetime
from sqlalchemy import text
from app.core.database import AsyncSessionLocal
from app.core.context import TenantContext
from app.domains.orders.repository import OrderRepository
from app.services.order_manager_service import OrderManagerService
from app.domains.orders.models import OrderStatus

pytestmark = pytest.mark.asyncio

async def test_order_cross_tenant_read_and_mutation():
    async with AsyncSessionLocal() as db:
        from app.db.models import User, Project
        from app.domains.orders.models import Order
        
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
        p1 = Project(id=proj_a_id, name="A", owner_id=user1, project_code=str(uuid4())[:8])
        p2 = Project(id=proj_b_id, name="B", owner_id=user2, project_code=str(uuid4())[:8])
        db.add_all([p1, p2])
        await db.flush()
        
        # Create order
        order_id = uuid4()
        o1 = Order(
            id=order_id,
            project_id=proj_b_id,
            customer={},
            total=100.0,
            status=OrderStatus.PENDING.value,
            provider="system",
            external_id=str(uuid4()),
            order_date=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(o1)
        await db.commit()

        context_a = TenantContext(project_id=proj_a_id, user_id=user1, role="owner")
        
        # Test Repository Read
        repo = OrderRepository(db)
        order = await repo.get_by_context(order_id, context_a)
        assert order is None  # Should not be able to read order B via context A
        
        # Test Service Mutation
        svc = OrderManagerService(db, context_a)
        with pytest.raises(ValueError, match="not found"):
            await svc.update_order_status(order_id, OrderStatus.FULFILLED)
            
        with pytest.raises(ValueError, match="not found"):
            await svc.auto_progress_order(order_id)
            
        # Test Aggregates
        stats = await repo.get_management_statistics(context_a)
        assert stats["total_orders"] == 0
        
        attention = await repo.get_orders_requiring_attention(context_a)
        assert len(attention["pending"]) == 0
        assert len(attention["processing"]) == 0
