from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Optional
from uuid import UUID

from app.core.context import TenantContext
from app.core.repository import BaseRepository
from app.domains.customers.models import CustomerProfile

class CustomerProfileRepository(BaseRepository[CustomerProfile]):
    def __init__(self, session: AsyncSession):
        super().__init__(CustomerProfile, session)
        
    async def get_by_provider_id(self, project_id: UUID, provider: str, provider_id: str) -> Optional[CustomerProfile]:
        query = select(self.model).where(
            self.model.project_id == project_id,
            self.model.provider == provider,
            self.model.provider_id == provider_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_project(self, project_id: UUID) -> List[CustomerProfile]:
        query = select(self.model).where(self.model.project_id == project_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    # --- Phase 1 Security Migration Methods ---
    
    async def get_profile_by_context(self, context: 'TenantContext', profile_id: UUID) -> Optional[CustomerProfile]:
        """
        Retrieves a customer profile securely scoped to the authorized TenantContext.
        Enforces the invariant: profile_id -> profile.project_id -> context.project_id
        """
        query = select(self.model).where(
            self.model.id == profile_id,
            self.model.project_id == context.project_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
