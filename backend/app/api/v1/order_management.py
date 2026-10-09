"""
Order Management API endpoints with AI-powered automation.
Handles order lifecycle, progress tracking, and customer notifications.
"""

from typing import Any, Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel
import structlog

from app.core.database import get_db
from app.core.context import TenantContext
from app.api.dependencies.tenant import get_tenant_context
from app.domains.orders.models import OrderStatus
from app.services.order_manager_service import OrderManagerService

router = APIRouter()
logger = structlog.get_logger(__name__)


class OrderStatusUpdate(BaseModel):
    """Update order status request."""
    order_id: UUID
    new_status: str  # pending, processing, fulfilled, shipped, cancelled
    notify_customer: bool = True
    note: Optional[str] = None
    auto_message: bool = True


class BulkOrderAction(BaseModel):
    """Bulk order action request."""
    order_ids: List[UUID]
    action: str  # progress, fulfill, cancel
    notify_customers: bool = True


class OrderNotification(BaseModel):
    """Send order notification request."""
    order_id: UUID
    message_type: str  # confirmation, processing, shipped, delivered, delay, custom
    custom_message: Optional[str] = None


class ScheduleFollowUp(BaseModel):
    """Schedule follow-up message."""
    order_id: UUID
    delay_hours: int
    message: Optional[str] = None


# ============================================================================
# Order Status Management
# ============================================================================

@router.post("/{project_id}/orders/update-status")
async def update_order_status(

    request: OrderStatusUpdate,
    context: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Update order status and optionally notify customer with AI-generated message.

    **Status Options:**
    - pending: Order received, not yet processed
    - processing: Order is being prepared
    - shipped: Order has been shipped
    - fulfilled: Order completed
    - cancelled: Order cancelled

    **Features:**
    - Automatic customer notification (optional)
    - AI-generated personalized messages
    - Status history tracking
    - Timeline updates
    """
    order_manager = OrderManagerService(db, context)

    try:
        # Parse status
        try:
            new_status = OrderStatus[request.new_status.upper()]
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {request.new_status}"
            )

        result = await order_manager.update_order_status(
            order_id=request.order_id,
            new_status=new_status,
            notify_customer=request.notify_customer,
            note=request.note,
            auto_message=request.auto_message
        )

        return {
            "success": True,
            **result
        }

    except Exception as e:
        logger.error("Failed to update order status", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update order status: {str(e)}"
        )


@router.post("/{project_id}/orders/{order_id}/auto-progress")
async def auto_progress_order(
    order_id: UUID,
    reason: Optional[str] = None,
    context: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    AI automatically determines and progresses order to next logical status.

    **AI Decision Factors:**
    - Current status
    - Time since last update
    - Order age
    - Historical patterns
    - Business rules

    **Safe & Intelligent:**
    - Won't progress if conditions aren't met
    - Provides reasoning for decisions
    - Automatically notifies customer
    """
    order_manager = OrderManagerService(db, context)

    try:
        result = await order_manager.auto_progress_order(
            order_id=order_id,
            reason=reason
        )

        return {
            "success": True,
            **result
        }

    except Exception as e:
        logger.error("Failed to auto-progress order", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to auto-progress order: {str(e)}"
        )


@router.get("/{project_id}/orders/{order_id}/progress")
async def get_order_progress(
    order_id: UUID,
    context: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get comprehensive order progress and timeline.

    **Returns:**
    - Current status
    - Progress percentage (0-100%)
    - Complete timeline with all status changes
    - Next expected status
    - Estimated completion date
    - All customer notifications sent
    - Order details

    **Perfect for:**
    - Customer service dashboards
    - Order tracking pages
    - Status monitoring
    """
    order_manager = OrderManagerService(db, context)

    try:
        progress = await order_manager.get_order_progress(order_id)

        return {
            "success": True,
            **progress
        }

    except Exception as e:
        logger.error("Failed to get order progress", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get order progress: {str(e)}"
        )


@router.get("/{project_id}/orders/requiring-attention")
async def get_orders_requiring_attention(
    max_age_hours: int = 48,
    context: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get orders that need attention (stuck, delayed, pending too long).

    **Identifies:**
    - Orders pending for more than specified hours
    - Orders stuck in processing
    - Stale orders

    **Use for:**
    - Daily order review
    - Automated alerts
    - Priority queue management
    """
    order_manager = OrderManagerService(db, context)

    try:
        attention_orders = await order_manager.get_orders_requiring_attention(
            max_age_hours=max_age_hours
        )

        return {
            "success": True,
            "total": len(attention_orders),
            "orders": attention_orders
        }

    except Exception as e:
        logger.error("Failed to get orders requiring attention", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get orders: {str(e)}"
        )


@router.post("/{project_id}/orders/bulk-action")
async def bulk_process_orders(

    request: BulkOrderAction,
    context: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Process multiple orders with same action.

    **Actions:**
    - progress: Auto-progress each order to next status
    - fulfill: Mark all orders as fulfilled
    - cancel: Cancel all orders

    **Bulk Operations:**
    - Up to 100 orders at once
    - Automatic customer notifications
    - Error handling per order
    - Detailed results
    """
    if len(request.order_ids) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 100 orders per bulk operation"
        )

    order_manager = OrderManagerService(db, context)

    try:
        results = await order_manager.bulk_process_orders(
            order_ids=request.order_ids,
            action=request.action,
            notify_customers=request.notify_customers
        )

        return {
            "success": True,
            **results
        }

    except Exception as e:
        logger.error("Failed to bulk process orders", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk process: {str(e)}"
        )


# ============================================================================
# Customer Communication
# ============================================================================

@router.post("/{project_id}/orders/notify")
async def send_order_notification(

    request: OrderNotification,
    context: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Send specific type of notification to customer.

    **Message Types:**
    - confirmation: Order received
    - processing: Being prepared
    - shipped: On the way
    - delivered: Arrived
    - delay: Delayed notification
    - custom: Your own message

    **AI-Generated:**
    - Personalized to customer
    - Platform-appropriate tone
    - Includes order details
    """
    order_manager = OrderManagerService(db, context)

    try:
        result = await order_manager.send_order_update(
            order_id=request.order_id,
            message_type=request.message_type,
            custom_message=request.custom_message
        )

        return {
            "success": True,
            **result
        }

    except Exception as e:
        logger.error("Failed to send notification", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send notification: {str(e)}"
        )


@router.post("/{project_id}/orders/schedule-followup")
async def schedule_followup(

    request: ScheduleFollowUp,
    context: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Schedule a follow-up message for later.

    **Use Cases:**
    - "How's your order?" after 3 days
    - "Did it arrive?" after expected delivery
    - "Need anything?" after delivery

    **Automatic Sending:**
    - Queued for specified time
    - Sent via customer's preferred channel
    - Tracked in order history
    """
    order_manager = OrderManagerService(db, context)

    try:
        result = await order_manager.schedule_follow_up(
            order_id=request.order_id,
            delay_hours=request.delay_hours,
            message=request.message
        )

        return {
            "success": True,
            **result
        }

    except Exception as e:
        logger.error("Failed to schedule follow-up", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to schedule follow-up: {str(e)}"
        )


# ============================================================================
# Analytics & Monitoring
# ============================================================================

@router.get("/{project_id}/orders/stats")
async def get_order_statistics(

    context: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get order management statistics.

    **Metrics:**
    - Total orders by status
    - Average processing time
    - Notification rate
    - Auto-progression rate
    - Orders requiring attention
    """
    from app.domains.orders.models import Order
    from app.domains.messages.models import Message
    from sqlalchemy import func, select, and_
    from datetime import datetime, timedelta
    from app.domains.orders.repository import OrderRepository

    try:
        order_repo = OrderRepository(db)
        stats = await order_repo.get_management_statistics(context)
        
        status_counts = stats["orders_by_status"]
        total_orders = stats["total_orders"]
        recent_orders = stats["recent_orders_7days"]

        # Orders with notifications
        result = await db.execute(
            select(func.count(func.distinct(Message.order_id)))
            .where(
                and_(
                    Message.project_id == context.project_id,
                    Message.ai_generated == True,
                    Message.order_id.isnot(None)
                )
            )
        )
        orders_with_notifications = result.scalar() or 0

        notification_rate = (orders_with_notifications / total_orders * 100) if total_orders > 0 else 0

        return {
            "success": True,
            "total_orders": total_orders,
            "orders_by_status": status_counts,
            "recent_orders_7days": recent_orders,
            "notification_rate": round(notification_rate, 2),
            "orders_with_notifications": orders_with_notifications
        }

    except Exception as e:
        logger.error("Failed to get order statistics", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )
