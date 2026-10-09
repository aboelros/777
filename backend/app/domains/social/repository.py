from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc

from app.core.repository import BaseRepository
from app.core.context import TenantContext
from app.domains.social.models import SocialMediaComment, SocialMediaPost


class SocialMediaCommentRepository(BaseRepository[SocialMediaComment]):
    def __init__(self, session: AsyncSession, context: Optional[TenantContext] = None):
        super().__init__(SocialMediaComment, session)
        self.context = context

    def _get_context(self, context: Optional[TenantContext] = None) -> TenantContext:
        ctx = context or self.context
        if not ctx or not ctx.project_id:
            raise ValueError("TenantContext with valid project_id is required")
        return ctx

    async def get_by_context(self, comment_id: UUID, context: Optional[TenantContext] = None) -> Optional[SocialMediaComment]:
        ctx = self._get_context(context)
        query = select(self.model).where(
            self.model.id == comment_id,
            self.model.project_id == ctx.project_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_by_context(
        self,
        context: Optional[TenantContext] = None,
        platform: Optional[str] = None,
        responded: Optional[bool] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[SocialMediaComment]:
        ctx = self._get_context(context)
        query = select(self.model).where(self.model.project_id == ctx.project_id)
        if platform:
            query = query.where(self.model.platform == platform)
        if responded is not None:
            query = query.where(self.model.responded == responded)
        query = query.order_by(desc(self.model.created_at)).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def find_existing(
        self,
        platform: str,
        external_id: str,
        context: Optional[TenantContext] = None
    ) -> Optional[SocialMediaComment]:
        ctx = self._get_context(context)
        query = select(self.model).where(
            self.model.project_id == ctx.project_id,
            self.model.platform == platform,
            self.model.external_id == external_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_comment(
        self,
        comment: SocialMediaComment,
        context: Optional[TenantContext] = None
    ) -> SocialMediaComment:
        ctx = self._get_context(context)
        comment.project_id = ctx.project_id
        self.session.add(comment)
        await self.session.commit()
        await self.session.refresh(comment)
        return comment

    async def update_comment(
        self,
        comment: SocialMediaComment,
        context: Optional[TenantContext] = None
    ) -> SocialMediaComment:
        ctx = self._get_context(context)
        if comment.project_id != ctx.project_id:
            raise ValueError("Cross-tenant modification prohibited")
        await self.session.commit()
        await self.session.refresh(comment)
        return comment

    async def get_comment_stats(self, context: Optional[TenantContext] = None) -> Dict[str, Any]:
        ctx = self._get_context(context)
        total_res = await self.session.execute(
            select(func.count(self.model.id)).where(self.model.project_id == ctx.project_id)
        )
        total = total_res.scalar() or 0

        pending_res = await self.session.execute(
            select(func.count(self.model.id)).where(
                self.model.project_id == ctx.project_id,
                self.model.responded == False
            )
        )
        pending = pending_res.scalar() or 0

        platform_res = await self.session.execute(
            select(self.model.platform, func.count(self.model.id).label("count"))
            .where(self.model.project_id == ctx.project_id)
            .group_by(self.model.platform)
        )
        by_platform = {row.platform: row.count for row in platform_res}

        return {
            "total_comments": total,
            "pending_responses": pending,
            "responded": total - pending,
            "by_platform": by_platform,
            "response_rate": round(((total - pending) / total * 100), 1) if total > 0 else 0
        }

    async def list_for_post(
        self,
        post_external_id: str,
        context: Optional[TenantContext] = None,
        limit: int = 50
    ) -> List[SocialMediaComment]:
        ctx = self._get_context(context)
        query = select(self.model).where(
            self.model.project_id == ctx.project_id,
            self.model.post_id == post_external_id
        ).order_by(desc(self.model.created_at)).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_unresponded(
        self,
        context: Optional[TenantContext] = None,
        post_external_id: Optional[str] = None,
        limit: int = 10
    ) -> List[SocialMediaComment]:
        ctx = self._get_context(context)
        query = select(self.model).where(
            self.model.project_id == ctx.project_id,
            self.model.responded == False,
            self.model.requires_human == False
        )
        if post_external_id:
            query = query.where(self.model.post_id == post_external_id)
        query = query.order_by(desc(self.model.priority), desc(self.model.created_at)).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_project(self, project_id: UUID) -> List[SocialMediaComment]:
        query = select(self.model).where(self.model.project_id == project_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())


class SocialMediaPostRepository(BaseRepository[SocialMediaPost]):
    def __init__(self, session: AsyncSession, context: Optional[TenantContext] = None):
        super().__init__(SocialMediaPost, session)
        self.context = context

    def _get_context(self, context: Optional[TenantContext] = None) -> TenantContext:
        ctx = context or self.context
        if not ctx or not ctx.project_id:
            raise ValueError("TenantContext with valid project_id is required")
        return ctx

    async def get_by_context(self, post_id: UUID, context: Optional[TenantContext] = None) -> Optional[SocialMediaPost]:
        ctx = self._get_context(context)
        query = select(self.model).where(
            self.model.id == post_id,
            self.model.project_id == ctx.project_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_external_id(
        self,
        platform: str,
        external_id: str,
        context: Optional[TenantContext] = None
    ) -> Optional[SocialMediaPost]:
        ctx = self._get_context(context)
        query = select(self.model).where(
            self.model.project_id == ctx.project_id,
            self.model.platform == platform,
            self.model.external_id == external_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_posts(
        self,
        context: Optional[TenantContext] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[SocialMediaPost]:
        ctx = self._get_context(context)
        query = select(self.model).where(
            self.model.project_id == ctx.project_id
        ).order_by(desc(self.model.created_at)).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_post(
        self,
        post: SocialMediaPost,
        context: Optional[TenantContext] = None
    ) -> SocialMediaPost:
        ctx = self._get_context(context)
        if post.project_id != ctx.project_id:
            raise ValueError("Cross-tenant modification prohibited")
        await self.session.commit()
        await self.session.refresh(post)
        return post

    async def create_post(
        self,
        post: SocialMediaPost,
        context: Optional[TenantContext] = None
    ) -> SocialMediaPost:
        ctx = self._get_context(context)
        post.project_id = ctx.project_id
        self.session.add(post)
        await self.session.commit()
        await self.session.refresh(post)
        return post

    async def get_by_project(self, project_id: UUID) -> List[SocialMediaPost]:
        query = select(self.model).where(self.model.project_id == project_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())
