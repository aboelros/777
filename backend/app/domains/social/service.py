from typing import List, Optional, Any, Dict
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context import TenantContext
from app.domains.social.repository import SocialMediaCommentRepository, SocialMediaPostRepository
from app.domains.social.models import SocialMediaComment, SocialMediaPost


class SocialMediaService:
    def __init__(self, session: AsyncSession, context: TenantContext):
        self.session = session
        self.context = context
        self.comment_repo = SocialMediaCommentRepository(session, context)
        self.post_repo = SocialMediaPostRepository(session, context)

    async def list_comments(
        self,
        platform: Optional[str] = None,
        responded: Optional[bool] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[SocialMediaComment]:
        return await self.comment_repo.list_by_context(
            context=self.context,
            platform=platform,
            responded=responded,
            skip=skip,
            limit=limit
        )

    async def get_comment(self, comment_id: UUID) -> Optional[SocialMediaComment]:
        return await self.comment_repo.get_by_context(comment_id, context=self.context)

    async def create_comment(self, comment: SocialMediaComment) -> SocialMediaComment:
        return await self.comment_repo.create_comment(comment, context=self.context)

    async def get_comment_stats(self) -> Dict[str, Any]:
        return await self.comment_repo.get_comment_stats(context=self.context)

    async def list_posts(self, skip: int = 0, limit: int = 50) -> List[SocialMediaPost]:
        return await self.post_repo.list_posts(context=self.context, skip=skip, limit=limit)

    async def get_post(self, post_id: UUID) -> Optional[SocialMediaPost]:
        return await self.post_repo.get_by_context(post_id, context=self.context)
