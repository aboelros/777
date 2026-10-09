import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.core.database import get_db

logger = logging.getLogger(__name__)

class UnitOfWork:
    """
    Unit of Work pattern to handle database transactions safely.
    It encapsulates the database session and provides commit/rollback functionality.
    """
    def __init__(self, session: AsyncSession):
        self.session = session

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is not None:
                await self.rollback()
        finally:
            pass # Let get_db handle closing

    async def commit(self):
        try:
            await self.session.commit()
        except Exception as e:
            logger.error(f"Error during commit: {e}")
            await self.session.rollback()
            raise

    async def rollback(self):
        await self.session.rollback()


async def get_uow(session: AsyncSession = Depends(get_db)) -> UnitOfWork:
    """Dependency for injecting UnitOfWork."""
    return UnitOfWork(session)
