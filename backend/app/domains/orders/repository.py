from typing import Optional, List
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.core.repository import BaseRepository
from app.domains.orders.models import Order

class OrderRepository(BaseRepository[Order]):
    def __init__(self, session: AsyncSession):
        super().__init__(Order, session)

    async def get_by_context(self, order_id: UUID, context: "TenantContext") -> Optional[Order]:
        """Fetch an order explicitly scoped to the TenantContext."""
        stmt = select(self.model).where(
            self.model.id == order_id,
            self.model.project_id == context.project_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_external_id(self, project_id: UUID, external_id: str, provider: str) -> Optional[Order]:
        result = await self.session.execute(
            select(self.model).where(
                self.model.project_id == project_id,
                self.model.external_id == external_id,
                self.model.provider == provider
            )
        )
        return result.scalar_one_or_none()

    async def get_project_orders(
        self, 
        project_id: UUID, 
        status: Optional[str] = None, 
        provider: Optional[str] = None, 
        start_date: Optional[datetime] = None,
        limit: int = 50, 
        offset: int = 0
    ) -> List[Order]:
        query = select(self.model).where(self.model.project_id == project_id)
        
        if status:
            query = query.where(self.model.status == status)
        if provider:
            query = query.where(self.model.provider == provider)
        if start_date:
            query = query.where(self.model.order_date >= start_date)
            
        query = query.order_by(self.model.order_date.desc()).offset(offset).limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_orders_requiring_attention(
        self,
        context: "TenantContext",
        max_age_hours: int = 48
    ) -> dict:
        from datetime import datetime, timedelta
        from app.domains.orders.models import OrderStatus
        from sqlalchemy import and_
        cutoff_date = datetime.utcnow() - timedelta(hours=max_age_hours)
        
        # Pending orders older than cutoff
        query_pending = select(self.model).where(
            and_(
                self.model.project_id == context.project_id,
                self.model.status == OrderStatus.PENDING.value,
                self.model.order_date < cutoff_date
            )
        ).order_by(self.model.order_date)
        pending_orders = (await self.session.execute(query_pending)).scalars().all()
        
        # Processing orders older than cutoff
        query_processing = select(self.model).where(
            and_(
                self.model.project_id == context.project_id,
                self.model.status == OrderStatus.PROCESSING.value,
                self.model.updated_at < cutoff_date
            )
        ).order_by(self.model.updated_at)
        processing_orders = (await self.session.execute(query_processing)).scalars().all()
        
        return {
            "pending": list(pending_orders),
            "processing": list(processing_orders)
        }

    async def get_order_stats(self, context: "TenantContext", start_date: datetime) -> dict:
        from sqlalchemy import func
        total_orders = await self.session.scalar(
            select(func.count(self.model.id))
            .where(self.model.project_id == context.project_id, self.model.order_date >= start_date)
        ) or 0
        
        total_revenue = await self.session.scalar(
            select(func.sum(self.model.total))
            .where(self.model.project_id == context.project_id, self.model.order_date >= start_date)
        ) or 0.0
        
        status_result = await self.session.execute(
            select(self.model.status, func.count(self.model.id))
            .where(self.model.project_id == context.project_id, self.model.order_date >= start_date)
            .group_by(self.model.status)
        )
        orders_by_status = dict(status_result.all())
        
        return {
            "total_orders": total_orders,
            "total_revenue": float(total_revenue),
            "orders_by_status": orders_by_status,
            "period_days": (datetime.utcnow() - start_date).days
        }

    async def get_management_statistics(self, context: "TenantContext") -> dict:
        from sqlalchemy import func, and_
        from datetime import datetime, timedelta
        
        # Count orders by status
        result = await self.session.execute(
            select(self.model.status, func.count(self.model.id))
            .where(self.model.project_id == context.project_id)
            .group_by(self.model.status)
        )
        status_counts = dict(result.fetchall())
        
        # Total orders
        total_orders = await self.session.scalar(
            select(func.count(self.model.id))
            .where(self.model.project_id == context.project_id)
        ) or 0
        
        # Orders in last 7 days
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_orders = await self.session.scalar(
            select(func.count(self.model.id))
            .where(
                and_(
                    self.model.project_id == context.project_id,
                    self.model.order_date >= week_ago
                )
            )
        ) or 0
        
        return {
            "total_orders": total_orders,
            "orders_by_status": status_counts,
            "recent_orders_7days": recent_orders
        }
