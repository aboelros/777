"""
Social Media Post and Comment Monitoring API endpoints for Enhanced Bot.
"""

from typing import Any, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from pydantic import BaseModel
import structlog

from app.core.database import get_db
from app.core.context import TenantContext
from app.api.dependencies.tenant import get_tenant_context
from app.services.social_media_monitor import SocialMediaMonitor

social_router = APIRouter()
logger = structlog.get_logger(__name__)


class CommentReplyRequest(BaseModel):
    """Request to generate comment reply."""
    comment_id: UUID
    use_templates: bool = True
    auto_send: bool = False


class PostAnalysisRequest(BaseModel):
    """Request to analyze post."""
    post_id: UUID
    analyze_comments: bool = True


class AutoResponseConfig(BaseModel):
    """Configure auto-response settings."""
    max_responses_per_run: int = 10
    post_id: Optional[UUID] = None


@social_router.post("/{project_id}/posts/analyze")
async def analyze_social_post(
    project_id: UUID,
    request: PostAnalysisRequest,
    context: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Analyze a social media post using AI.
    """
    monitor = SocialMediaMonitor(db, context.project_id)
    try:
        analysis = await monitor.analyze_post(
            post_id=request.post_id,
            fetch_comments=request.analyze_comments
        )
        return {
            "success": True,
            "analysis": analysis
        }
    except Exception as e:
        logger.error("Failed to analyze post", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze post: {str(e)}"
        )


@social_router.post("/{project_id}/comments/generate-reply")
async def generate_comment_reply(
    project_id: UUID,
    request: CommentReplyRequest,
    context: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Generate AI-powered reply to a social media comment.
    """
    monitor = SocialMediaMonitor(db, context.project_id)
    try:
        reply = await monitor.generate_comment_reply(
            comment_id=request.comment_id,
            use_templates=request.use_templates,
            auto_send=request.auto_send
        )
        return {
            "success": True,
            **reply
        }
    except Exception as e:
        logger.error("Failed to generate reply", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate reply: {str(e)}"
        )


@social_router.post("/{project_id}/comments/auto-respond")
async def auto_respond_comments(
    project_id: UUID,
    config: AutoResponseConfig,
    context: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Automatically respond to pending comments.
    """
    monitor = SocialMediaMonitor(db, context.project_id)
    try:
        results = await monitor.auto_respond_to_comments(
            post_id=config.post_id,
            max_responses=config.max_responses_per_run
        )
        return {
            "success": True,
            **results
        }
    except Exception as e:
        logger.error("Failed to auto-respond", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to auto-respond: {str(e)}"
        )


@social_router.post("/{project_id}/posts/{post_id}/learn")
async def learn_from_post(
    project_id: UUID,
    post_id: UUID,
    context: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Learn from high-performing post and update business context.
    """
    monitor = SocialMediaMonitor(db, context.project_id)
    try:
        learnings = await monitor.learn_from_post_performance(post_id)
        return {
            "success": True,
            **learnings
        }
    except Exception as e:
        logger.error("Failed to learn from post", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to learn from post: {str(e)}"
        )


@social_router.get("/{project_id}/insights/overview")
async def get_ai_insights_overview(
    project_id: UUID,
    context: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get comprehensive AI insights overview.
    """
    from app.domains.messages.models import ConversationHistory
    from app.domains.customers.models import CustomerProfile
    from app.domains.projects.models import BusinessContext
    from app.domains.social.models import SocialMediaComment

    result = await db.execute(
        select(func.count(ConversationHistory.id))
        .where(ConversationHistory.project_id == context.project_id)
    )
    conversation_count = result.scalar() or 0

    result = await db.execute(
        select(func.count(CustomerProfile.id))
        .where(CustomerProfile.project_id == context.project_id)
    )
    customer_count = result.scalar() or 0

    result = await db.execute(
        select(func.count(BusinessContext.id))
        .where(BusinessContext.project_id == context.project_id)
    )
    context_count = result.scalar() or 0

    result = await db.execute(
        select(func.count(SocialMediaComment.id))
        .where(
            and_(
                SocialMediaComment.project_id == context.project_id,
                SocialMediaComment.responded == True,
                SocialMediaComment.auto_generated == True
            )
        )
    )
    auto_response_count = result.scalar() or 0

    result = await db.execute(
        select(func.count(SocialMediaComment.id))
        .where(
            and_(
                SocialMediaComment.project_id == context.project_id,
                SocialMediaComment.responded == False
            )
        )
    )
    pending_comments = result.scalar() or 0

    return {
        "conversations_tracked": conversation_count,
        "customer_profiles": customer_count,
        "business_contexts": context_count,
        "comments_auto_responded": auto_response_count,
        "pending_comments": pending_comments,
        "ai_learning_active": context_count > 0
    }
