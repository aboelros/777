from typing import List, Optional, Any, Dict
from uuid import UUID
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy import select, func
import structlog

from app.core.uow import UnitOfWork
from app.core.context import TenantContext
from app.domains.ai.repository import (
    ModelTrainingRepository, 
    BotInstructionRepository,
    KnowledgeBaseRepository,
    AutoResponseTemplateRepository
)
from app.domains.ai.models import BotInstruction, KnowledgeBase, AutoResponseTemplate
from app.domains.analytics.models import APILog
from app.core.default_instructions import get_default_instructions

logger = structlog.get_logger(__name__)


class AIService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    # --- Bot Instructions ---

    async def list_bot_instructions(
        self, context: TenantContext, active_only: bool = False
    ) -> List[BotInstruction]:
        async with self.uow as uow:
            repo = BotInstructionRepository(uow.session)
            return await repo.list_by_context(context, active_only=active_only)

    async def get_bot_instruction(
        self, instruction_id: UUID, context: TenantContext
    ) -> BotInstruction:
        async with self.uow as uow:
            repo = BotInstructionRepository(uow.session)
            instruction = await repo.get_by_context(instruction_id, context)
            if not instruction:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Instruction not found"
                )
            return instruction

    async def create_bot_instruction(
        self, context: TenantContext, data: Dict[str, Any]
    ) -> BotInstruction:
        async with self.uow as uow:
            repo = BotInstructionRepository(uow.session)
            instruction = await repo.create_instruction(context, data)
            await uow.commit()
            await uow.session.refresh(instruction)
            logger.info("Bot instruction created", instruction_id=str(instruction.id), project_id=str(context.project_id))
            return instruction

    async def update_bot_instruction(
        self, instruction_id: UUID, context: TenantContext, update_data: Dict[str, Any]
    ) -> BotInstruction:
        async with self.uow as uow:
            repo = BotInstructionRepository(uow.session)
            instruction = await repo.update_by_context(instruction_id, context, update_data)
            if not instruction:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Instruction not found"
                )
            await uow.commit()
            await uow.session.refresh(instruction)
            logger.info("Bot instruction updated", instruction_id=str(instruction.id), project_id=str(context.project_id))
            return instruction

    async def delete_bot_instruction(
        self, instruction_id: UUID, context: TenantContext
    ) -> None:
        async with self.uow as uow:
            repo = BotInstructionRepository(uow.session)
            deleted = await repo.delete_by_context(instruction_id, context)
            if not deleted:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Instruction not found"
                )
            await uow.commit()
            logger.info("Bot instruction deleted", instruction_id=str(instruction_id), project_id=str(context.project_id))

    async def seed_default_instructions(self, context: TenantContext) -> List[BotInstruction]:
        async with self.uow as uow:
            repo = BotInstructionRepository(uow.session)
            existing = await repo.list_by_context(context)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Project already has instructions. Delete existing ones first or add manually."
                )
            created = []
            for default_inst in get_default_instructions():
                inst = await repo.create_instruction(context, default_inst)
                created.append(inst)
            await uow.commit()
            logger.info("Seeded default bot instructions", count=len(created), project_id=str(context.project_id))
            return created

    # --- Auto Response Templates ---

    async def list_auto_response_templates(
        self, context: TenantContext, active_only: bool = False
    ) -> List[AutoResponseTemplate]:
        async with self.uow as uow:
            repo = AutoResponseTemplateRepository(uow.session)
            return await repo.list_by_context(context, active_only=active_only)

    async def create_auto_response_template(
        self, context: TenantContext, data: Dict[str, Any]
    ) -> AutoResponseTemplate:
        async with self.uow as uow:
            repo = AutoResponseTemplateRepository(uow.session)
            template = await repo.create_template(context, data)
            await uow.commit()
            await uow.session.refresh(template)
            logger.info("Auto response template created", template_id=str(template.id), project_id=str(context.project_id))
            return template

    # --- Knowledge Base Items ---

    async def list_knowledge_items(
        self, context: TenantContext, active_only: bool = False
    ) -> List[KnowledgeBase]:
        async with self.uow as uow:
            repo = KnowledgeBaseRepository(uow.session)
            return await repo.list_by_context(context, active_only=active_only)

    async def get_knowledge_item(
        self, item_id: UUID, context: TenantContext
    ) -> KnowledgeBase:
        async with self.uow as uow:
            repo = KnowledgeBaseRepository(uow.session)
            item = await repo.get_by_context(item_id, context)
            if not item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Knowledge item not found"
                )
            return item

    async def create_knowledge_item(
        self, context: TenantContext, data: Dict[str, Any]
    ) -> KnowledgeBase:
        async with self.uow as uow:
            repo = KnowledgeBaseRepository(uow.session)
            item = await repo.create_item(context, data)
            await uow.commit()
            await uow.session.refresh(item)
            logger.info("Knowledge item created", item_id=str(item.id), project_id=str(context.project_id))
            return item

    async def update_knowledge_item(
        self, item_id: UUID, context: TenantContext, update_data: Dict[str, Any]
    ) -> KnowledgeBase:
        async with self.uow as uow:
            repo = KnowledgeBaseRepository(uow.session)
            item = await repo.update_by_context(item_id, context, update_data)
            if not item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Knowledge item not found"
                )
            await uow.commit()
            await uow.session.refresh(item)
            logger.info("Knowledge item updated", item_id=str(item.id), project_id=str(context.project_id))
            return item

    async def delete_knowledge_item(
        self, item_id: UUID, context: TenantContext
    ) -> None:
        async with self.uow as uow:
            repo = KnowledgeBaseRepository(uow.session)
            deleted = await repo.delete_by_context(item_id, context)
            if not deleted:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Knowledge item not found"
                )
            await uow.commit()
            logger.info("Knowledge item deleted", item_id=str(item_id), project_id=str(context.project_id))

    # --- Analytics / Usage ---

    async def get_ai_usage_stats(self, context: TenantContext, days: int = 30) -> Dict[str, Any]:
        async with self.uow as uow:
            start_date = datetime.utcnow() - timedelta(days=days)
            query = select(
                func.count(APILog.id).label("total_calls"),
                func.sum(APILog.ai_tokens_used).label("total_tokens"),
                func.sum(APILog.cost_estimate).label("total_cost")
            ).where(
                APILog.project_id == context.project_id,
                APILog.created_at >= start_date
            )
            result = await uow.session.execute(query)
            row = result.first()
            total_calls = row.total_calls or 0 if row else 0
            total_tokens = row.total_tokens or 0 if row else 0
            total_cost = float(row.total_cost or 0.0) if row else 0.0
            return {
                "period_days": days,
                "total_api_calls": total_calls,
                "total_tokens_used": total_tokens,
                "total_cost_usd": total_cost,
                "average_cost_per_call": float(total_cost / total_calls) if total_calls > 0 else 0.0
            }
