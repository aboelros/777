from typing import Dict, Any, Optional, List
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
import structlog
import re

from app.core.context import TenantContext
from app.domains.social.models import SocialMediaComment, SocialMediaPost
from app.domains.social.repository import SocialMediaCommentRepository, SocialMediaPostRepository
from app.domains.ai.models import AutoResponseTemplate
from app.domains.ai.providers.gemini import GeminiClient
from app.services.enhanced_ai_service import EnhancedAIService

logger = structlog.get_logger(__name__)


class SocialMediaAutoResponder:
    """Handles comment reply generation and automated responses."""

    def __init__(self, db: AsyncSession, context: TenantContext):
        self.db = db
        self.context = context
        self.comment_repo = SocialMediaCommentRepository(db, context)
        self.post_repo = SocialMediaPostRepository(db, context)
        self.gemini_client = GeminiClient()
        self.ai_service = EnhancedAIService(db, context.project_id)

    async def generate_comment_reply(
        self,
        comment_id: UUID,
        use_templates: bool = True,
        auto_send: bool = False
    ) -> Dict[str, Any]:
        """Generate an AI or template reply for a comment within tenant boundary."""
        comment = await self.comment_repo.get_by_context(comment_id)
        if not comment:
            raise ValueError(f"Comment {comment_id} not found")

        template_response = None
        if use_templates:
            template_response = await self._find_matching_template(
                comment_content=comment.content,
                platform=comment.platform,
                intent=comment.intent
            )

        if template_response:
            response = await self._personalize_template(template=template_response, comment=comment)
            method = "template"
        else:
            response = await self._generate_custom_reply(comment)
            method = "ai_generated"

        comment.response_content = response
        comment.auto_generated = True

        if auto_send:
            comment.responded = True
            comment.response_sent_at = datetime.utcnow()

        await self.comment_repo.update_comment(comment)

        logger.info("Comment reply generated", comment_id=str(comment_id), method=method, auto_send=auto_send)

        return {
            "comment_id": str(comment_id),
            "response": response,
            "method": method,
            "auto_sent": auto_send,
            "requires_approval": not auto_send
        }

    async def auto_respond_to_comments(
        self,
        post_id: Optional[UUID] = None,
        max_responses: int = 10
    ) -> Dict[str, Any]:
        """Automatically respond to pending comments for the tenant."""
        post_external_id = None
        if post_id:
            post = await self.post_repo.get_by_context(post_id)
            if not post:
                raise ValueError(f"Post {post_id} not found")
            post_external_id = post.external_id

        comments = await self.comment_repo.get_unresponded(
            context=self.context,
            post_external_id=post_external_id,
            limit=max_responses
        )

        responses_sent = 0
        responses_generated = []

        for comment in comments:
            try:
                reply_result = await self.generate_comment_reply(
                    comment_id=comment.id,
                    use_templates=True,
                    auto_send=True
                )
                responses_sent += 1
                responses_generated.append(reply_result)
            except Exception as e:
                logger.error("Failed to respond to comment", comment_id=str(comment.id), error=str(e))

        return {
            "responses_sent": responses_sent,
            "total_pending": len(comments),
            "responses": responses_generated
        }

    async def _find_matching_template(
        self,
        comment_content: str,
        platform: str,
        intent: Optional[str] = None
    ) -> Optional[AutoResponseTemplate]:
        query = select(AutoResponseTemplate).where(
            AutoResponseTemplate.project_id == self.context.project_id,
            AutoResponseTemplate.is_active == True
        )
        result = await self.db.execute(query)
        templates = result.scalars().all()

        content_lower = comment_content.lower()
        for t in templates:
            if t.keywords:
                for kw in t.keywords:
                    if kw.lower() in content_lower:
                        return t
            if intent and t.trigger_event == intent:
                return t
        return None

    async def _personalize_template(
        self,
        template: AutoResponseTemplate,
        comment: SocialMediaComment
    ) -> str:
        text = template.template_text
        if comment.author_username:
            text = text.replace("{username}", f"@{comment.author_username}")
            text = text.replace("{name}", comment.author_username)
        else:
            text = re.sub(r"@?\{username\}", "there", text)
            text = re.sub(r"\{name\}", "there", text)
        return text

    async def _generate_custom_reply(self, comment: SocialMediaComment) -> str:
        prompt = f"""Generate a brief, friendly response to this {comment.platform} comment:
Comment: "{comment.content}"
From: {comment.author_username or 'User'}
Keep it under 150 characters."""
        try:
            response = await self.gemini_client.generate_response(prompt=prompt, use_functions=False, temperature=0.7)
            return response.get("text", "Thank you for reaching out!").strip()
        except Exception as e:
            logger.error("Failed to generate custom reply", error=str(e))
            return "Thank you for your comment!"
