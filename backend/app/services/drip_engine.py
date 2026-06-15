from datetime import datetime, timedelta
from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import joinedload

from app.db.models import DripCampaign, DripStep, CampaignEnrollment, CustomerProfile, Project
from app.services.messages import MessageService

class DripEngine:
    """Handles the execution of automated drip campaigns."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.message_service = MessageService(db)

    async def enroll_customer(self, project_id: UUID, campaign_id: UUID, customer_id: UUID):
        """Enroll a customer into a drip campaign."""
        # Check if already enrolled
        existing = await self.db.execute(
            select(CampaignEnrollment)
            .where(CampaignEnrollment.campaign_id == campaign_id)
            .where(CampaignEnrollment.customer_id == customer_id)
        )
        if existing.scalar_one_or_none():
            return # Already enrolled
            
        # Get first step delay
        first_step = await self._get_step(campaign_id, 1)
        if not first_step:
            return # Empty campaign
            
        next_run = datetime.utcnow() + timedelta(hours=first_step.delay_hours)
        
        enrollment = CampaignEnrollment(
            project_id=project_id,
            campaign_id=campaign_id,
            customer_id=customer_id,
            status='active',
            current_step=1,
            next_execution_at=next_run
        )
        self.db.add(enrollment)
        await self.db.commit()
    
    async def process_due_steps(self):
        """Check all active enrollments and execute due steps."""
        now = datetime.utcnow()
        
        # Find due enrollments
        result = await self.db.execute(
            select(CampaignEnrollment)
            .options(joinedload(CampaignEnrollment.campaign), joinedload(CampaignEnrollment.customer))
            .where(CampaignEnrollment.status == 'active')
            .where(CampaignEnrollment.next_execution_at <= now)
        )
        enrollments = result.scalars().all()
        
        for enrollment in enrollments:
            await self._execute_step(enrollment)
            
    async def _execute_step(self, enrollment: CampaignEnrollment):
        """Execute the current step for an enrollment."""
        step = await self._get_step(enrollment.campaign_id, enrollment.current_step)
        
        if not step:
            # Campaign finished
            enrollment.status = 'completed'
            enrollment.completed_at = datetime.utcnow()
            await self.db.commit()
            return
            
        # Send Message
        try:
            # Simple template replacement
            content = step.content_template.replace("{{name}}", enrollment.customer.name or "Customer")
            
            # Send (assuming MessageService handles the actual sending logic abstractly)
            # In a real scenario, we'd need to mock the request object or use an internal send method
            # For now, we simulate the action
            print(f"Sending Drip Message to {enrollment.customer.customer_id}: {content}")
            
            # Move to next step
            enrollment.current_step += 1
            
            # Calculate next run
            next_step = await self._get_step(enrollment.campaign_id, enrollment.current_step)
            if next_step:
                enrollment.next_execution_at = datetime.utcnow() + timedelta(hours=next_step.delay_hours)
            else:
                enrollment.status = 'completed'
                enrollment.completed_at = datetime.utcnow()
                
            await self.db.commit()
            
        except Exception as e:
            print(f"Failed to execute drip step: {e}")
            # Optional: increment error count on enrollment

    async def _get_step(self, campaign_id: UUID, step_order: int) -> DripStep:
        result = await self.db.execute(
            select(DripStep)
            .where(DripStep.campaign_id == campaign_id)
            .where(DripStep.step_order == step_order)
        )
        return result.scalar_one_or_none()
