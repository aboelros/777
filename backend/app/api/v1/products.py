"""
Product Catalog API endpoints
"""

from typing import Any, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog
import csv
import io

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.db.models import Product, Project
from app.services.file_storage import FileStorageService
from pydantic import BaseModel

router = APIRouter()
logger = structlog.get_logger(__name__)


def sign_product_images(images: List[dict] | None) -> List[dict]:
    """
    Generate presigned URLs for product images.
    """
    if not images:
        return []
    
    signed_images = []
    for img in images:
        # Create a copy to avoid modifying the original object if it's from DB
        img_copy = img.copy() if isinstance(img, dict) else img
        
        # Handle dict images (new format)
        if isinstance(img_copy, dict) and "url" in img_copy:
            img_copy["url"] = FileStorageService.generate_presigned_url(img_copy["url"])
        # Handle string images (legacy format if any)
        elif isinstance(img_copy, str):
            # If it's just a string, we can't easily modify it in place if we want to return a dict
            # But if the API expects strings, we might return strings.
            # However, the code seems to use dicts.
            pass
            
        signed_images.append(img_copy)
    return signed_images


class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    sku: str | None = None
    price: float | None = None
    currency: str = "USD"
    stock_quantity: int = 0
    in_stock: bool = True
    images: List[dict] = [] # Changed to dict to match actual usage
    category: str | None = None
    tags: List[str] = []
    specifications: dict = {}
    faq: List[dict] = []
    keywords: List[str] = []
    storage_locations: List[dict] = []
    reorder_point: int = 0
    safety_stock: int = 0
    storage_notes: Optional[str] = None
    storage_attachments: List[str] = []


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    sku: str | None = None
    price: float | None = None
    currency: str | None = None
    stock_quantity: int | None = None
    in_stock: bool | None = None
    images: List[dict] | None = None # Changed to dict
    category: str | None = None
    tags: List[str] | None = None
    specifications: dict | None = None
    faq: List[dict] | None = None
    keywords: List[str] | None = None
    is_active: bool | None = None
    storage_locations: List[dict] | None = None
    reorder_point: int | None = None
    safety_stock: int | None = None
    storage_notes: Optional[str] = None
    storage_attachments: List[str] | None = None


class ProductResponse(BaseModel):
    id: str
    name: str
    description: str | None
    sku: str | None
    price: float | None
    currency: str
    stock_quantity: int
    in_stock: bool
    images: List[dict] # Changed to dict
    category: str | None
    tags: List[str]
    specifications: dict
    faq: List[dict]
    keywords: List[str]
    storage_locations: List[dict]
    reorder_point: int
    safety_stock: int
    storage_notes: Optional[str]
    storage_attachments: List[str]
    is_active: bool
    created_at: str
    updated_at: str | None

    class Config:
        from_attributes = True


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


# IMPORTANT: More specific routes (with 2+ params) MUST come before less specific routes
# Otherwise FastAPI will match /{project_id} before /{project_id}/{product_id}

@router.post("/{project_id}/bulk-upload")
async def bulk_upload_products(
    project_id: UUID,
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Bulk upload products from CSV file."""
    await verify_project_access(project_id, user_id, db)
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV"
        )
    
    contents = await file.read()
    csv_data = contents.decode('utf-8')
    csv_file = io.StringIO(csv_data)
    csv_reader = csv.DictReader(csv_file)
    
    products_created = 0
    errors = []
    
    for row_num, row in enumerate(csv_reader, start=2):
        try:
            product = Product(
                project_id=project_id,
                name=row.get('name', '').strip(),
                description=row.get('description', '').strip() or None,
                sku=row.get('sku', '').strip() or None,
                price=float(row.get('price', 0)) if row.get('price') else None,
                currency=row.get('currency', 'USD').strip(),
                stock_quantity=int(row.get('stock_quantity', 0)),
                in_stock=row.get('in_stock', 'true').lower() == 'true',
                category=row.get('category', '').strip() or None,
                tags=[tag.strip() for tag in row.get('tags', '').split(',') if tag.strip()],
                keywords=[kw.strip() for kw in row.get('keywords', '').split(',') if kw.strip()],
                reorder_point=int(row.get('reorder_point', 0)) if row.get('reorder_point') else 0,
                safety_stock=int(row.get('safety_stock', 0)) if row.get('safety_stock') else 0,
                storage_notes=row.get('storage_notes', '').strip() or None,
                storage_locations=[loc.strip() for loc in row.get('storage_locations', '').split('|') if loc.strip()],
                storage_attachments=[att.strip() for att in row.get('storage_attachments', '').split(',') if att.strip()],
            )
            
            if not product.name:
                errors.append(f"Row {row_num}: Product name is required")
                continue
            
            db.add(product)
            products_created += 1
            
        except Exception as e:
            errors.append(f"Row {row_num}: {str(e)}")
    
    if products_created > 0:
        await db.commit()
    
    logger.info(
        "Bulk products upload",
        project_id=str(project_id),
        created=products_created,
        errors=len(errors)
    )
    
    return {
        "message": f"Successfully uploaded {products_created} products",
        "created": products_created,
        "errors": errors if errors else None
    }


@router.get("/{project_id}/{product_id}")
async def get_product(
    project_id: UUID,
    product_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get a single product by ID."""
    await verify_project_access(project_id, user_id, db)
    
    result = await db.execute(
        select(Product)
        .where(Product.id == product_id)
        .where(Product.project_id == project_id)
    )
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return {
        "id": str(product.id),
        "name": product.name,
        "description": product.description,
        "sku": product.sku,
        "price": product.price,
        "currency": product.currency,
        "stock_quantity": product.stock_quantity,
        "in_stock": product.in_stock,
        "images": sign_product_images(product.images),
        "category": product.category,
        "tags": product.tags,
        "specifications": product.specifications,
        "faq": product.faq,
        "keywords": product.keywords,
        "storage_locations": product.storage_locations,
        "reorder_point": product.reorder_point,
        "safety_stock": product.safety_stock,
        "storage_notes": product.storage_notes,
        "storage_attachments": product.storage_attachments,
        "is_active": product.is_active,
        "created_at": product.created_at.isoformat() if product.created_at else None,
        "updated_at": product.updated_at.isoformat() if product.updated_at else None,
    }


@router.put("/{project_id}/{product_id}")
async def update_product(
    project_id: UUID,
    product_id: UUID,
    product_update: ProductUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Update a product."""
    await verify_project_access(project_id, user_id, db)
    
    result = await db.execute(
        select(Product)
        .where(Product.id == product_id)
        .where(Product.project_id == project_id)
    )
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Update fields
    update_data = product_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    await db.commit()
    await db.refresh(product)
    
    logger.info("Product updated", product_id=str(product_id))
    
    return {"message": "Product updated successfully"}


@router.delete("/{project_id}/{product_id}")
async def delete_product(
    project_id: UUID,
    product_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Delete a product."""
    await verify_project_access(project_id, user_id, db)
    
    result = await db.execute(
        select(Product)
        .where(Product.id == product_id)
        .where(Product.project_id == project_id)
    )
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    await db.delete(product)
    await db.commit()
    
    logger.info("Product deleted", product_id=str(product_id))
    
    return {"message": "Product deleted successfully"}


@router.get("/{project_id}")
async def list_products(
    project_id: UUID,
    skip: int = 0,
    limit: int = 100,
    category: str | None = None,
    active_only: bool = True,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """List all products for a project."""
    await verify_project_access(project_id, user_id, db)
    
    query = select(Product).where(Product.project_id == project_id)
    
    if active_only:
        query = query.where(Product.is_active == True)
    
    if category:
        query = query.where(Product.category == category)
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    products = result.scalars().all()
    
    return {
        "products": [
            {
                "id": str(p.id),
                "name": p.name,
                "description": p.description,
                "sku": p.sku,
                "price": p.price,
                "currency": p.currency,
                "stock_quantity": p.stock_quantity,
                "in_stock": p.in_stock,
                "images": sign_product_images(p.images),
                "category": p.category,
                "tags": p.tags,
                "specifications": p.specifications,
                "faq": p.faq,
                "keywords": p.keywords,
                "storage_locations": p.storage_locations,
                "reorder_point": p.reorder_point,
                "safety_stock": p.safety_stock,
                "storage_notes": p.storage_notes,
                "storage_attachments": p.storage_attachments,
                "is_active": p.is_active,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "updated_at": p.updated_at.isoformat() if p.updated_at else None,
            }
            for p in products
        ],
        "total": len(products)
    }


@router.post("/{project_id}")
async def create_product(
    project_id: UUID,
    product: ProductCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Create a new product."""
    await verify_project_access(project_id, user_id, db)
    
    new_product = Product(
        project_id=project_id,
        name=product.name,
        description=product.description,
        sku=product.sku,
        price=product.price,
        currency=product.currency,
        stock_quantity=product.stock_quantity,
        in_stock=product.in_stock,
        images=product.images,
        category=product.category,
        tags=product.tags,
        specifications=product.specifications,
        faq=product.faq,
        keywords=product.keywords,
        storage_locations=product.storage_locations,
        reorder_point=product.reorder_point,
        safety_stock=product.safety_stock,
        storage_notes=product.storage_notes,
        storage_attachments=product.storage_attachments,
    )
    
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    
    logger.info("Product created", product_id=str(new_product.id), project_id=str(project_id))
    
    return {
        "id": str(new_product.id),
        "name": new_product.name,
        "message": "Product created successfully"
    }


# ============================================================================
# Image Management Endpoints
# ============================================================================

@router.post("/{project_id}/{product_id}/images", status_code=status.HTTP_201_CREATED)
async def upload_product_image(
    project_id: UUID,
    product_id: UUID,
    file: UploadFile = File(...),
    description: str = "",
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Upload an image for a product.
    """
    # Verify project access
    result = await db.execute(
        select(Project).where(Project.id == project_id).where(Project.owner_id == UUID(user_id))
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or access denied"
        )
    
    # Get product
    result = await db.execute(
        select(Product).where(Product.id == product_id).where(Product.project_id == project_id)
    )
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Upload image
    try:
        upload_result = await FileStorageService.upload_image(
            file=file,
            project_id=str(project_id),
            product_id=str(product_id)
        )
        
        # Add image to product
        if not product.images:
            product.images = []
        
        # Get next order number
        next_order = len(product.images) + 1
        
        image_data = {
            "url": upload_result["url"],
            "filename": upload_result["filename"],
            "description": description or "",
            "order": next_order,
            "size": upload_result["size"]
        }
        
        product.images.append(image_data)
        await db.commit()
        await db.refresh(product)
        
        logger.info(
            "Product image uploaded",
            product_id=str(product_id),
            filename=upload_result["filename"]
        )
        
        # Sign the URL for the response
        response_image = image_data.copy()
        response_image["url"] = FileStorageService.generate_presigned_url(response_image["url"])
        
        return {
            "success": True,
            "image": response_image,
            "message": "Image uploaded successfully"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Failed to upload image", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload image"
        )


@router.delete("/{project_id}/{product_id}/images/{image_index}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_image(
    project_id: UUID,
    product_id: UUID,
    image_index: int,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Delete a product image by index.
    """
    # Verify project access
    result = await db.execute(
        select(Project).where(Project.id == project_id).where(Project.owner_id == UUID(user_id))
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or access denied"
        )
    
    # Get product
    result = await db.execute(
        select(Product).where(Product.id == product_id).where(Product.project_id == project_id)
    )
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if image exists
    if not product.images or image_index >= len(product.images):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    # Delete file
    image = product.images[image_index]
    await FileStorageService.delete_image(image.get("url", ""))
    
    # Remove from product
    product.images.pop(image_index)
    
    # Reorder remaining images
    for idx, img in enumerate(product.images):
        img["order"] = idx + 1
    
    await db.commit()
    
    logger.info(
        "Product image deleted",
        product_id=str(product_id),
        image_index=image_index
    )
    
    return None


@router.patch("/{project_id}/{product_id}/images/{image_index}")
async def update_product_image(
    project_id: UUID,
    product_id: UUID,
    image_index: int,
    description: str = "",
    order: Optional[int] = None,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Update image description or order.
    """
    # Verify project access
    result = await db.execute(
        select(Project).where(Project.id == project_id).where(Project.owner_id == UUID(user_id))
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or access denied"
        )
    
    # Get product
    result = await db.execute(
        select(Product).where(Product.id == product_id).where(Product.project_id == project_id)
    )
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if image exists
    if not product.images or image_index >= len(product.images):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    # Update description
    if description:
        product.images[image_index]["description"] = description
    
    # Update order
    if order is not None and 0 < order <= len(product.images):
        # Reorder images
        image = product.images.pop(image_index)
        product.images.insert(order - 1, image)
        
        # Update order numbers
        for idx, img in enumerate(product.images):
            img["order"] = idx + 1
    
    await db.commit()
    await db.refresh(product)
    
    logger.info(
        "Product image updated",
        product_id=str(product_id),
        image_index=image_index
    )
    
    return {
        "success": True,
        "images": sign_product_images(product.images),
        "message": "Image updated successfully"
    }
