from typing import List, Optional, Any, Dict
from uuid import UUID
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy import select, and_, or_, func

from app.core.uow import UnitOfWork
from app.domains.messages.repository import MessageRepository
from app.domains.customers.repository import CustomerProfileRepository
from app.domains.messages.models import Message, MessageDirection
from app.domains.customers.models import CustomerProfile
from app.domains.messages.schemas import MessageSend, MessageResponse, ConversationSummary
from app.domains.projects.repository import ProjectRepository
from app.domains.orders.repository import OrderRepository
from app.domains.ai.orchestrator import AIOrchestrator

import structlog
logger = structlog.get_logger(__name__)

class MessageService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def _verify_project_access(self, project_id: UUID, user_id: UUID) -> Any:
        project_repo = ProjectRepository(self.uow.session)
        project = await project_repo.get(project_id)
        if not project or project.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found or access denied"
            )
        return project

    async def toggle_customer_ai(self, project_id: str, profile_id: str, enabled: bool, user_id: str) -> dict:
        async with self.uow as uow:
            proj_uuid = UUID(project_id)
            prof_uuid = UUID(profile_id)
            user_uuid = UUID(user_id)
            await self._verify_project_access(proj_uuid, user_uuid)
            
            repo = CustomerProfileRepository(uow.session)
            profile = await repo.get(prof_uuid)
            if not profile or profile.project_id != proj_uuid:
                raise HTTPException(status_code=404, detail="Customer not found")
                
            profile.ai_enabled = enabled
            await uow.commit()
            return {"status": "success", "ai_enabled": enabled}

    async def send_message(self, project_id: str, user_id: str, message_data: MessageSend) -> Message:
        async with self.uow as uow:
            proj_uuid = UUID(project_id)
            user_uuid = UUID(user_id)
            await self._verify_project_access(proj_uuid, user_uuid)
            
            if message_data.order_id:
                order_repo = OrderRepository(uow.session)
                order = await order_repo.get(message_data.order_id)
                if not order or order.project_id != proj_uuid:
                    raise HTTPException(status_code=404, detail="Order not found")
                    
            customer_id = None
            target_platform_id = message_data.recipient.get("id") or message_data.recipient.get("customer_id")
            
            if target_platform_id:
                cust_result = await uow.session.execute(
                    select(CustomerProfile)
                    .where(CustomerProfile.project_id == proj_uuid)
                    .where(or_(
                        CustomerProfile.customer_id == str(target_platform_id),
                        and_(
                            CustomerProfile.platform_accounts.contains({message_data.provider.value: str(target_platform_id)})
                        )
                    ))
                )
                customer = cust_result.scalar_one_or_none()
                if customer:
                    customer_id = customer.id
                    message_data.recipient["id"] = target_platform_id
                    
            new_message = Message(
                project_id=proj_uuid,
                customer_id=customer_id,
                order_id=message_data.order_id,
                direction=MessageDirection.OUTBOUND,
                platform=message_data.provider.value,
                provider=message_data.provider.value,
                content=message_data.content,
                content_type=message_data.content_type,
                attachments=message_data.attachments,
                sender={"type": "system", "user_id": user_id},
                recipient=message_data.recipient,
                status="queued"
            )
            
            msg_repo = MessageRepository(uow.session)
            msg_repo.add(new_message)
            await uow.commit()
            await uow.session.refresh(new_message)
            
            try:
                orchestrator = AIOrchestrator(uow.session)
                await orchestrator.initialize_integrations(proj_uuid)
                
                send_result = await orchestrator._send_message(
                    customer_id=customer_id,
                    message=new_message.content,
                    channel=new_message.provider,
                    project_id=proj_uuid,
                    existing_message_id=new_message.id
                )
                
                if send_result.get("status") == "success":
                    new_message.status = "sent"
                    new_message.external_id = send_result.get("id")
                    new_message.sent_at = datetime.utcnow()
                else:
                    new_message.status = "failed"
                    new_message.error_message = send_result.get("message")
                    
                await uow.commit()
            except Exception as e:
                logger.error("Failed to send manual message", error=str(e))
                new_message.status = "failed"
                new_message.error_message = str(e)
                await uow.commit()
                
            return new_message

    async def get_message(self, project_id: str, message_id: str, user_id: str) -> Message:
        async with self.uow as uow:
            proj_uuid = UUID(project_id)
            user_uuid = UUID(user_id)
            await self._verify_project_access(proj_uuid, user_uuid)
            
            repo = MessageRepository(uow.session)
            message = await repo.get(UUID(message_id))
            if not message or message.project_id != proj_uuid:
                raise HTTPException(status_code=404, detail="Message not found")
                
            return message

    async def mark_message_read(self, project_id: str, message_id: str, user_id: str) -> Message:
        async with self.uow as uow:
            proj_uuid = UUID(project_id)
            user_uuid = UUID(user_id)
            await self._verify_project_access(proj_uuid, user_uuid)
            
            repo = MessageRepository(uow.session)
            message = await repo.get(UUID(message_id))
            if not message or message.project_id != proj_uuid:
                raise HTTPException(status_code=404, detail="Message not found")
                
            message.is_read = True
            await uow.commit()
            return message
