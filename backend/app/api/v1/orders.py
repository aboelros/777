"""
Order management endpoints.
"""

from typing import List, Any, Optional
from uuid import UUID
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import structlog

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.db.models import Project, Order
from app.models.schemas import OrderCreate, OrderUpdate, OrderResponse

router = APIRouter()
logger = structlog.get_logger(__name__)


async def verify_project_access(project_id: UUID, user_id: str, db: AsyncSession) -> Project:
    """Helper to verify user has access to project."""
    result = await db.execute(
        select(Project)
        .where(Project.id == project_id)
        .where(Project.owner_id == UUID(user_id))
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or access denied"
        )
    
    return project


@router.post("/{project_id}", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    project_id: UUID,
    order_data: OrderCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Create a new order manually.
    
    Typically orders are created automatically via webhooks from integrated platforms.
    """
    # Verify project access
    await verify_project_access(project_id, user_id, db)
    
    # Check for duplicate external_id
    result = await db.execute(
        select(Order)
        .where(Order.project_id == project_id)
        .where(Order.external_id == order_data.external_id)
        .where(Order.provider == order_data.provider)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order {order_data.external_id} already exists"
        )
    
    new_order = Order(
        project_id=project_id,
        external_id=order_data.external_id,
        provider=order_data.provider,
        customer_id=order_data.customer_id,
        status=order_data.status,
        customer=order_data.customer,
        items=order_data.items,
        total=order_data.total,
        currency=order_data.currency,
        metadata=order_data.metadata,
        tags=order_data.tags,
        order_date=order_data.order_date or datetime.utcnow()
    )
    
    db.add(new_order)
    await db.commit()
    await db.refresh(new_order)
    
    logger.info(
        "Order created",
        order_id=str(new_order.id),
        external_id=order_data.external_id,
        project_id=str(project_id)
    )
    
    return new_order


@router.get("/{project_id}", response_model=List[OrderResponse])
async def list_orders(
    project_id: UUID,
    status: Optional[str] = Query(None, description="Filter by status"),
    provider: Optional[str] = Query(None, description="Filter by provider"),
    days: int = Query(30, description="Number of days to look back", ge=1, le=365),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    List orders for a project with optional filters.
    """
    # Verify project access
    await verify_project_access(project_id, user_id, db)
    
    # Build query
    query = select(Order).where(Order.project_id == project_id)
    
    # Apply filters
    if status:
        query = query.where(Order.status == status)
    if provider:
        query = query.where(Order.provider == provider)
    
    # Date filter
    start_date = datetime.utcnow() - timedelta(days=days)
    query = query.where(Order.order_date >= start_date)
    
    # Order and pagination
    query = query.order_by(Order.order_date.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    orders = result.scalars().all()
    
    return orders


@router.get("/{project_id}/stats")  # Alias for backward compatibility  
@router.get("/{project_id}/stats/summary")
async def get_order_stats(
    project_id: UUID,
    days: int = Query(30, description="Number of days to analyze", ge=1, le=365),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get order statistics summary for a project.
    """
    # Verify project access
    await verify_project_access(project_id, user_id, db)
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Total orders
    result = await db.execute(
        select(func.count(Order.id))
        .where(Order.project_id == project_id)
        .where(Order.order_date >= start_date)
    )
    total_orders = result.scalar() or 0
    
    # Total revenue
    result = await db.execute(
        select(func.sum(Order.total))
        .where(Order.project_id == project_id)
        .where(Order.order_date >= start_date)
    )
    total_revenue = result.scalar() or 0.0
    
    # Orders by status
    result = await db.execute(
        select(Order.status, func.count(Order.id))
        .where(Order.project_id == project_id)
        .where(Order.order_date >= start_date)
        .group_by(Order.status)
    )
    orders_by_status = {row[0]: row[1] for row in result.all()}
    
    return {
        "period_days": days,
        "start_date": start_date.isoformat(),
        "end_date": datetime.utcnow().isoformat(),
        "total_orders": total_orders,
        "total_revenue": float(total_revenue),
        "orders_by_status": orders_by_status,
        "average_order_value": float(total_revenue / total_orders) if total_orders > 0 else 0.0
    }


@router.get("/{project_id}/{order_id}", response_model=OrderResponse)
async def get_order(
    project_id: UUID,
    order_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get a specific order with full details.
    """
    # Verify project access
    await verify_project_access(project_id, user_id, db)
    
    result = await db.execute(
        select(Order)
        .where(Order.id == order_id)
        .where(Order.project_id == project_id)
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return order


@router.patch("/{project_id}/{order_id}", response_model=OrderResponse)
async def update_order(
    project_id: UUID,
    order_id: UUID,
    order_data: OrderUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Update an order's information.
    """
    # Verify project access
    await verify_project_access(project_id, user_id, db)
    
    result = await db.execute(
        select(Order)
        .where(Order.id == order_id)
        .where(Order.project_id == project_id)
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Track if status changed
    old_status = order.status
    
    # Update fields
    update_data = order_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(order, field, value)
    
    await db.commit()
    await db.refresh(order)
    
    logger.info("Order updated", order_id=str(order_id), project_id=str(project_id))
    
    # Send notification if status changed
    if old_status != order.status and order.status:
        from app.services.order_notifications import notify_customer_order_status
        try:
            await notify_customer_order_status(
                order_id=order_id,
                new_status=order.status,
                db=db,
                language="ar"  # Default to Arabic, can be detected from customer profile
            )
        except Exception as e:
            logger.error("Failed to send order notification", error=str(e))
            # Don't fail the update if notification fails
    
    return order


@router.delete("/{project_id}/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    project_id: UUID,
    order_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Delete an order.
    
    This will also delete associated messages.
    """
    # Verify project access
    await verify_project_access(project_id, user_id, db)
    
    result = await db.execute(
        select(Order)
        .where(Order.id == order_id)
        .where(Order.project_id == project_id)
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    await db.delete(order)
    await db.commit()
    
    logger.info("Order deleted", order_id=str(order_id), project_id=str(project_id))
    
    return None



