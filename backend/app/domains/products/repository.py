from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.core.repository import BaseRepository
from app.domains.products.models import Product

class ProductRepository(BaseRepository[Product]):
    def __init__(self, session: AsyncSession):
        super().__init__(Product, session)

    async def get_project_products(
        self,
        project_id: UUID,
        category: Optional[str] = None,
        search: Optional[str] = None,
        in_stock: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Product]:
        query = select(self.model).where(
            self.model.project_id == project_id,
            self.model.is_active == True
        )
        
        if category:
            query = query.where(self.model.category == category)
        
        if in_stock is not None:
            query = query.where(self.model.in_stock == in_stock)
            
        if search:
            query = query.where(
                or_(
                    self.model.name.ilike(f"%{search}%"),
                    self.model.sku.ilike(f"%{search}%")
                )
            )
            
        query = query.order_by(self.model.created_at.desc()).offset(offset).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_sku(self, project_id: UUID, sku: str) -> Optional[Product]:
        if not sku:
            return None
        result = await self.session.execute(
            select(self.model).where(
                self.model.project_id == project_id,
                self.model.sku == sku
            )
        )
        return result.scalar_one_or_none()
