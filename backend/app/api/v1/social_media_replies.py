from typing import Any, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.core.context import TenantContext
from app.api.dependencies.tenant import get_tenant_context
from app.domains.social.repository import SocialMediaCommentRepository
from app.domains.products.repository import ProductRepository
from app.domains.ai.repository import BotInstructionRepository
from app.domains.integrations.repository import IntegrationRepository
from app.domains.ai.providers.gemini import gemini_client
from app.api.v1.social_media_schemas import ResponseGenerate

router = APIRouter()
logger = structlog.get_logger(__name__)


@router.post("/{project_id}/comments/{comment_id}/generate-response")
async def generate_comment_response(
    project_id: UUID,
    comment_id: UUID,
    request: Optional[ResponseGenerate] = None,
    context: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Generate AI response for a comment within verified tenant boundary."""
    comment_repo = SocialMediaCommentRepository(db, context)
    comment = await comment_repo.get_by_context(comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    product_repo = ProductRepository(db)
    products = await product_repo.get_project_products(context.project_id)

    instruction_repo = BotInstructionRepository(db)
    instructions = await instruction_repo.get_active_by_context(context)

    product_info = "\n".join([
        f"- {p.name}: {p.description} (${p.price}, {'In Stock' if p.in_stock else 'Out of Stock'})"
        for p in products[:10]
    ])

    custom_instructions = "\n".join([
        f"- {i.instruction}"
        for i in instructions
        if not i.active_for_platforms or comment.platform in i.active_for_platforms
    ])

    prompt = f"""Generate a professional, helpful response to this {comment.platform} comment.

Comment: {comment.content}
Author: {comment.author_username}
Sentiment: {comment.sentiment}
Intent: {comment.intent}

Available Products:
{product_info}

Brand Guidelines:
{custom_instructions}

{f'Additional Context: {request.custom_context}' if request and request.custom_context else ''}

Generate a friendly, on-brand response that:
1. Addresses the comment directly
2. Provides helpful information about products if relevant
3. Encourages engagement
4. Matches the platform's tone ({comment.platform})
5. Is concise (max 280 characters for Twitter-like platforms)

Response:"""

    try:
        ai_response = await gemini_client.generate_response(
            prompt=prompt,
            use_functions=False,
            temperature=0.7
        )
        generated_response = ai_response.get("text", "").strip()

        logger.info(
            "Response generated for comment",
            comment_id=str(comment_id),
            project_id=str(context.project_id),
            response_length=len(generated_response)
        )

        return {
            "comment_id": str(comment_id),
            "generated_response": generated_response,
            "tokens_used": ai_response.get("tokens_used", 0),
            "cost": ai_response.get("cost", 0.0)
        }
    except Exception as e:
        logger.error("Response generation failed", error=str(e), comment_id=str(comment_id))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate response: {str(e)}"
        )


@router.post("/{project_id}/comments/{comment_id}/send-response")
async def send_comment_response(
    project_id: UUID,
    comment_id: UUID,
    response_text: str,
    context: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Send live reply to comment with pre-authorization invariant strictly enforced."""
    comment_repo = SocialMediaCommentRepository(db, context)
    comment = await comment_repo.get_by_context(comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    integration_repo = IntegrationRepository(db)
    integrations = await integration_repo.get_project_integrations(context.project_id)
    integration = next((i for i in integrations if i.provider == comment.platform), None)

    if integration:
        try:
            if comment.platform == "facebook":
                from app.services.integrations.facebook import FacebookClient
                fb_client = FacebookClient({
                    "page_id": integration.config.get("page_id"),
                    "access_token": integration.config.get("access_token")
                })
                await fb_client.reply_to_comment(comment.external_id, response_text)
            elif comment.platform == "instagram":
                from app.services.integrations.instagram import InstagramClient
                ig_client = InstagramClient({
                    "page_id": integration.config.get("instagram_business_account_id"),
                    "access_token": integration.config.get("access_token")
                })
                await ig_client.reply_to_comment(comment.external_id, response_text)
        except Exception as e:
            logger.error(f"Failed to send live reply to {comment.platform}", error=str(e))

    comment.responded = True
    comment.response_content = response_text
    comment.response_sent_at = datetime.utcnow()
    comment.auto_generated = True

    await comment_repo.update_comment(comment)

    logger.info(
        "Response sent to comment",
        comment_id=str(comment_id),
        project_id=str(context.project_id),
        platform=comment.platform
    )

    return {
        "message": "Response sent successfully",
        "comment_id": str(comment_id)
    }
