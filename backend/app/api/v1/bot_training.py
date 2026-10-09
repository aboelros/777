"""
Bot Training & Customization API endpoints
"""

from typing import Any, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import structlog

from app.core.database import get_db
from app.core.context import TenantContext
from app.api.dependencies.tenant import get_tenant_context
from app.core.uow import UnitOfWork
from app.domains.ai.service import AIService
from app.domains.products.repository import ProductRepository

router = APIRouter()
logger = structlog.get_logger(__name__)


async def get_ai_service(db: AsyncSession = Depends(get_db)) -> AIService:
    return AIService(UnitOfWork(db))


class BotInstructionCreate(BaseModel):
    title: str
    instruction: str
    category: Optional[str] = None
    priority: int = 0
    active_for_platforms: List[str] = []
    active_for_topics: List[str] = []
    examples: List[dict] = []


class BotInstructionUpdate(BaseModel):
    title: Optional[str] = None
    instruction: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[int] = None
    active_for_platforms: Optional[List[str]] = None
    active_for_topics: Optional[List[str]] = None
    examples: Optional[List[dict]] = None
    is_active: Optional[bool] = None


class AutoResponseTemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    trigger_keywords: List[str] = []
    trigger_platforms: List[str] = []
    trigger_intent: Optional[str] = None
    response_template: str
    variations: List[str] = []
    use_ai_enhancement: bool = True
    requires_approval: bool = False


@router.get("/{project_id}/instructions")
async def list_bot_instructions(
    project_id: UUID,
    active_only: bool = True,
    context: TenantContext = Depends(get_tenant_context),
    service: AIService = Depends(get_ai_service)
) -> Any:
    """List all bot instructions for a project."""
    instructions = await service.list_bot_instructions(context, active_only=active_only)
    return {
        "instructions": [
            {
                "id": str(i.id),
                "title": i.title,
                "instruction": i.instruction,
                "category": i.category,
                "priority": i.priority,
                "active_for_platforms": i.active_for_platforms,
                "active_for_topics": i.active_for_topics,
                "examples": i.examples,
                "is_active": i.is_active,
                "created_at": i.created_at.isoformat() if i.created_at else None,
            }
            for i in instructions
        ],
        "total": len(instructions)
    }


@router.post("/{project_id}/instructions")
async def create_bot_instruction(
    project_id: UUID,
    instruction: BotInstructionCreate,
    context: TenantContext = Depends(get_tenant_context),
    service: AIService = Depends(get_ai_service)
) -> Any:
    """Create a new bot instruction."""
    new_inst = await service.create_bot_instruction(context, instruction.model_dump())
    return {
        "success": True,
        "message": "Instruction created successfully",
        "instruction": {
            "id": str(new_inst.id),
            "title": new_inst.title,
            "instruction": new_inst.instruction,
            "category": new_inst.category,
            "priority": new_inst.priority,
            "is_active": new_inst.is_active,
            "created_at": new_inst.created_at.isoformat()
        }
    }


@router.put("/{project_id}/instructions/{instruction_id}")
async def update_bot_instruction(
    project_id: UUID,
    instruction_id: UUID,
    instruction_update: BotInstructionUpdate,
    context: TenantContext = Depends(get_tenant_context),
    service: AIService = Depends(get_ai_service)
) -> Any:
    """Update a bot instruction."""
    await service.update_bot_instruction(
        instruction_id, context, instruction_update.model_dump(exclude_unset=True)
    )
    return {"message": "Instruction updated successfully"}


@router.delete("/{project_id}/instructions/{instruction_id}")
async def delete_bot_instruction(
    project_id: UUID,
    instruction_id: UUID,
    context: TenantContext = Depends(get_tenant_context),
    service: AIService = Depends(get_ai_service)
) -> Any:
    """Delete a bot instruction."""
    await service.delete_bot_instruction(instruction_id, context)
    return {"message": "Instruction deleted successfully"}


@router.get("/{project_id}/templates")
async def list_auto_response_templates(
    project_id: UUID,
    active_only: bool = True,
    context: TenantContext = Depends(get_tenant_context),
    service: AIService = Depends(get_ai_service)
) -> Any:
    """List all auto-response templates."""
    templates = await service.list_auto_response_templates(context, active_only=active_only)
    return {
        "templates": [
            {
                "id": str(t.id),
                "name": t.name,
                "description": t.description,
                "trigger_keywords": t.trigger_keywords,
                "trigger_platforms": t.trigger_platforms,
                "trigger_intent": t.trigger_intent,
                "response_template": t.response_template,
                "variations": t.variations,
                "use_ai_enhancement": t.use_ai_enhancement,
                "requires_approval": t.requires_approval,
                "times_used": t.times_used,
                "success_rate": t.success_rate,
                "is_active": t.is_active,
            }
            for t in templates
        ],
        "total": len(templates)
    }


@router.post("/{project_id}/templates")
async def create_auto_response_template(
    project_id: UUID,
    template: AutoResponseTemplateCreate,
    context: TenantContext = Depends(get_tenant_context),
    service: AIService = Depends(get_ai_service)
) -> Any:
    """Create a new auto-response template."""
    new_template = await service.create_auto_response_template(context, template.model_dump())
    return {
        "id": str(new_template.id),
        "message": "Template created successfully"
    }


@router.get("/{project_id}/knowledge-base")
async def get_bot_knowledge_base(
    project_id: UUID,
    context: TenantContext = Depends(get_tenant_context),
    service: AIService = Depends(get_ai_service),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get complete bot knowledge base for this project (all instructions + products)."""
    instructions = await service.list_bot_instructions(context, active_only=True)
    prod_repo = ProductRepository(db)
    products = await prod_repo.get_project_products(context.project_id)

    return {
        "instructions": [
            {
                "title": i.title,
                "instruction": i.instruction,
                "category": i.category,
                "priority": i.priority,
                "examples": i.examples,
            }
            for i in instructions
        ],
        "products": [
            {
                "name": p.name,
                "description": p.description,
                "price": p.price,
                "currency": p.currency,
                "in_stock": p.in_stock,
                "faq": p.faq,
                "keywords": p.keywords,
            }
            for p in products
        ],
        "total_instructions": len(instructions),
        "total_products": len(products)
    }


@router.post("/{project_id}/seed-instructions")
async def seed_default_instructions(
    project_id: UUID,
    context: TenantContext = Depends(get_tenant_context),
    service: AIService = Depends(get_ai_service)
) -> Any:
    """Seed project with amazing default bot instructions."""
    created = await service.seed_default_instructions(context)
    return {
        "success": True,
        "message": f"🚀 Created {len(created)} bot instructions!",
        "instructions_created": len(created),
        "categories": list(set(inst.category for inst in created if inst.category))
    }
