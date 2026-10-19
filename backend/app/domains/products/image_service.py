from typing import List, Optional, Any
from uuid import UUID
from app.core.context import TenantContext
from fastapi import HTTPException, status, UploadFile
import structlog
from app.core.uow import UnitOfWork
from app.domains.products.repository import ProductRepository
from app.domains.products.models import Product
from app.services.file_storage import FileStorageService

logger = structlog.get_logger(__name__)

def sign_product_images(images: List[dict] | None) -> List[dict]:
    if not images:
        return []
    
    signed_images = []
    for img in images:
        img_copy = img.copy() if isinstance(img, dict) else img
        if isinstance(img_copy, dict) and "url" in img_copy:
            img_copy["url"] = FileStorageService.generate_presigned_url(img_copy["url"])
        signed_images.append(img_copy)
    return signed_images


class ProductImageService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def upload_product_image(self, tenant: TenantContext, product_id: str, file: UploadFile, description: str) -> dict:
        async with self.uow as uow:
            proj_uuid = tenant.project_id
            prod_uuid = UUID(product_id)
            
            
            product_repo = ProductRepository(uow.session)
            product = await product_repo.get_tenant_product(proj_uuid, prod_uuid)
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
                
            try:
                upload_result = await FileStorageService.upload_image(
                    file=file, project_id=str(tenant.project_id), product_id=product_id
                )
                
                if not product.images:
                    product.images = []
                    
                next_order = len(product.images) + 1
                image_data = {
                    "url": upload_result["url"],
                    "filename": upload_result["filename"],
                    "description": description or "",
                    "order": next_order,
                    "size": upload_result["size"]
                }
                
                # SQLAlchemy JSON mutations workaround
                images = product.images.copy()
                images.append(image_data)
                product.images = images
                
                await uow.commit()
                
                response_image = image_data.copy()
                response_image["url"] = FileStorageService.generate_presigned_url(response_image["url"])
                
                return {
                    "success": True,
                    "image": response_image,
                    "message": "Image uploaded successfully"
                }
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
                
    async def delete_product_image(self, tenant: TenantContext, product_id: str, image_index: int) -> None:
        async with self.uow as uow:
            proj_uuid = tenant.project_id
            prod_uuid = UUID(product_id)
            
            
            product_repo = ProductRepository(uow.session)
            product = await product_repo.get_tenant_product(proj_uuid, prod_uuid)
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
                
            if not product.images or image_index >= len(product.images):
                raise HTTPException(status_code=404, detail="Image not found")
                
            image = product.images[image_index]
            await FileStorageService.delete_image(image.get("url", ""))
            
            images = product.images.copy()
            images.pop(image_index)
            for idx, img in enumerate(images):
                img["order"] = idx + 1
            product.images = images
            
            await uow.commit()

    async def update_product_image(self, tenant: TenantContext, product_id: str, image_index: int, description: str, order: int) -> dict:
        async with self.uow as uow:
            proj_uuid = tenant.project_id
            prod_uuid = UUID(product_id)
            
            
            product_repo = ProductRepository(uow.session)
            product = await product_repo.get_tenant_product(proj_uuid, prod_uuid)
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
                
            if not product.images or image_index >= len(product.images):
                raise HTTPException(status_code=404, detail="Image not found")
                
            images = product.images.copy()
            if description is not None:
                images[image_index]["description"] = description
                
            if order is not None and order != images[image_index].get("order"):
                img = images.pop(image_index)
                target_idx = max(0, min(order - 1, len(images)))
                images.insert(target_idx, img)
                for idx, im in enumerate(images):
                    im["order"] = idx + 1
                    
            product.images = images
            await uow.commit()
            return {"message": "Image updated successfully"}
