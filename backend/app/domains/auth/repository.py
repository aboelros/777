from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.core.repository import BaseRepository
from app.domains.auth.models import User, RefreshToken

class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(
            select(self.model).where(self.model.email == email)
        )
        return result.scalar_one_or_none()

class RefreshTokenRepository(BaseRepository[RefreshToken]):
    def __init__(self, session: AsyncSession):
        super().__init__(RefreshToken, session)

    async def get_by_token(self, token: str) -> Optional[RefreshToken]:
        result = await self.session.execute(
            select(self.model).where(self.model.token == token)
        )
        return result.scalar_one_or_none()
        
    async def delete_by_token(self, token: str) -> None:
        await self.session.execute(
            delete(self.model).where(self.model.token == token)
        )
        
    async def delete_by_user(self, user_id: UUID) -> None:
        await self.session.execute(
            delete(self.model).where(self.model.user_id == user_id)
        )
