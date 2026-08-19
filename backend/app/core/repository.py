from typing import Generic, TypeVar, Type, Any, Optional, List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    def add(self, obj: ModelType) -> None:
        self.session.add(obj)


    async def get(self, id: Any) -> Optional[ModelType]:
        query = select(self.model).filter(self.model.id == id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_multi(
        self, *, skip: int = 0, limit: int = 100, filters: dict = None
    ) -> List[ModelType]:
        query = select(self.model)
        if filters:
            for attr, value in filters.items():
                if hasattr(self.model, attr):
                    query = query.filter(getattr(self.model, attr) == value)
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create(self, *, obj_in: Dict[str, Any]) -> ModelType:
        db_obj = self.model(**obj_in)
        self.session.add(db_obj)
        # Flush to get the ID, but don't commit yet (UoW handles commit)
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj

    async def update(
        self, *, db_obj: ModelType, obj_in: Dict[str, Any]
    ) -> ModelType:
        for field in obj_in:
            if hasattr(db_obj, field):
                setattr(db_obj, field, obj_in[field])
        self.session.add(db_obj)
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj

    async def delete(self, *, id: Any) -> ModelType:
        obj = await self.get(id=id)
        if obj:
            await self.session.delete(obj)
            await self.session.flush()
        return obj
