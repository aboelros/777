from typing import List, Optional, Any
from uuid import UUID
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy import func, select
import structlog

from app.core.uow import UnitOfWork
from app.domains.orders.repository import OrderRepository
from app.domains.orders.models import Order
from app.domains.orders.schemas import OrderCreate, OrderUpdate
from app.core.context import TenantContext

logger = structlog.get_logger(__name__)

class OrderService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow


    async def create_order(self, context, order_data: OrderCreate) -> Order:
        async with self.uow as uow:
            
            order_repo = OrderRepository(uow.session)
            
            existing = await order_repo.get_by_external_id(
                context.project_id, order_data.external_id, order_data.provider
            )
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Order {order_data.external_id} already exists"
                )
                
            new_order = Order(
                project_id=context.project_id,
                external_id=order_data.external_id,
                provider=order_data.provider,
                customer_id=order_data.customer_id,
                status=order_data.status,
                customer=order_data.customer,
                items=order_data.items,
                total=order_data.total,
                currency=order_data.currency,
                extra_data=order_data.extra_data,
                tags=order_data.tags,
                order_date=order_data.order_date or datetime.utcnow()
            )
            order_repo.add(new_order)
            await uow.commit()
            await uow.session.refresh(new_order)
            
            logger.info("Order created", order_id=str(new_order.id), external_id=order_data.external_id)
            return new_order

    async def list_orders(
        self, context,
        status_filter: Optional[str], provider: Optional[str],
        days: int, page: int, page_size: int
    ) -> List[Order]:
        async with self.uow as uow:
            
            start_date = datetime.utcnow() - timedelta(days=days)
            offset = (page - 1) * page_size
            
            order_repo = OrderRepository(uow.session)
            return await order_repo.get_project_orders(
                context.project_id, status=status_filter, provider=provider,
                start_date=start_date, limit=page_size, offset=offset
            )

    async def get_order_stats(self, context, days: int) -> dict:
        async with self.uow as uow:
            
            start_date = datetime.utcnow() - timedelta(days=days)
            
            order_repo = OrderRepository(uow.session)
            stats = await order_repo.get_order_stats(context, start_date)
            
            return {
                "period_days": days,
                "start_date": start_date.isoformat(),
                "end_date": datetime.utcnow().isoformat(),
                "total_orders": stats["total_orders"],
                "total_revenue": float(stats["total_revenue"]),
                "orders_by_status": stats["orders_by_status"],
                "average_order_value": float(stats["total_revenue"] / stats["total_orders"]) if stats["total_orders"] > 0 else 0.0
            }

    async def get_order(self, order_id: str, context) -> Order:
        async with self.uow as uow:
            ord_uuid = UUID(order_id)
            
            order_repo = OrderRepository(uow.session)
            order = await order_repo.get_by_context(ord_uuid, context)
            if not order:
                raise HTTPException(status_code=404, detail="Order not found")
            await uow.session.refresh(order)
            return order

    async def update_order(self, order_id: str, context, order_data: OrderUpdate) -> Order:
        async with self.uow as uow:
            ord_uuid = UUID(order_id)
            
            order_repo = OrderRepository(uow.session)
            order = await order_repo.get_by_context(ord_uuid, context)
            if not order:
                raise HTTPException(status_code=404, detail="Order not found")
                
            old_status = order.status
            update_dict = order_data.dict(exclude_unset=True)
            for field, value in update_dict.items():
                setattr(order, field, value)
                
            await uow.commit()
            await uow.session.refresh(order)
            
            if old_status != order.status and order.status:
                # Let's handle notifications asynchronously or pass it to a background task
                # For now just log it or call the original notification function
                pass
                
            return order

    async def delete_order(self, order_id: str, context) -> None:
        async with self.uow as uow:
            ord_uuid = UUID(order_id)
            
            order_repo = OrderRepository(uow.session)
            order = await order_repo.get_by_context(ord_uuid, context)
            if not order:
                raise HTTPException(status_code=404, detail="Order not found")
                
            await order_repo.delete(order)
            await uow.commit()
