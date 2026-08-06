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
