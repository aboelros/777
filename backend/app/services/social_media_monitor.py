from typing import List, Dict, Any, Optional, Union
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.context import TenantContext
from app.domains.ai.providers.gemini import GeminiClient
from app.services.enhanced_ai_service import EnhancedAIService
from app.domains.social.models import SocialMediaPost, SocialMediaComment
from app.domains.social.repository import SocialMediaPostRepository, SocialMediaCommentRepository
from app.domains.projects.models import BusinessContext
from app.services.social_media_analyzer import (
    analyze_post_content,
    analyze_comments_batch,
    assess_comment_priority,
    extract_post_learnings,
)
from app.services.social_media_auto_responder import SocialMediaAutoResponder

logger = structlog.get_logger(__name__)


class SocialMediaMonitor:
    """Monitor social media posts and comments for automated engagement with strict tenant boundaries."""

    def __init__(self, db: AsyncSession, project_id: Union[UUID, TenantContext]):
        self.db = db
        if isinstance(project_id, TenantContext):
            self.context = project_id
        else:
            self.context = TenantContext(project_id=project_id, roles=["system"])
        self.project_id = self.context.project_id
        self.gemini_client = GeminiClient()
        self.ai_service = EnhancedAIService(db, self.project_id)
        self.post_repo = SocialMediaPostRepository(db, self.context)
        self.comment_repo = SocialMediaCommentRepository(db, self.context)
        self.auto_responder = SocialMediaAutoResponder(db, self.context)

    async def analyze_post(self, post_id: UUID, fetch_comments: bool = True) -> Dict[str, Any]:
        """Analyze a social media post using AI within tenant boundary."""
        post = await self.post_repo.get_by_context(post_id)
        if not post:
            raise ValueError(f"Post {post_id} not found")

        analysis = await analyze_post_content(
            gemini_client=self.gemini_client,
            content=post.content or "",
            platform=post.platform,
            media_type=post.media_type
        )

        post.ai_analyzed = True
        post.sentiment = analysis.get("overall_sentiment")
        post.topics = analysis.get("topics", [])
        post.keywords = analysis.get("keywords", [])
        post.ai_summary = analysis.get("summary")

        if post.likes_count or post.comments_count or post.shares_count:
            total_engagement = (
                (post.likes_count or 0) +
                ((post.comments_count or 0) * 2) +
                ((post.shares_count or 0) * 3)
            )
            followers = post.extra_data.get("follower_count", 1000) if post.extra_data else 1000
            post.engagement_rate = (total_engagement / max(followers, 1)) * 100

        await self.post_repo.update_post(post)

        comment_analysis = None
        if fetch_comments:
            comment_analysis = await self.analyze_post_comments(post_id)

        logger.info("Post analyzed", post_id=str(post_id), sentiment=post.sentiment)

        return {
            "post": {
                "id": str(post.id),
                "platform": post.platform,
                "sentiment": post.sentiment,
                "topics": post.topics,
                "keywords": post.keywords,
                "summary": post.ai_summary,
                "engagement_rate": post.engagement_rate
            },
            "analysis": analysis,
            "comment_analysis": comment_analysis
        }

    async def analyze_post_comments(self, post_id: UUID) -> Dict[str, Any]:
        """Analyze all comments on a post within tenant boundary."""
        post = await self.post_repo.get_by_context(post_id)
        if not post:
            raise ValueError(f"Post {post_id} not found")

        comments = await self.comment_repo.list_for_post(post.external_id, limit=50)
        if not comments:
            return {"total_comments": 0, "analysis": None}

        comment_texts = [c.content for c in comments[:50]]
        analysis = await analyze_comments_batch(
            gemini_client=self.gemini_client,
            comments=comment_texts,
            platform=post.platform
        )

        priority_comments = []
        for comment in comments:
            if not comment.responded:
                priority = assess_comment_priority(comment)
                if priority > 0:
                    comment.priority = priority
                    priority_comments.append(comment)
                    await self.comment_repo.update_comment(comment)

        post.unresponded_comments = len([c for c in comments if not c.responded])
        post.last_comment_check = datetime.utcnow()
        await self.post_repo.update_post(post)

        return {
            "total_comments": len(comments),
            "unresponded_comments": post.unresponded_comments,
            "priority_comments": len(priority_comments),
            "overall_sentiment": analysis.get("overall_sentiment"),
            "common_topics": analysis.get("common_topics", []),
            "questions_count": analysis.get("questions_count", 0),
            "complaints_count": analysis.get("complaints_count", 0),
            "praise_count": analysis.get("praise_count", 0)
        }

    async def generate_comment_reply(
        self,
        comment_id: UUID,
        use_templates: bool = True,
        auto_send: bool = False
    ) -> Dict[str, Any]:
        return await self.auto_responder.generate_comment_reply(
            comment_id=comment_id,
            use_templates=use_templates,
            auto_send=auto_send
        )

    async def auto_respond_to_comments(
        self,
        post_id: Optional[UUID] = None,
        max_responses: int = 10
    ) -> Dict[str, Any]:
        return await self.auto_responder.auto_respond_to_comments(
            post_id=post_id,
            max_responses=max_responses
        )

    async def learn_from_post_performance(self, post_id: UUID) -> Dict[str, Any]:
        """Analyze post performance within tenant boundary and persist learnings."""
        post = await self.post_repo.get_by_context(post_id)
        if not post:
            raise ValueError(f"Post {post_id} not found")

        if post.engagement_rate and post.engagement_rate > 5.0:
            post.best_performing = True
            learnings = await extract_post_learnings(self.gemini_client, post)

            for learning in learnings:
                context_entity = BusinessContext(
                    project_id=self.context.project_id,
                    context_type="content_strategy",
                    context_key=f"high_performing_{post.platform}",
                    title=f"Successful {post.platform.title()} Post Pattern",
                    content=learning["insight"],
                    tags=[post.platform, "high_engagement", "content_strategy"],
                    relevance_score=learning.get("score", 0.8),
                    learned_from="ai_analysis",
                    confidence_score=0.7,
                    active_for_platforms=[post.platform],
                    examples=[{
                        "post_id": post.external_id,
                        "engagement_rate": post.engagement_rate,
                        "content_snippet": post.content[:100] if post.content else ""
                    }]
                )
                self.db.add(context_entity)

            await self.post_repo.update_post(post)
            logger.info("Learned from high-performing post", post_id=str(post_id))

            return {
                "learnings_extracted": len(learnings),
                "insights": learnings
            }

        return {"learnings_extracted": 0, "reason": "Post performance not significant"}
