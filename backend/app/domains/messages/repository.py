from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from app.core.repository import BaseRepository
from app.core.context import TenantContext
from app.domains.messages.models import Message

class MessageRepository(BaseRepository[Message]):
    def __init__(self, session: AsyncSession):
        super().__init__(Message, session)

    async def get_project_messages(self, project_id: UUID, limit: int = 50, offset: int = 0) -> List[Message]:
        query = select(self.model).where(
            self.model.project_id == project_id
        ).order_by(self.model.created_at.desc()).offset(offset).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    # --- Phase 1 Security Migration Methods ---
    
    async def get_message_by_context(self, context: 'TenantContext', message_id: UUID) -> Optional[Message]:
        """
        Retrieves a message, enforcing that the message belongs to the tenant.
        The project scope is explicitly derived from the authorized TenantContext.
        """
        query = select(self.model).where(
            self.model.id == message_id,
            self.model.project_id == context.project_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_inbox_by_context(
        self, 
        context: 'TenantContext', 
        limit: int = 50,
        provider: Optional[str] = None,
        days: int = 30
    ) -> List[Message]:
        """
        Retrieves inbox messages scoped strictly to the authorized TenantContext.
        """
        from datetime import datetime, timedelta
        from sqlalchemy.orm import selectinload
        
        query = select(self.model).options(selectinload(self.model.customer)).where(
            self.model.project_id == context.project_id
        )
        
        if provider and provider.lower() != "all":
            query = query.where(self.model.provider == provider)
            
        start_date = datetime.utcnow() - timedelta(days=days)
        query = query.where(self.model.created_at >= start_date)
        
        query = query.order_by(self.model.created_at.desc()).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_recent_messages_by_context(
        self,
        context: 'TenantContext',
        provider: Optional[str] = None,
        days: int = 30,
        limit: int = 200
    ) -> List[Message]:
        """
        Retrieves messages strictly scoped to the authorized TenantContext.
        """
        from datetime import datetime, timedelta
        from sqlalchemy.orm import selectinload
        
        query = select(self.model).options(selectinload(self.model.customer)).where(
            self.model.project_id == context.project_id
        )
        
        if provider and provider.lower() != "all":
            if provider.lower() in ["instagram", "facebook", "whatsapp"]:
                query = query.where(or_(
                    self.model.provider == provider, 
                    self.model.platform == provider,
                    and_(self.model.provider == "meta", self.model.platform == provider)
                ))
            else:
                query = query.where(self.model.provider == provider)
                
        start_date = datetime.utcnow() - timedelta(days=days)
        query = query.where(self.model.created_at >= start_date)
        
        query = query.order_by(self.model.created_at.desc()).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())



