"""
Business context endpoints for Enhanced AI Bot.
"""

from typing import Any, Optional
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.core.context import TenantContext
from app.api.dependencies.tenant import get_tenant_context
from app.services.enhanced_ai_service import EnhancedAIService
from app.domains.projects.models import BusinessContext
from app.api.v1.enhanced_bot_schemas import BusinessContextCreate

context_router = APIRouter()
logger = structlog.get_logger(__name__)


@context_router.post("/{project_id}/context/create")
async def create_business_context(
    project_id: UUID,
    biz_context: BusinessContextCreate,
    context: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Create business-specific context for AI to use.
    """
    business_context = BusinessContext(
        project_id=context.project_id,
        context_type=biz_context.context_type,
        context_key=biz_context.context_key,
        title=biz_context.title,
        content=biz_context.content,
        tags=biz_context.tags,
        active_for_platforms=biz_context.platforms,
        learned_from="manual",
        confidence_score=1.0
    )

    db.add(business_context)
    await db.commit()
    await db.refresh(business_context)

    logger.info("Business context created", context_id=str(business_context.id))

    return {
        "success": True,
        "context_id": str(business_context.id),
        "message": "Business context created successfully"
    }


@context_router.get("/{project_id}/context/list")
async def list_business_contexts(
    project_id: UUID,
    context_type: Optional[str] = None,
    platform: Optional[str] = None,
    context: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    List all business contexts for the project.
    """
    ai_service = EnhancedAIService(db, context.project_id)
    contexts = await ai_service.get_business_context(
        context_type=context_type,
        platform=platform
    )

    return {
        "total": len(contexts),
        "contexts": [
            {
                "id": str(c.id),
                "type": c.context_type,
                "key": c.context_key,
                "title": c.title,
                "content": c.content[:200] + "..." if len(c.content) > 200 else c.content,
                "tags": c.tags,
                "times_used": c.times_used,
                "relevance_score": c.relevance_score,
                "platforms": c.active_for_platforms
            }
            for c in contexts
        ]
    }
