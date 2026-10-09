from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from app.core.repository import BaseRepository
from app.core.context import TenantContext
from app.domains.messages.models import Message

class MessageRepository(BaseRepository[Message]):
    def __init__(self, session: AsyncSession):
        super().__init__(Message, session)

    async def get_project_messages(self, project_id: UUID, limit: int = 50, offset: int = 0) -> List[Message]:
        query = select(self.model).where(
            self.model.project_id == project_id
        ).order_by(self.model.created_at.desc()).offset(offset).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    # --- Phase 1 Security Migration Methods ---

    async def get_message_by_context(self, context: 'TenantContext', message_id: UUID) -> Optional[Message]:
        """
        Retrieves a message, enforcing that the message belongs to the tenant.
        The project scope is explicitly derived from the authorized TenantContext.
        """
        query = select(self.model).where(
            self.model.id == message_id,
            self.model.project_id == context.project_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_inbox_messages_by_context(
        self,
        context: 'TenantContext',
        direction: Optional[str] = None,
        provider: Optional[str] = None,
        order_id: Optional['UUID'] = None,
        is_read: Optional[bool] = None,
        days: int = 7,
        page: int = 1,
        page_size: int = 50
    ) -> List['Message']:
        """
        Retrieves unified inbox messages scoped strictly to the authorized TenantContext.
        """
        from datetime import datetime, timedelta
        from sqlalchemy.orm import joinedload
        from sqlalchemy import or_, and_

        query = select(self.model).options(joinedload(self.model.customer)).where(
            self.model.project_id == context.project_id
        )

        if direction:
            query = query.where(self.model.direction == direction)

        if provider:
            if provider.lower() in ["instagram", "facebook", "whatsapp"]:
                query = query.where(or_(
                    self.model.provider == provider,
                    self.model.platform == provider,
                    and_(self.model.provider == "meta", self.model.platform == provider)
                ))
            else:
                query = query.where(self.model.provider == provider)

        if order_id:
            query = query.where(self.model.order_id == order_id)

        if is_read is not None:
            query = query.where(self.model.is_read == is_read)

        start_date = datetime.utcnow() - timedelta(days=days)
        query = query.where(self.model.created_at >= start_date)

        query = query.order_by(self.model.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_inbox_by_context(
        self,
        context: 'TenantContext',
        limit: int = 50,
        provider: Optional[str] = None,
        days: int = 30
    ) -> List[Message]:
        """
        Retrieves inbox messages scoped strictly to the authorized TenantContext.
        """
        from datetime import datetime, timedelta
        from sqlalchemy.orm import selectinload

        query = select(self.model).options(selectinload(self.model.customer)).where(
            self.model.project_id == context.project_id
        )

        if provider and provider.lower() != "all":
            query = query.where(self.model.provider == provider)

        start_date = datetime.utcnow() - timedelta(days=days)
        query = query.where(self.model.created_at >= start_date)

        query = query.order_by(self.model.created_at.desc()).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_recent_messages_by_context(
        self,
        context: 'TenantContext',
        provider: Optional[str] = None,
        days: int = 30,
        limit: int = 200
    ) -> List[Message]:
        """
        Retrieves messages strictly scoped to the authorized TenantContext.
        """
        from datetime import datetime, timedelta
        from sqlalchemy.orm import selectinload

        query = select(self.model).options(selectinload(self.model.customer)).where(
            self.model.project_id == context.project_id
        )

        if provider and provider.lower() != "all":
            if provider.lower() in ["instagram", "facebook", "whatsapp"]:
                query = query.where(or_(
                    self.model.provider == provider,
                    self.model.platform == provider,
                    and_(self.model.provider == "meta", self.model.platform == provider)
                ))
            else:
                query = query.where(self.model.provider == provider)

        start_date = datetime.utcnow() - timedelta(days=days)
        query = query.where(self.model.created_at >= start_date)

        query = query.order_by(self.model.created_at.desc()).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())




    async def check_conversation_ownership(self, context: 'TenantContext', conversation_id: str) -> bool:
        """
        Explicit SQL check to verify if a conversation belongs to the tenant.
        Does not retrieve records into Python; relies entirely on the SQL engine.
        """
        from sqlalchemy import select, or_
        from uuid import UUID

        try:
            uid = UUID(conversation_id)
            # 1. Check CustomerProfile ownership (Gold standard for resolving conversations)
            from app.domains.customers.models import CustomerProfile
            profile_query = select(CustomerProfile.id).where(
                CustomerProfile.id == uid,
                CustomerProfile.project_id == context.project_id
            )
            res = await self.session.execute(profile_query)
            if res.scalar_one_or_none():
                return True

            # 2. Fallback to direct Message linkage (if conversation_id is a message ID or order ID)
            msg_query = select(self.model.id).where(
                self.model.project_id == context.project_id,
                or_(self.model.id == uid, self.model.order_id == uid)
            ).limit(1)
            res = await self.session.execute(msg_query)
            return res.scalar_one_or_none() is not None

        except ValueError:
            # 3. Fallback for orphan platform string conversations
            msg_query = select(self.model.id).where(
                self.model.project_id == context.project_id,
                or_(
                    self.model.sender['id'].astext == conversation_id,
                    self.model.sender['customer_id'].astext == conversation_id,
                    self.model.sender['phone'].astext == conversation_id,
                    self.model.recipient['id'].astext == conversation_id,
                    self.model.recipient['phone'].astext == conversation_id,
                )
            ).limit(1)
            res = await self.session.execute(msg_query)
            return res.scalar_one_or_none() is not None

    async def mark_conversation_read_by_context(self, context: 'TenantContext', conversation_id: str) -> int:
        """
        Mark all inbound unread messages in a conversation as read.
        Enforces tenant isolation purely in SQL via project_id and conversation scope.
        """
        from sqlalchemy import update, or_
        from app.domains.messages.models import MessageDirection
        from uuid import UUID

        stmt = update(self.model).where(
            self.model.project_id == context.project_id,
            self.model.direction == MessageDirection.INBOUND,
            self.model.is_read == False
        ).values(is_read=True)

        try:
            uid = UUID(conversation_id)
            stmt = stmt.where(
                or_(
                    self.model.customer_id == uid,
                    self.model.id == uid,
                    self.model.order_id == uid
                )
            )
        except ValueError:
            stmt = stmt.where(
                or_(
                    self.model.sender['id'].astext == conversation_id,
                    self.model.sender['customer_id'].astext == conversation_id,
                    self.model.sender['phone'].astext == conversation_id,
                    self.model.recipient['id'].astext == conversation_id,
                    self.model.recipient['phone'].astext == conversation_id,
                )
            )

        result = await self.session.execute(stmt)
        return result.rowcount

    async def get_conversation_messages_by_context(self, context: 'TenantContext', conversation_id: str) -> List['Message']:
        """
        Retrieves all messages belonging to a conversation, scoped securely by TenantContext.
        """
        from sqlalchemy import select, or_
        from uuid import UUID

        stmt = select(self.model).where(
            self.model.project_id == context.project_id
        )

        try:
            uid = UUID(conversation_id)
            stmt = stmt.where(
                or_(
                    self.model.customer_id == uid,
                    self.model.id == uid,
                    self.model.order_id == uid
                )
            )
        except ValueError:
            stmt = stmt.where(
                or_(
                    self.model.sender['id'].astext == conversation_id,
                    self.model.sender['customer_id'].astext == conversation_id,
                    self.model.sender['phone'].astext == conversation_id,
                    self.model.recipient['id'].astext == conversation_id,
                    self.model.recipient['phone'].astext == conversation_id,
                )
            )

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete_messages_by_ids_and_context(self, context: 'TenantContext', message_ids: List['UUID']) -> int:
        """
        Deletes messages securely by verifying they belong to the tenant context.
        """
        from sqlalchemy import delete
        if not message_ids:
            return 0

        stmt = delete(self.model).where(
            self.model.project_id == context.project_id,
            self.model.id.in_(message_ids)
        )
        result = await self.session.execute(stmt)
        return result.rowcount


    async def get_by_context(self, context: 'TenantContext', message_id: UUID) -> Optional['Message']:
        from sqlalchemy import select
        stmt = select(self.model).where(
            self.model.id == message_id,
            self.model.project_id == context.project_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
