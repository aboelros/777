"""
Product Catalog API endpoints
"""

from typing import Any, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, status, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.api.dependencies.tenant import get_tenant_context, TenantContext
from app.core.uow import UnitOfWork
from app.domains.products.schemas import ProductCreate, ProductUpdate, ProductResponse
from app.domains.products.service import ProductService
from app.domains.products.image_service import ProductImageService

router = APIRouter()
logger = structlog.get_logger(__name__)

async def get_product_image_service(db: AsyncSession = Depends(get_db)) -> ProductImageService:
    return ProductImageService(UnitOfWork(db))

async def get_product_service(db: AsyncSession = Depends(get_db)) -> ProductService:
    return ProductService(UnitOfWork(db))

@router.post("/{project_id}/bulk-upload")
async def bulk_upload_products(
    project_id: UUID,
    file: UploadFile = File(...),
    tenant: TenantContext = Depends(get_tenant_context),
    service: ProductService = Depends(get_product_service)
) -> Any:
    
    from fastapi import HTTPException
    if tenant.role not in ['owner', 'moderator']:
        raise HTTPException(status_code=403, detail='Access denied.')
    return await service.bulk_upload_products(tenant, file)

@router.get("/{project_id}/{product_id}")
async def get_product(
    project_id: UUID,
    product_id: UUID,
    tenant: TenantContext = Depends(get_tenant_context),
    service: ProductService = Depends(get_product_service)
) -> Any:
    return await service.get_product(tenant, str(product_id))

@router.put("/{project_id}/{product_id}")
async def update_product(
    project_id: UUID,
    product_id: UUID,
    product_update: ProductUpdate,
    tenant: TenantContext = Depends(get_tenant_context),
    service: ProductService = Depends(get_product_service)
) -> Any:
    from fastapi import HTTPException
    if tenant.role not in ['owner', 'moderator']:
        raise HTTPException(status_code=403, detail='Access denied.')

    return await service.update_product(tenant, str(product_id), product_update)

@router.delete("/{project_id}/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    project_id: UUID,
    product_id: UUID,
    tenant: TenantContext = Depends(get_tenant_context),
    service: ProductService = Depends(get_product_service)
) -> None:
    from fastapi import HTTPException
    if tenant.role not in ['owner', 'moderator']:
        raise HTTPException(status_code=403, detail='Access denied.')

    
    from fastapi import HTTPException
    if tenant.role not in ['owner', 'moderator']:
        raise HTTPException(status_code=403, detail='Access denied.')
    await service.delete_product(tenant, str(product_id))

@router.get("/{project_id}")
async def list_products(
    project_id: UUID,
    skip: int = 0,
    limit: int = 100,
    category: str | None = None,
    active_only: bool = True,
    tenant: TenantContext = Depends(get_tenant_context),
    service: ProductService = Depends(get_product_service)
) -> Any:
    return await service.list_products(tenant, skip, limit, category, active_only)

@router.post("/{project_id}")
async def create_product(
    project_id: UUID,
    product: ProductCreate,
    tenant: TenantContext = Depends(get_tenant_context),
    service: ProductService = Depends(get_product_service)
) -> Any:
    from fastapi import HTTPException
    if tenant.role not in ['owner', 'moderator']:
        raise HTTPException(status_code=403, detail='Access denied.')

    return await service.create_product(tenant, product)

# Image Management Endpoints

@router.post("/{project_id}/{product_id}/images", status_code=status.HTTP_201_CREATED)
async def upload_product_image(
    project_id: UUID,
    product_id: UUID,
    file: UploadFile = File(...),
    description: str = "",
    tenant: TenantContext = Depends(get_tenant_context),
    image_service: ProductImageService = Depends(get_product_image_service)
) -> Any:
    from fastapi import HTTPException
    if tenant.role not in ['owner', 'moderator']:
        raise HTTPException(status_code=403, detail='Access denied.')

    
    from fastapi import HTTPException
    if tenant.role not in ['owner', 'moderator']:
        raise HTTPException(status_code=403, detail='Access denied.')
    return await image_service.upload_product_image(tenant, str(product_id), file, description)

@router.delete("/{project_id}/{product_id}/images/{image_index}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_image(
    project_id: UUID,
    product_id: UUID,
    image_index: int,
    tenant: TenantContext = Depends(get_tenant_context),
    image_service: ProductImageService = Depends(get_product_image_service)
) -> None:
    from fastapi import HTTPException
    if tenant.role not in ['owner', 'moderator']:
        raise HTTPException(status_code=403, detail='Access denied.')

    
    from fastapi import HTTPException
    if tenant.role not in ['owner', 'moderator']:
        raise HTTPException(status_code=403, detail='Access denied.')
    await image_service.delete_product_image(tenant, str(product_id), image_index)

@router.patch("/{project_id}/{product_id}/images/{image_index}")
async def update_product_image(
    project_id: UUID,
    product_id: UUID,
    image_index: int,
    description: str = "",
    order: int | None = Query(None),
    tenant: TenantContext = Depends(get_tenant_context),
    image_service: ProductImageService = Depends(get_product_image_service)
) -> Any:
    return await image_service.update_product_image(tenant, str(product_id), image_index, description, order)
