"""
Bot Training & Customization API endpoints
"""

from typing import Any, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.db.models import Project, BotInstruction
from app.api.v1.projects import verify_project_access
from app.core.default_instructions import get_default_instructions
from pydantic import BaseModel

router = APIRouter()
logger = structlog.get_logger(__name__)


class BotInstructionCreate(BaseModel):
    title: str
    instruction: str
    category: str | None = None
    priority: int = 0
    active_for_platforms: List[str] = []
    active_for_topics: List[str] = []
    examples: List[dict] = []


class BotInstructionUpdate(BaseModel):
    title: str | None = None
    instruction: str | None = None
    category: str | None = None
    priority: int | None = None
    active_for_platforms: List[str] | None = None
    active_for_topics: List[str] | None = None
    examples: List[dict] | None = None
    is_active: bool | None = None


class AutoResponseTemplateCreate(BaseModel):
    name: str
    description: str | None = None
    trigger_keywords: List[str] = []
    trigger_platforms: List[str] = []
    trigger_intent: str | None = None
    response_template: str
    variations: List[str] = []
    use_ai_enhancement: bool = True
    requires_approval: bool = False


async def verify_project_access(project_id: UUID, user_id: str, db: AsyncSession) -> Project:
    """Helper to verify user has access to project."""
    result = await db.execute(
        select(Project)
        .where(Project.id == project_id)
        .where(Project.owner_id == UUID(user_id))
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or access denied"
        )
    
    return project


@router.get("/{project_id}/instructions")
async def list_bot_instructions(
    project_id: UUID,
    active_only: bool = True,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """List all bot instructions for a project."""
    await verify_project_access(project_id, user_id, db)
    
    query = select(BotInstruction).where(BotInstruction.project_id == project_id)
    
    if active_only:
        query = query.where(BotInstruction.is_active == True)
    
    query = query.order_by(BotInstruction.priority.desc(), BotInstruction.created_at.desc())
    
    result = await db.execute(query)
    instructions = result.scalars().all()
    
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
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Create a new bot instruction."""
    try:
        await verify_project_access(project_id, user_id, db)
        
        new_instruction = BotInstruction(
            project_id=project_id,
            title=instruction.title,
            instruction=instruction.instruction,
            category=instruction.category,
            priority=instruction.priority,
            active_for_platforms=instruction.active_for_platforms or [],
            active_for_topics=instruction.active_for_topics or [],
            examples=instruction.examples or [],
        )
        
        db.add(new_instruction)
        await db.commit()
        await db.refresh(new_instruction)
        
        logger.info("Bot instruction created", instruction_id=str(new_instruction.id))
        
        return {
            "success": True,
            "message": "Instruction created successfully",
            "instruction": {
                "id": str(new_instruction.id),
                "title": new_instruction.title,
                "instruction": new_instruction.instruction,
                "category": new_instruction.category,
                "priority": new_instruction.priority,
                "is_active": new_instruction.is_active,
                "created_at": new_instruction.created_at.isoformat()
            }
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions (like access denied)
        raise
    except Exception as e:
        logger.error("Failed to create bot instruction", error=str(e), project_id=str(project_id))
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create instruction: {str(e)}"
        )


@router.put("/{project_id}/instructions/{instruction_id}")
async def update_bot_instruction(
    project_id: UUID,
    instruction_id: UUID,
    instruction_update: BotInstructionUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Update a bot instruction."""
    await verify_project_access(project_id, user_id, db)
    
    result = await db.execute(
        select(BotInstruction)
        .where(BotInstruction.id == instruction_id)
        .where(BotInstruction.project_id == project_id)
    )
    instruction = result.scalar_one_or_none()
    
    if not instruction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instruction not found"
        )
    
    update_data = instruction_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(instruction, field, value)
    
    await db.commit()
    
    logger.info("Bot instruction updated", instruction_id=str(instruction_id))
    
    return {"message": "Instruction updated successfully"}


@router.delete("/{project_id}/instructions/{instruction_id}")
async def delete_bot_instruction(
    project_id: UUID,
    instruction_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Delete a bot instruction."""
    await verify_project_access(project_id, user_id, db)
    
    result = await db.execute(
        select(BotInstruction)
        .where(BotInstruction.id == instruction_id)
        .where(BotInstruction.project_id == project_id)
    )
    instruction = result.scalar_one_or_none()
    
    if not instruction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instruction not found"
        )
    
    await db.delete(instruction)
    await db.commit()
    
    logger.info("Bot instruction deleted", instruction_id=str(instruction_id))
    
    return {"message": "Instruction deleted successfully"}


@router.get("/{project_id}/templates")
async def list_auto_response_templates(
    project_id: UUID,
    active_only: bool = True,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """List all auto-response templates."""
    await verify_project_access(project_id, user_id, db)
    
    query = select(AutoResponseTemplate).where(AutoResponseTemplate.project_id == project_id)
    
    if active_only:
        query = query.where(AutoResponseTemplate.is_active == True)
    
    result = await db.execute(query)
    templates = result.scalars().all()
    
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
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Create a new auto-response template."""
    await verify_project_access(project_id, user_id, db)
    
    new_template = AutoResponseTemplate(
        project_id=project_id,
        name=template.name,
        description=template.description,
        trigger_keywords=template.trigger_keywords,
        trigger_platforms=template.trigger_platforms,
        trigger_intent=template.trigger_intent,
        response_template=template.response_template,
        variations=template.variations,
        use_ai_enhancement=template.use_ai_enhancement,
        requires_approval=template.requires_approval,
    )
    
    db.add(new_template)
    await db.commit()
    await db.refresh(new_template)
    
    logger.info("Auto-response template created", template_id=str(new_template.id))
    
    return {
        "id": str(new_template.id),
        "message": "Template created successfully"
    }


@router.get("/{project_id}/knowledge-base")
async def get_bot_knowledge_base(
    project_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get complete bot knowledge base for this project (all instructions + products)."""
    await verify_project_access(project_id, user_id, db)
    
    # Get instructions
    instructions_result = await db.execute(
        select(BotInstruction)
        .where(BotInstruction.project_id == project_id)
        .where(BotInstruction.is_active == True)
        .order_by(BotInstruction.priority.desc())
    )
    instructions = instructions_result.scalars().all()
    
    # Get products (for product knowledge)
    from app.db.models import Product
    products_result = await db.execute(
        select(Product)
        .where(Product.project_id == project_id)
        .where(Product.is_active == True)
    )
    products = products_result.scalars().all()
    
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
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Seed project with amazing default bot instructions.
    
    This will create the BEST AI assistant experience ever!
    """
    try:
        await verify_project_access(project_id, user_id, db)
        
        # Check if instructions already exist
        result = await db.execute(
            select(BotInstruction).where(BotInstruction.project_id == project_id)
        )
        existing_instructions = result.scalars().all()
        
        if existing_instructions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project already has instructions. Delete existing ones first or add manually."
            )
        
        # Get default instructions
        default_instructions = get_default_instructions()
        
        # Create instruction records
        created_instructions = []
        for inst_data in default_instructions:
            instruction = BotInstruction(
                project_id=project_id,
                title=inst_data["title"],
                instruction=inst_data["instruction"],
                category=inst_data["category"],
                priority=inst_data["priority"],
                active_for_platforms=inst_data["active_for_platforms"],
                active_for_topics=inst_data.get("active_for_topics", []),
                examples=inst_data["examples"],
                is_active=True
            )
            db.add(instruction)
            created_instructions.append(instruction)
        
        await db.commit()
        
        logger.info(
            "Default instructions seeded",
            project_id=str(project_id),
            count=len(created_instructions)
        )
        
        return {
            "success": True,
            "message": f"🚀 Amazing! Created {len(created_instructions)} world-class bot instructions!",
            "instructions_created": len(created_instructions),
            "categories": list(set(inst["category"] for inst in default_instructions))
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions (like access denied or already exists)
        raise
    except Exception as e:
        logger.error("Failed to seed instructions", error=str(e), project_id=str(project_id))
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to seed instructions: {str(e)}"
        )
