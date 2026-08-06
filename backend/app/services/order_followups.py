"""
Proactive Order Follow-up System
Automatically checks in with customers at specific intervals about their orders.
"""

from typing import Optional, List
from uuid import UUID
from datetime import datetime, timedelta
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.domains.orders.models import Order
from app.domains.customers.models import CustomerProfile
from app.domains.ai.orchestrator import AIOrchestrator

logger = structlog.get_logger(__name__)

# Follow-up intervals (in hours)
FOLLOWUP_INTERVALS = {
    "order_confirmation": 2,  # X hours: Check if order is confirmed
    "delivery_check_1": 48,   # Y hours: Ask if delivered (2 days)
    "delivery_check_2": 72,   # Z hours: Ask again if not delivered (3 days)
    "request_review": 120     # G hours: Ask for review after delivery (5 days)
}

# Follow-up messages
FOLLOWUP_MESSAGES = {
    "order_confirmation": {
        "ar": """مرحباً! 👋

أردت التأكد من طلبك #{order_id}.

هل كل شيء على ما يرام مع الطلب؟ أم تحتاج إلى تعديل؟

يمكنك الرد بـ "نعم" للتأكيد أو "إلغاء" إذا أردت إلغاء الطلب.""",
        "en": """Hello! 👋

I wanted to confirm your order #{order_id}.

Is everything okay with the order? Or do you need to make changes?

Reply "yes" to confirm or "cancel" if you want to cancel the order."""
    },
    "delivery_check": {
        "ar": """مرحباً! 📦

طلبك #{order_id} كان من المفترض أن يصل.

هل استلمت الطلب؟

يرجى الرد بـ "نعم" إذا استلمته أو "لا" إذا لم يصل بعد.""",
        "en": """Hello! 📦

Your order #{order_id} should have arrived.

Did you receive your order?

Please reply "yes" if you received it or "no" if it hasn't arrived yet."""
    },
    "delivery_followup": {
        "ar": """مرحباً مرة أخرى! 🚚

لا يزال طلبك #{order_id} لم يصل؟

هذا غير طبيعي. دعني أتحقق من حالة الشحن وأساعدك.

هل تريد رقم التتبع؟""",
        "en": """Hello again! 🚚

Your order #{order_id} still hasn't arrived?

This is unusual. Let me check the shipping status and help you.

Would you like the tracking number?"""
    },
    "request_review": {
        "ar": """مرحباً! ⭐

أتمنى أن تكون راضياً عن طلبك #{order_id}!

هل يمكنك تقييم تجربتك معنا؟

من 1 إلى 5، كم تقيم المنتج والخدمة؟""",
        "en": """Hello! ⭐

I hope you're satisfied with your order #{order_id}!

Could you rate your experience with us?

From 1 to 5, how would you rate the product and service?"""
    }
}


async def check_and_send_followups(db: AsyncSession) -> int:
    """
    Check all orders and send appropriate follow-up messages.
    This should be called periodically (e.g., every hour) by a background task.
    
    Returns:
        Number of follow-ups sent
    """
    followups_sent = 0
    now = datetime.utcnow()
    
    try:
        # Get all orders that might need follow-up
        result = await db.execute(
            select(Order).where(
                and_(
                    Order.status.in_(["pending", "processing", "shipped", "fulfilled"]),
                    Order.order_date.isnot(None)
                )
            )
        )
        orders = result.scalars().all()
        
        for order in orders:
            if not order.customer_id:
                continue
            
            order_age_hours = (now - order.order_date).total_seconds() / 3600
            
            # Check which follow-up to send
            followup_type = None
            
            # 1. Order confirmation (after X hours, only for pending/processing)
            if (order.status in ["pending", "processing"] and 
                order_age_hours >= FOLLOWUP_INTERVALS["order_confirmation"] and
                not _has_sent_followup(order, "order_confirmation")):
                followup_type = "order_confirmation"
            
            # 2. First delivery check (after Y hours, only for shipped)
            elif (order.status == "shipped" and 
                  order_age_hours >= FOLLOWUP_INTERVALS["delivery_check_1"] and
                  not _has_sent_followup(order, "delivery_check")):
                followup_type = "delivery_check"
            
            # 3. Second delivery check (after Z hours, still shipped)
            elif (order.status == "shipped" and 
                  order_age_hours >= FOLLOWUP_INTERVALS["delivery_check_2"] and
                  _has_sent_followup(order, "delivery_check") and
                  not _has_sent_followup(order, "delivery_followup")):
                followup_type = "delivery_followup"
            
            # 4. Request review (after G hours, fulfilled)
            elif (order.status == "fulfilled" and 
                  order.fulfilled_date and
                  (now - order.fulfilled_date).total_seconds() / 3600 >= FOLLOWUP_INTERVALS["request_review"] and
                  not _has_sent_followup(order, "request_review")):
                followup_type = "request_review"
            
            # Send follow-up if needed
            if followup_type:
                success = await _send_followup(
                    order=order,
                    followup_type=followup_type,
                    db=db
                )
                if success:
                    followups_sent += 1
                    # Mark follow-up as sent
                    _mark_followup_sent(order, followup_type)
                    await db.commit()
        
        logger.info(f"Follow-up check complete", followups_sent=followups_sent, orders_checked=len(orders))
        return followups_sent
        
    except Exception as e:
        logger.error("Error in follow-up check", error=str(e))
        return followups_sent


def _has_sent_followup(order: Order, followup_type: str) -> bool:
    """Check if a specific follow-up has already been sent for this order."""
    if not order.extra_data:
        return False
    
    followups_sent = order.extra_data.get("followups_sent", [])
    return followup_type in followups_sent


def _mark_followup_sent(order: Order, followup_type: str):
    """Mark a follow-up as sent in the order's extra_data."""
    if not order.extra_data:
        order.extra_data = {}
    
    if "followups_sent" not in order.extra_data:
        order.extra_data["followups_sent"] = []
    
    if followup_type not in order.extra_data["followups_sent"]:
        order.extra_data["followups_sent"].append(followup_type)
        order.extra_data["last_followup"] = datetime.utcnow().isoformat()


async def _send_followup(
    order: Order,
    followup_type: str,
    db: AsyncSession,
    language: str = "ar"
) -> bool:
    """Send a follow-up message to the customer."""
    try:
        if followup_type not in FOLLOWUP_MESSAGES:
            logger.warning(f"Unknown follow-up type: {followup_type}")
            return False
        
        message = FOLLOWUP_MESSAGES[followup_type][language].format(
            order_id=order.external_id
        )
        
        # Send via AI orchestrator
        orchestrator = AIOrchestrator(db)
        result = await orchestrator._send_whatsapp_message(
            customer_id=order.customer_id,
            message=message,
            project_id=order.project_id
        )
        
        if result.get("status") == "success":
            logger.info(
                "Follow-up sent",
                order_id=str(order.id),
                followup_type=followup_type,
                customer_id=str(order.customer_id)
            )
            return True
        else:
            logger.error(
                "Failed to send follow-up",
                order_id=str(order.id),
                followup_type=followup_type,
                error=result.get("message")
            )
            return False
            
    except Exception as e:
        logger.error(
            "Error sending follow-up",
            order_id=str(order.id),
            followup_type=followup_type,
            error=str(e)
        )
        return False
