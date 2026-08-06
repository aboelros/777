"""
Order management endpoints.
"""

from typing import List, Any, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.core.uow import UnitOfWork
from app.domains.orders.service import OrderService
from app.domains.orders.schemas import OrderCreate, OrderUpdate, OrderResponse

router = APIRouter()
logger = structlog.get_logger(__name__)

async def get_order_service(db: AsyncSession = Depends(get_db)) -> OrderService:
    return OrderService(UnitOfWork(db))

@router.post("/{project_id}", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    project_id: UUID,
    order_data: OrderCreate,
    user_id: str = Depends(get_current_user_id),
    service: OrderService = Depends(get_order_service)
) -> Any:
    return await service.create_order(str(project_id), user_id, order_data)

@router.get("/{project_id}", response_model=List[OrderResponse])
async def list_orders(
    project_id: UUID,
    status: Optional[str] = Query(None, description="Filter by status"),
    provider: Optional[str] = Query(None, description="Filter by provider"),
    days: int = Query(30, description="Number of days to look back", ge=1, le=365),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
    service: OrderService = Depends(get_order_service)
) -> Any:
    return await service.list_orders(str(project_id), user_id, status, provider, days, page, page_size)

@router.get("/{project_id}/stats")  # Alias for backward compatibility  
@router.get("/{project_id}/stats/summary")
async def get_order_stats(
    project_id: UUID,
    days: int = Query(30, description="Number of days to analyze", ge=1, le=365),
    user_id: str = Depends(get_current_user_id),
    service: OrderService = Depends(get_order_service)
) -> Any:
    return await service.get_order_stats(str(project_id), user_id, days)

@router.get("/{project_id}/{order_id}", response_model=OrderResponse)
async def get_order(
    project_id: UUID,
    order_id: UUID,
    user_id: str = Depends(get_current_user_id),
    service: OrderService = Depends(get_order_service)
) -> Any:
    return await service.get_order(str(project_id), str(order_id), user_id)

@router.patch("/{project_id}/{order_id}", response_model=OrderResponse)
async def update_order(
    project_id: UUID,
    order_id: UUID,
    order_data: OrderUpdate,
    user_id: str = Depends(get_current_user_id),
    service: OrderService = Depends(get_order_service)
) -> Any:
    return await service.update_order(str(project_id), str(order_id), user_id, order_data)

@router.delete("/{project_id}/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    project_id: UUID,
    order_id: UUID,
    user_id: str = Depends(get_current_user_id),
    service: OrderService = Depends(get_order_service)
) -> None:
    await service.delete_order(str(project_id), str(order_id), user_id)
