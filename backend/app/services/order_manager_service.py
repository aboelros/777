"""
Intelligent Order Management Service with AI-powered automation.
Handles order lifecycle, status transitions, and customer notifications.
"""

from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc
import structlog
import json

from app.services.gemini_client import GeminiClient
from app.services.enhanced_ai_service import EnhancedAIService
from app.db.models import (
    Order, OrderStatus, Message, MessageDirection,
    CustomerProfile, Product
)

logger = structlog.get_logger(__name__)


class OrderManagerService:
    """
    Intelligent order management with automated status updates and customer communication.
    """
    
    def __init__(self, db: AsyncSession, project_id: UUID):
        self.db = db
        self.project_id = project_id
        self.gemini_client = GeminiClient()
        self.ai_service = EnhancedAIService(db, project_id)
    
    # =========================================================================
    # Order Status Management
    # =========================================================================
    
    async def update_order_status(
        self,
        order_id: UUID,
        new_status: OrderStatus,
        notify_customer: bool = True,
        note: Optional[str] = None,
        auto_message: bool = True
    ) -> Dict[str, Any]:
        """
        Update order status and optionally notify customer.
        
        Args:
            order_id: Order to update
            new_status: New status to set
            notify_customer: Whether to notify customer
            note: Optional note about status change
            auto_message: Use AI to generate personalized message
        """
        # Get order
        result = await self.db.execute(
            select(Order).where(Order.id == order_id)
        )
        order = result.scalar_one_or_none()
        
        if not order:
            raise ValueError(f"Order {order_id} not found")
        
        old_status = order.status
        
        # Update status
        order.status = new_status.value
        order.updated_at = datetime.utcnow()
        
        # Add to status history
        status_history = order.extra_data.get("status_history", [])
        status_history.append({
            "from_status": old_status,
            "to_status": new_status.value,
            "timestamp": datetime.utcnow().isoformat(),
            "note": note,
            "automated": auto_message
        })
        order.extra_data["status_history"] = status_history
        
        # Update fulfilled date if status is fulfilled
        if new_status == OrderStatus.FULFILLED and not order.fulfilled_date:
            order.fulfilled_date = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(order)
        
        logger.info(
            "Order status updated",
            order_id=str(order_id),
            old_status=old_status,
            new_status=new_status.value
        )
        
        # Notify customer if requested
        notification_sent = False
        notification_message = None
        
        if notify_customer:
            customer_id = order.customer.get("id")
            platform = order.customer.get("platform", "whatsapp")
            
            if customer_id:
                notification_message = await self._generate_status_notification(
                    order=order,
                    new_status=new_status,
                    note=note,
                    use_ai=auto_message
                )
                
                # Save notification as outbound message
                await self._save_notification_message(
                    order=order,
                    customer_id=customer_id,
                    platform=platform,
                    message=notification_message
                )
                
                notification_sent = True
                
                logger.info(
                    "Customer notified of status change",
                    order_id=str(order_id),
                    customer_id=customer_id,
                    status=new_status.value
                )
        
        return {
            "order_id": str(order.id),
            "external_id": order.external_id,
            "old_status": old_status,
            "new_status": new_status.value,
            "notification_sent": notification_sent,
            "notification_message": notification_message,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def auto_progress_order(
        self,
        order_id: UUID,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Automatically progress order to next logical status using AI decision.
        
        AI determines if order should progress based on:
        - Current status
        - Time since last update
        - Order details
        - Business rules
        """
        result = await self.db.execute(
            select(Order).where(Order.id == order_id)
        )
        order = result.scalar_one_or_none()
        
        if not order:
            raise ValueError(f"Order {order_id} not found")
        
        # AI decides next status
        next_status_decision = await self._ai_determine_next_status(order)
        
        if not next_status_decision.get("should_progress"):
            return {
                "progressed": False,
                "reason": next_status_decision.get("reason"),
                "current_status": order.status
            }
        
        # Progress to next status
        next_status = OrderStatus[next_status_decision["next_status"].upper()]
        
        result = await self.update_order_status(
            order_id=order_id,
            new_status=next_status,
            notify_customer=True,
            note=reason or next_status_decision.get("reason"),
            auto_message=True
        )
        
        return {
            "progressed": True,
            **result
        }
    
    async def get_order_progress(self, order_id: UUID) -> Dict[str, Any]:
        """
        Get comprehensive order progress information.
        
        Returns timeline, current status, next expected status, estimated completion.
        """
        result = await self.db.execute(
            select(Order).where(Order.id == order_id)
        )
        order = result.scalar_one_or_none()
        
        if not order:
            raise ValueError(f"Order {order_id} not found")
        
        # Get status history
        status_history = order.extra_data.get("status_history", [])
        
        # Calculate progress percentage
        progress_pct = self._calculate_progress_percentage(order.status)
        
        # Get estimated completion
        estimated_completion = await self._estimate_completion_date(order)
        
        # Get next expected status
        next_status = self._get_next_expected_status(order.status)
        
        # Get customer notifications sent
        result = await self.db.execute(
            select(Message)
            .where(
                and_(
                    Message.order_id == order_id,
                    Message.direction == MessageDirection.OUTBOUND,
                    Message.ai_generated == True
                )
            )
            .order_by(desc(Message.created_at))
        )
        notifications = result.scalars().all()
        
        return {
            "order_id": str(order.id),
            "external_id": order.external_id,
            "current_status": order.status,
            "progress_percentage": progress_pct,
            "next_expected_status": next_status,
            "estimated_completion": estimated_completion,
            "order_date": order.order_date.isoformat() if order.order_date else None,
            "updated_at": order.updated_at.isoformat() if order.updated_at else None,
            "timeline": [
                {
                    "from_status": h.get("from_status"),
                    "to_status": h.get("to_status"),
                    "timestamp": h.get("timestamp"),
                    "note": h.get("note"),
                    "automated": h.get("automated", False)
                }
                for h in status_history
            ],
            "notifications_sent": [
                {
                    "id": str(n.id),
                    "content": n.content,
                    "platform": n.platform,
                    "status": n.status,
                    "created_at": n.created_at.isoformat()
                }
                for n in notifications
            ],
            "customer": order.customer,
            "total": order.total,
            "items_count": len(order.items)
        }
    
    async def get_orders_requiring_attention(
        self,
        max_age_hours: int = 48
    ) -> List[Dict[str, Any]]:
        """
        Get orders that require attention (stale, pending too long, etc.).
        
        Args:
            max_age_hours: Maximum hours in pending status before flagging
        """
        cutoff_date = datetime.utcnow() - timedelta(hours=max_age_hours)
        
        # Get pending orders older than cutoff
        result = await self.db.execute(
            select(Order)
            .where(
                and_(
                    Order.project_id == self.project_id,
                    Order.status == OrderStatus.PENDING.value,
                    Order.order_date < cutoff_date
                )
            )
            .order_by(Order.order_date)
        )
        pending_orders = result.scalars().all()
        
        # Get processing orders older than cutoff
        result = await self.db.execute(
            select(Order)
            .where(
                and_(
                    Order.project_id == self.project_id,
                    Order.status == OrderStatus.PROCESSING.value,
                    Order.updated_at < cutoff_date
                )
            )
            .order_by(Order.updated_at)
        )
        processing_orders = result.scalars().all()
        
        attention_required = []
        
        for order in pending_orders:
            age_hours = (datetime.utcnow() - order.order_date).total_seconds() / 3600
            attention_required.append({
                "order_id": str(order.id),
                "external_id": order.external_id,
                "status": order.status,
                "reason": "pending_too_long",
                "age_hours": round(age_hours, 1),
                "customer": order.customer,
                "total": order.total,
                "order_date": order.order_date.isoformat()
            })
        
        for order in processing_orders:
            age_hours = (datetime.utcnow() - order.updated_at).total_seconds() / 3600
            attention_required.append({
                "order_id": str(order.id),
                "external_id": order.external_id,
                "status": order.status,
                "reason": "processing_too_long",
                "age_hours": round(age_hours, 1),
                "customer": order.customer,
                "total": order.total,
                "updated_at": order.updated_at.isoformat()
            })
        
        return attention_required
    
    async def bulk_process_orders(
        self,
        order_ids: List[UUID],
        action: str,
        notify_customers: bool = True
    ) -> Dict[str, Any]:
        """
        Process multiple orders with same action.
        
        Actions: 'progress', 'fulfill', 'cancel'
        """
        results = {
            "total": len(order_ids),
            "successful": 0,
            "failed": 0,
            "results": []
        }
        
        for order_id in order_ids:
            try:
                if action == "progress":
                    result = await self.auto_progress_order(order_id)
                elif action == "fulfill":
                    result = await self.update_order_status(
                        order_id=order_id,
                        new_status=OrderStatus.FULFILLED,
                        notify_customer=notify_customers
                    )
                elif action == "cancel":
                    result = await self.update_order_status(
                        order_id=order_id,
                        new_status=OrderStatus.CANCELLED,
                        notify_customer=notify_customers
                    )
                else:
                    raise ValueError(f"Unknown action: {action}")
                
                results["successful"] += 1
                results["results"].append({
                    "order_id": str(order_id),
                    "success": True,
                    "result": result
                })
                
            except Exception as e:
                results["failed"] += 1
                results["results"].append({
                    "order_id": str(order_id),
                    "success": False,
                    "error": str(e)
                })
                logger.error("Failed to process order", order_id=str(order_id), error=str(e))
        
        return results
    
    # =========================================================================
    # Customer Communication
    # =========================================================================
    
    async def send_order_update(
        self,
        order_id: UUID,
        message_type: str,
        custom_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a specific type of order update to customer.
        
        Message types:
        - confirmation: Order received confirmation
        - processing: Order is being processed
        - shipped: Order has shipped
        - delivered: Order delivered
        - delay: Notify about delay
        - custom: Custom message
        """
        result = await self.db.execute(
            select(Order).where(Order.id == order_id)
        )
        order = result.scalar_one_or_none()
        
        if not order:
            raise ValueError(f"Order {order_id} not found")
        
        customer_id = order.customer.get("id")
        platform = order.customer.get("platform", "whatsapp")
        
        if not customer_id:
            raise ValueError("Customer ID not found in order")
        
        # Generate message based on type
        if custom_message:
            message = custom_message
        else:
            message = await self._generate_typed_message(
                order=order,
                message_type=message_type
            )
        
        # Save message
        await self._save_notification_message(
            order=order,
            customer_id=customer_id,
            platform=platform,
            message=message,
            message_type=message_type
        )
        
        logger.info(
            "Order update sent",
            order_id=str(order_id),
            message_type=message_type,
            customer_id=customer_id
        )
        
        return {
            "order_id": str(order.id),
            "customer_id": customer_id,
            "platform": platform,
            "message_type": message_type,
            "message": message,
            "sent_at": datetime.utcnow().isoformat()
        }
    
    async def schedule_follow_up(
        self,
        order_id: UUID,
        delay_hours: int,
        message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Schedule a follow-up message for an order.
        """
        result = await self.db.execute(
            select(Order).where(Order.id == order_id)
        )
        order = result.scalar_one_or_none()
        
        if not order:
            raise ValueError(f"Order {order_id} not found")
        
        send_at = datetime.utcnow() + timedelta(hours=delay_hours)
        
        # Store scheduled message in order extra_data
        scheduled_messages = order.extra_data.get("scheduled_messages", [])
        scheduled_messages.append({
            "message": message or "Follow-up about your order",
            "scheduled_for": send_at.isoformat(),
            "status": "pending"
        })
        order.extra_data["scheduled_messages"] = scheduled_messages
        
        await self.db.commit()
        
        logger.info(
            "Follow-up scheduled",
            order_id=str(order_id),
            send_at=send_at.isoformat()
        )
        
        return {
            "order_id": str(order.id),
            "scheduled_for": send_at.isoformat(),
            "message": message
        }
    
    # =========================================================================
    # AI-Powered Helpers
    # =========================================================================
    
    async def _ai_determine_next_status(self, order: Order) -> Dict[str, Any]:
        """
        Use AI to determine if order should progress to next status.
        """
        current_status = order.status
        order_age_hours = (datetime.utcnow() - order.order_date).total_seconds() / 3600
        
        prompt = f"""Analyze this order and determine if it should progress to the next status:

Order ID: {order.external_id}
Current Status: {current_status}
Order Age: {order_age_hours:.1f} hours
Total: ${order.total}
Items: {len(order.items)} items
Customer: {order.customer.get('name', 'Unknown')}

Status History:
{json.dumps(order.extra_data.get('status_history', []), indent=2)}

Determine:
1. Should this order progress to the next status? (yes/no)
2. If yes, what should be the next status?
3. Reason for the decision

Return as JSON:
{{
    "should_progress": true/false,
    "next_status": "pending/processing/fulfilled/shipped/cancelled",
    "reason": "explanation",
    "confidence": 0.0-1.0
}}"""

        try:
            response = await self.gemini_client.generate_content(prompt=prompt, temperature=0.3)
            decision = json.loads(self._extract_json(response))
            return decision
        except:
            # Default conservative decision
            return {
                "should_progress": False,
                "reason": "Unable to determine - manual review required",
                "confidence": 0.0
            }
    
    async def _generate_status_notification(
        self,
        order: Order,
        new_status: OrderStatus,
        note: Optional[str],
        use_ai: bool = True
    ) -> str:
        """
        Generate customer notification message for status change.
        """
        if not use_ai:
            # Use template messages
            templates = {
                "pending": f"Hi! We've received your order #{order.external_id}. We'll start processing it shortly! 📦",
                "processing": f"Good news! Your order #{order.external_id} is now being processed. We'll update you when it ships! 🎉",
                "fulfilled": f"Your order #{order.external_id} has been fulfilled! Thank you for your purchase! ✨",
                "shipped": f"Great news! Your order #{order.external_id} has shipped! Track it here: [tracking link] 🚚",
                "cancelled": f"Your order #{order.external_id} has been cancelled. If you have questions, please let us know. 💬"
            }
            return templates.get(new_status.value.lower(), f"Your order status has been updated to: {new_status.value}")
        
        # AI-generated personalized message
        customer_name = order.customer.get("name", "there")
        platform = order.customer.get("platform", "message")
        
        prompt = f"""Generate a friendly, personalized order status notification for {platform.upper()}:

Customer Name: {customer_name}
Order ID: {order.external_id}
Previous Status: {order.status}
New Status: {new_status.value}
Total: ${order.total}
Items: {', '.join([item.get('product_name', 'Item') for item in order.items[:3]])}
Additional Note: {note or 'None'}

Requirements:
- Warm and friendly tone
- Include order ID
- Appropriate emoji for {platform}
- Keep under 150 characters for SMS/WhatsApp, 200 for other platforms
- Be specific about the status change

Return only the message text, no explanations."""

        try:
            message = await self.gemini_client.generate_content(prompt=prompt, temperature=0.8)
            return message
        except:
            # Fallback to template
            return f"Hi {customer_name}! Your order #{order.external_id} status has been updated to: {new_status.value} 📦"
    
    async def _generate_typed_message(
        self,
        order: Order,
        message_type: str
    ) -> str:
        """
        Generate specific type of message.
        """
        customer_name = order.customer.get("name", "there")
        
        prompts = {
            "confirmation": f"Generate an order confirmation message for {customer_name}. Order #{order.external_id}, Total: ${order.total}",
            "processing": f"Generate a processing update for {customer_name}. Order #{order.external_id} is being prepared.",
            "shipped": f"Generate a shipping notification for {customer_name}. Order #{order.external_id} has shipped!",
            "delivered": f"Generate a delivery confirmation for {customer_name}. Order #{order.external_id} has been delivered!",
            "delay": f"Generate an apologetic delay notification for {customer_name}. Order #{order.external_id} is delayed."
        }
        
        prompt = prompts.get(message_type, f"Generate a message about order #{order.external_id}")
        prompt += " Keep it friendly and concise (under 150 chars)."
        
        try:
            message = await self.gemini_client.generate_content(prompt=prompt, temperature=0.7)
            return message
        except:
            return f"Hi {customer_name}! Update about your order #{order.external_id}. We'll keep you posted! 📦"
    
    async def _save_notification_message(
        self,
        order: Order,
        customer_id: str,
        platform: str,
        message: str,
        message_type: str = "order_update"
    ):
        """
        Save notification as outbound message.
        """
        notification = Message(
            project_id=self.project_id,
            order_id=order.id,
            direction=MessageDirection.OUTBOUND,
            platform=platform,
            provider=platform,
            content=message,
            sender={"type": "system", "name": "Order Manager"},
            recipient={"id": customer_id, "name": order.customer.get("name")},
            ai_generated=True,
            ai_model="gemini-2.0-flash",
            extra_data={
                "message_type": message_type,
                "order_external_id": order.external_id,
                "order_status": order.status
            },
            status="sent"
        )
        
        self.db.add(notification)
        await self.db.commit()
    
    def _calculate_progress_percentage(self, status: str) -> int:
        """Calculate progress percentage based on status."""
        progress_map = {
            "pending": 25,
            "processing": 50,
            "shipped": 75,
            "fulfilled": 100,
            "delivered": 100,
            "cancelled": 0,
            "refunded": 0
        }
        return progress_map.get(status.lower(), 25)
    
    async def _estimate_completion_date(self, order: Order) -> Optional[str]:
        """Estimate when order will be completed."""
        if order.status in ["fulfilled", "delivered", "cancelled", "refunded"]:
            return None
        
        # Simple estimation based on average processing time
        # In production, this could use ML based on historical data
        days_to_complete = {
            "pending": 3,
            "processing": 2,
            "shipped": 1
        }
        
        days = days_to_complete.get(order.status.lower(), 3)
        estimated = datetime.utcnow() + timedelta(days=days)
        return estimated.isoformat()
    
    def _get_next_expected_status(self, current_status: str) -> Optional[str]:
        """Get the next expected status in the workflow."""
        workflow = {
            "pending": "processing",
            "processing": "shipped",
            "shipped": "fulfilled"
        }
        return workflow.get(current_status.lower())
    
    def _extract_json(self, response: str) -> str:
        """Extract JSON from response."""
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            return json_match.group(0)
        return response
