"""
Order status change notification system.
Automatically notifies customers when their order status changes.
"""

from typing import Optional
from uuid import UUID
from datetime import datetime
import structlog

from app.db.models import Order
from app.services.ai_orchestrator import AIOrchestrator
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger(__name__)

# Status change messages in Arabic and English
STATUS_MESSAGES = {
    "processing": {
        "ar": "📦 تحديث الطلب #{order_id}\n\nطلبك الآن قيد المعالجة! نحن نجهز منتجاتك للشحن.\n\nسأبقيك على اطلاع بأي تحديثات.",
        "en": "📦 Order Update #{order_id}\n\nYour order is now being processed! We're preparing your products for shipment.\n\nI'll keep you updated."
    },
    "shipped": {
        "ar": "🚚 تحديث الطلب #{order_id}\n\nطلبك في الطريق إليك! 🎉\n\nسيصل خلال 2-3 أيام عمل.\n\nهل تحتاج رقم التتبع؟",
        "en": "🚚 Order Update #{order_id}\n\nYour order is on its way! 🎉\n\nExpected delivery in 2-3 business days.\n\nNeed the tracking number?"
    },
    "fulfilled": {
        "ar": "✅ تحديث الطلب #{order_id}\n\nتم تسليم طلبك بنجاح! 🎊\n\nنأمل أن تكون راضياً عن منتجاتك.\n\nهل تود تقييم تجربتك؟",
        "en": "✅ Order Update #{order_id}\n\nYour order has been delivered! 🎊\n\nWe hope you're satisfied with your products.\n\nWould you like to rate your experience?"
    },
    "cancelled": {
        "ar": "❌ تحديث الطلب #{order_id}\n\nتم إلغاء طلبك.\n\nإذا كان هذا خطأ أو تحتاج مساعدة، يرجى إخباري!",
        "en": "❌ Order Update #{order_id}\n\nYour order has been cancelled.\n\nIf this was a mistake or you need help, please let me know!"
    }
}


async def notify_customer_order_status(
    order_id: UUID,
    new_status: str,
    db: AsyncSession,
    language: str = "ar"
) -> bool:
    """
    Notify customer about order status change.
    
    Args:
        order_id: Order UUID
        new_status: New order status
        db: Database session
        language: Customer's preferred language (ar/en)
    
    Returns:
        True if notification sent successfully
    """
    try:
        from sqlalchemy import select
        
        # Get order details
        result = await db.execute(
            select(Order).where(Order.id == order_id)
        )
        order = result.scalar_one_or_none()
        
        if not order or not order.customer_id:
            logger.warning("Order not found or no customer", order_id=str(order_id))
            return False
        
        # Get message template
        if new_status not in STATUS_MESSAGES:
            logger.info("No notification template for status", status=new_status)
            return False
        
        message = STATUS_MESSAGES[new_status][language].format(
            order_id=order.external_id
        )
        
        # Send message via AI orchestrator
        orchestrator = AIOrchestrator(db)
        
        result = await orchestrator._send_whatsapp_message(
            customer_id=order.customer_id,
            message=message,
            project_id=order.project_id
        )
        
        if result.get("status") == "success":
            logger.info(
                "Order status notification sent",
                order_id=str(order_id),
                status=new_status,
                customer_id=str(order.customer_id)
            )
            return True
        else:
            logger.error(
                "Failed to send order notification",
                order_id=str(order_id),
                error=result.get("message")
            )
            return False
            
    except Exception as e:
        logger.error(
            "Error sending order notification",
            order_id=str(order_id),
            error=str(e)
        )
        return False
