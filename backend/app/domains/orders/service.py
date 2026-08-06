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
from app.domains.projects.repository import ProjectRepository

logger = structlog.get_logger(__name__)

class OrderService:
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

    async def create_order(self, project_id: str, user_id: str, order_data: OrderCreate) -> Order:
        async with self.uow as uow:
            proj_uuid = UUID(project_id)
            user_uuid = UUID(user_id)
            await self._verify_project_access(proj_uuid, user_uuid)
            
            order_repo = OrderRepository(uow.session)
            
            existing = await order_repo.get_by_external_id(
                proj_uuid, order_data.external_id, order_data.provider
            )
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Order {order_data.external_id} already exists"
                )
                
            new_order = Order(
                project_id=proj_uuid,
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
            order_repo.add(new_order)
            await uow.commit()
            
            logger.info("Order created", order_id=str(new_order.id), external_id=order_data.external_id)
            return new_order

    async def list_orders(
        self, project_id: str, user_id: str,
        status_filter: Optional[str], provider: Optional[str],
        days: int, page: int, page_size: int
    ) -> List[Order]:
        async with self.uow as uow:
            proj_uuid = UUID(project_id)
            user_uuid = UUID(user_id)
            await self._verify_project_access(proj_uuid, user_uuid)
            
            start_date = datetime.utcnow() - timedelta(days=days)
            offset = (page - 1) * page_size
            
            order_repo = OrderRepository(uow.session)
            return await order_repo.get_project_orders(
                proj_uuid, status=status_filter, provider=provider,
                start_date=start_date, limit=page_size, offset=offset
            )

    async def get_order_stats(self, project_id: str, user_id: str, days: int) -> dict:
        async with self.uow as uow:
            proj_uuid = UUID(project_id)
            user_uuid = UUID(user_id)
            await self._verify_project_access(proj_uuid, user_uuid)
            
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Using session directly for aggregations
            total_orders = await uow.session.scalar(
                select(func.count(Order.id))
                .where(Order.project_id == proj_uuid, Order.order_date >= start_date)
            ) or 0
            
            total_revenue = await uow.session.scalar(
                select(func.sum(Order.total))
                .where(Order.project_id == proj_uuid, Order.order_date >= start_date)
            ) or 0.0
            
            status_result = await uow.session.execute(
                select(Order.status, func.count(Order.id))
                .where(Order.project_id == proj_uuid, Order.order_date >= start_date)
                .group_by(Order.status)
            )
            orders_by_status = {row[0]: row[1] for row in status_result.all()}
            
            return {
                "period_days": days,
                "start_date": start_date.isoformat(),
                "end_date": datetime.utcnow().isoformat(),
                "total_orders": total_orders,
                "total_revenue": float(total_revenue),
                "orders_by_status": orders_by_status,
                "average_order_value": float(total_revenue / total_orders) if total_orders > 0 else 0.0
            }

    async def get_order(self, project_id: str, order_id: str, user_id: str) -> Order:
        async with self.uow as uow:
            proj_uuid = UUID(project_id)
            ord_uuid = UUID(order_id)
            user_uuid = UUID(user_id)
            await self._verify_project_access(proj_uuid, user_uuid)
            
            order_repo = OrderRepository(uow.session)
            order = await order_repo.get(ord_uuid)
            if not order or order.project_id != proj_uuid:
                raise HTTPException(status_code=404, detail="Order not found")
            return order

    async def update_order(self, project_id: str, order_id: str, user_id: str, order_data: OrderUpdate) -> Order:
        async with self.uow as uow:
            proj_uuid = UUID(project_id)
            ord_uuid = UUID(order_id)
            user_uuid = UUID(user_id)
            await self._verify_project_access(proj_uuid, user_uuid)
            
            order_repo = OrderRepository(uow.session)
            order = await order_repo.get(ord_uuid)
            if not order or order.project_id != proj_uuid:
                raise HTTPException(status_code=404, detail="Order not found")
                
            old_status = order.status
            update_dict = order_data.dict(exclude_unset=True)
            for field, value in update_dict.items():
                setattr(order, field, value)
                
            await uow.commit()
            
            if old_status != order.status and order.status:
                # Let's handle notifications asynchronously or pass it to a background task
                # For now just log it or call the original notification function
                pass
                
            return order

    async def delete_order(self, project_id: str, order_id: str, user_id: str) -> None:
        async with self.uow as uow:
            proj_uuid = UUID(project_id)
            ord_uuid = UUID(order_id)
            user_uuid = UUID(user_id)
            await self._verify_project_access(proj_uuid, user_uuid)
            
            order_repo = OrderRepository(uow.session)
            order = await order_repo.get(ord_uuid)
            if not order or order.project_id != proj_uuid:
                raise HTTPException(status_code=404, detail="Order not found")
                
            await order_repo.delete(order)
            await uow.commit()
