from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete
from typing import List, Optional, Any, Dict
from uuid import UUID

from app.core.repository import BaseRepository
from app.core.context import TenantContext
from app.domains.ai.models import (
    ModelTraining,
    BotInstruction,
    KnowledgeBase,
    AutoResponseTemplate,
)


class ModelTrainingRepository(BaseRepository[ModelTraining]):
    def __init__(self, session: AsyncSession):
        super().__init__(ModelTraining, session)

    async def get_by_context(self, training_id: UUID, context: TenantContext) -> Optional[ModelTraining]:
        query = select(self.model).where(
            self.model.id == training_id,
            self.model.project_id == context.project_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_by_context(self, context: TenantContext) -> List[ModelTraining]:
        query = select(self.model).where(
            self.model.project_id == context.project_id
        ).order_by(self.model.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_project(self, project_id: UUID) -> List[ModelTraining]:
        query = select(self.model).where(self.model.project_id == project_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())


class BotInstructionRepository(BaseRepository[BotInstruction]):
    def __init__(self, session: AsyncSession):
        super().__init__(BotInstruction, session)

    async def get_by_context(self, instruction_id: UUID, context: TenantContext) -> Optional[BotInstruction]:
        query = select(self.model).where(
            self.model.id == instruction_id,
            self.model.project_id == context.project_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_active_by_context(self, context: TenantContext) -> List[BotInstruction]:
        query = select(self.model).where(
            self.model.project_id == context.project_id,
            self.model.is_active == True
        ).order_by(self.model.priority.desc(), self.model.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_by_context(self, context: TenantContext, active_only: bool = False) -> List[BotInstruction]:
        query = select(self.model).where(self.model.project_id == context.project_id)
        if active_only:
            query = query.where(self.model.is_active == True)
        query = query.order_by(self.model.priority.desc(), self.model.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create_instruction(self, context: TenantContext, data: Dict[str, Any]) -> BotInstruction:
        instruction = BotInstruction(
            project_id=context.project_id,
            title=data["title"],
            instruction=data["instruction"],
            category=data.get("category"),
            priority=data.get("priority", 0),
            active_for_platforms=data.get("active_for_platforms") or [],
            active_for_topics=data.get("active_for_topics") or [],
            examples=data.get("examples") or [],
            is_active=data.get("is_active", True)
        )
        self.session.add(instruction)
        return instruction

    async def update_by_context(
        self, instruction_id: UUID, context: TenantContext, update_data: Dict[str, Any]
    ) -> Optional[BotInstruction]:
        instruction = await self.get_by_context(instruction_id, context)
        if not instruction:
            return None
        for field, value in update_data.items():
            if value is not None and hasattr(instruction, field):
                setattr(instruction, field, value)
        return instruction

    async def delete_by_context(self, instruction_id: UUID, context: TenantContext) -> bool:
        instruction = await self.get_by_context(instruction_id, context)
        if not instruction:
            return False
        await self.session.delete(instruction)
        return True

    async def get_by_project(self, project_id: UUID) -> List[BotInstruction]:
        query = select(self.model).where(self.model.project_id == project_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())


class KnowledgeBaseRepository(BaseRepository[KnowledgeBase]):
    def __init__(self, session: AsyncSession):
        super().__init__(KnowledgeBase, session)

    async def get_by_context(self, item_id: UUID, context: TenantContext) -> Optional[KnowledgeBase]:
        query = select(self.model).where(
            self.model.id == item_id,
            self.model.project_id == context.project_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_by_context(self, context: TenantContext, active_only: bool = False) -> List[KnowledgeBase]:
        query = select(self.model).where(self.model.project_id == context.project_id)
        if active_only:
            query = query.where(self.model.is_active == True)
        query = query.order_by(self.model.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_active_by_context(self, context: TenantContext, limit: int = 10) -> List[KnowledgeBase]:
        query = select(self.model).where(
            self.model.project_id == context.project_id,
            self.model.is_active == True
        ).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create_item(self, context: TenantContext, data: Dict[str, Any]) -> KnowledgeBase:
        item = KnowledgeBase(
            project_id=context.project_id,
            title=data["title"],
            content=data["content"],
            source_type=data.get("source_type", "text"),
            source_url=data.get("source_url"),
            is_active=data.get("is_active", True),
            tags=data.get("tags") or [],
            metadata_info=data.get("metadata_info") or {}
        )
        self.session.add(item)
        return item

    async def update_by_context(
        self, item_id: UUID, context: TenantContext, update_data: Dict[str, Any]
    ) -> Optional[KnowledgeBase]:
        item = await self.get_by_context(item_id, context)
        if not item:
            return None
        for field, value in update_data.items():
            if value is not None and hasattr(item, field):
                setattr(item, field, value)
        return item

    async def delete_by_context(self, item_id: UUID, context: TenantContext) -> bool:
        item = await self.get_by_context(item_id, context)
        if not item:
            return False
        await self.session.delete(item)
        return True

    async def get_by_project(self, project_id: UUID) -> List[KnowledgeBase]:
        query = select(self.model).where(self.model.project_id == project_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())


class AutoResponseTemplateRepository(BaseRepository[AutoResponseTemplate]):
    def __init__(self, session: AsyncSession):
        super().__init__(AutoResponseTemplate, session)

    async def get_by_context(self, template_id: UUID, context: TenantContext) -> Optional[AutoResponseTemplate]:
        query = select(self.model).where(
            self.model.id == template_id,
            self.model.project_id == context.project_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_by_context(self, context: TenantContext, active_only: bool = False) -> List[AutoResponseTemplate]:
        query = select(self.model).where(self.model.project_id == context.project_id)
        if active_only:
            query = query.where(self.model.is_active == True)
        query = query.order_by(self.model.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create_template(self, context: TenantContext, data: Dict[str, Any]) -> AutoResponseTemplate:
        template = AutoResponseTemplate(
            project_id=context.project_id,
            name=data["name"],
            description=data.get("description"),
            trigger_keywords=data.get("trigger_keywords") or [],
            trigger_platforms=data.get("trigger_platforms") or [],
            trigger_intent=data.get("trigger_intent"),
            response_template=data["response_template"],
            variations=data.get("variations") or [],
            use_ai_enhancement=data.get("use_ai_enhancement", True),
            requires_approval=data.get("requires_approval", False),
            is_active=data.get("is_active", True)
        )
        self.session.add(template)
        return template

    async def get_by_project(self, project_id: UUID) -> List[AutoResponseTemplate]:
        query = select(self.model).where(self.model.project_id == project_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())
