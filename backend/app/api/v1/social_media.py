from typing import Any, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.core.context import TenantContext
from app.api.dependencies.tenant import get_tenant_context
from app.domains.social.models import SocialMediaComment
from app.domains.social.repository import SocialMediaCommentRepository
from app.domains.ai.providers.gemini import gemini_client
from app.api.v1.social_media_schemas import CommentCreate
from app.api.v1.social_media_accounts import router as accounts_router
from app.api.v1.social_media_replies import router as replies_router

router = APIRouter()
router.include_router(accounts_router)
router.include_router(replies_router)

logger = structlog.get_logger(__name__)


@router.get("/{project_id}/comments")
async def list_comments(
    project_id: UUID,
    platform: Optional[str] = None,
    responded: Optional[bool] = None,
    skip: int = 0,
    limit: int = 50,
    context: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """List social media comments within verified tenant boundary."""
    comment_repo = SocialMediaCommentRepository(db, context)
    comments = await comment_repo.list_by_context(
        context=context,
        platform=platform,
        responded=responded,
        skip=skip,
        limit=limit
    )

    return {
        "comments": [
            {
                "id": str(c.id),
                "platform": c.platform,
                "external_id": c.external_id,
                "post_id": c.post_id,
                "content": c.content,
                "text": c.content,
                "author_username": c.author_username,
                "author_name": c.author_username or "Customer",
                "responded": c.responded,
                "response_content": c.response_content,
                "response_text": c.response_content,
                "response_sent_at": c.response_sent_at.isoformat() if c.response_sent_at else None,
                "auto_generated": c.auto_generated,
                "sentiment": c.sentiment,
                "intent": c.intent,
                "requires_human": c.requires_human,
                "priority": c.priority,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in comments
        ],
        "total": len(comments)
    }


@router.post("/{project_id}/comments")
async def create_comment(
    project_id: UUID,
    comment: CommentCreate,
    context: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Create a new comment within verified tenant boundary."""
    comment_repo = SocialMediaCommentRepository(db, context)
    existing = await comment_repo.find_existing(comment.platform, comment.external_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment already exists"
        )

    try:
        sentiment_analysis = await gemini_client.analyze_sentiment(comment.content)
        sentiment = sentiment_analysis.get("sentiment", "neutral")
        content_lower = comment.content.lower()
        if any(word in content_lower for word in ["price", "cost", "how much"]):
            intent = "pricing_inquiry"
        elif any(word in content_lower for word in ["shipping", "deliver", "ship"]):
            intent = "shipping_inquiry"
        elif any(word in content_lower for word in ["available", "stock", "buy"]):
            intent = "product_inquiry"
        else:
            intent = "general"
    except Exception as e:
        logger.warning("Sentiment analysis failed", error=str(e))
        sentiment = "neutral"
        intent = "general"

    new_comment = SocialMediaComment(
        project_id=context.project_id,
        platform=comment.platform,
        external_id=comment.external_id,
        post_id=comment.post_id,
        content=comment.content,
        author_username=comment.author_username,
        author_id=comment.author_id,
        sentiment=sentiment,
        intent=intent,
    )

    created = await comment_repo.create_comment(new_comment)
    logger.info("Social media comment created", comment_id=str(created.id), platform=comment.platform)

    return {
        "id": str(created.id),
        "sentiment": sentiment,
        "intent": intent,
        "message": "Comment created successfully"
    }


@router.get("/{project_id}/stats")
async def get_comment_stats(
    project_id: UUID,
    context: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get social media comment statistics within verified tenant boundary."""
    comment_repo = SocialMediaCommentRepository(db, context)
    return await comment_repo.get_comment_stats(context=context)
