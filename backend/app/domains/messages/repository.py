from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from app.core.repository import BaseRepository
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



