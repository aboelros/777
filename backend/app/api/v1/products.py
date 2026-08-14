"""
Product Catalog API endpoints
"""

from typing import Any, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, status, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.core.uow import UnitOfWork
from app.domains.products.schemas import ProductCreate, ProductUpdate, ProductResponse
from app.domains.products.service import ProductService

router = APIRouter()
logger = structlog.get_logger(__name__)

async def get_product_service(db: AsyncSession = Depends(get_db)) -> ProductService:
    return ProductService(UnitOfWork(db))

@router.post("/{project_id}/bulk-upload")
async def bulk_upload_products(
    project_id: UUID,
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    service: ProductService = Depends(get_product_service)
) -> Any:
    return await service.bulk_upload_products(str(project_id), user_id, file)

@router.get("/{project_id}/{product_id}")
async def get_product(
    project_id: UUID,
    product_id: UUID,
    user_id: str = Depends(get_current_user_id),
    service: ProductService = Depends(get_product_service)
) -> Any:
    return await service.get_product(str(project_id), str(product_id), user_id)

@router.put("/{project_id}/{product_id}")
async def update_product(
    project_id: UUID,
    product_id: UUID,
    product_update: ProductUpdate,
    user_id: str = Depends(get_current_user_id),
    service: ProductService = Depends(get_product_service)
) -> Any:
    return await service.update_product(str(project_id), str(product_id), user_id, product_update)

@router.delete("/{project_id}/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    project_id: UUID,
    product_id: UUID,
    user_id: str = Depends(get_current_user_id),
    service: ProductService = Depends(get_product_service)
) -> None:
    await service.delete_product(str(project_id), str(product_id), user_id)

@router.get("/{project_id}")
async def list_products(
    project_id: UUID,
    skip: int = 0,
    limit: int = 100,
    category: str | None = None,
    active_only: bool = True,
    user_id: str = Depends(get_current_user_id),
    service: ProductService = Depends(get_product_service)
) -> Any:
    return await service.list_products(str(project_id), user_id, skip, limit, category, active_only)

@router.post("/{project_id}")
async def create_product(
    project_id: UUID,
    product: ProductCreate,
    user_id: str = Depends(get_current_user_id),
    service: ProductService = Depends(get_product_service)
) -> Any:
    return await service.create_product(str(project_id), user_id, product)

# Image Management Endpoints

@router.post("/{project_id}/{product_id}/images", status_code=status.HTTP_201_CREATED)
async def upload_product_image(
    project_id: UUID,
    product_id: UUID,
    file: UploadFile = File(...),
    description: str = "",
    user_id: str = Depends(get_current_user_id),
    service: ProductService = Depends(get_product_service)
) -> Any:
    return await service.upload_product_image(str(project_id), str(product_id), user_id, file, description)

@router.delete("/{project_id}/{product_id}/images/{image_index}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_image(
    project_id: UUID,
    product_id: UUID,
    image_index: int,
    user_id: str = Depends(get_current_user_id),
    service: ProductService = Depends(get_product_service)
) -> None:
    await service.delete_product_image(str(project_id), str(product_id), image_index, user_id)

@router.patch("/{project_id}/{product_id}/images/{image_index}")
async def update_product_image(
    project_id: UUID,
    product_id: UUID,
    image_index: int,
    description: str = "",
    order: int | None = Query(None),
    user_id: str = Depends(get_current_user_id),
    service: ProductService = Depends(get_product_service)
) -> Any:
    return await service.update_product_image(str(project_id), str(product_id), image_index, description, order, user_id)
