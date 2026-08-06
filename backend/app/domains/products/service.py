from typing import List, Optional, Any
from uuid import UUID
from fastapi import HTTPException, status, UploadFile
import structlog
import csv
import io

from app.core.uow import UnitOfWork
from app.domains.products.repository import ProductRepository
from app.domains.products.models import Product
from app.domains.products.schemas import ProductCreate, ProductUpdate
from app.domains.projects.repository import ProjectRepository
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

class ProductService:
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

    async def create_product(self, project_id: str, user_id: str, product_data: ProductCreate) -> dict:
        async with self.uow as uow:
            proj_uuid = UUID(project_id)
            user_uuid = UUID(user_id)
            await self._verify_project_access(proj_uuid, user_uuid)
            
            product_repo = ProductRepository(uow.session)
            
            new_product = Product(
                project_id=proj_uuid,
                name=product_data.name,
                description=product_data.description,
                sku=product_data.sku,
                price=product_data.price,
                currency=product_data.currency,
                stock_quantity=product_data.stock_quantity,
                in_stock=product_data.in_stock,
                images=product_data.images,
                category=product_data.category,
                tags=product_data.tags,
                specifications=product_data.specifications,
                faq=product_data.faq,
                keywords=product_data.keywords,
                storage_locations=product_data.storage_locations,
                reorder_point=product_data.reorder_point,
                safety_stock=product_data.safety_stock,
                storage_notes=product_data.storage_notes,
                storage_attachments=product_data.storage_attachments,
            )
            
            product_repo.add(new_product)
            await uow.commit()
            
            logger.info("Product created", product_id=str(new_product.id), project_id=project_id)
            
            return {
                "id": str(new_product.id),
                "name": new_product.name,
                "message": "Product created successfully"
            }

    async def list_products(
        self, project_id: str, user_id: str, skip: int, limit: int,
        category: Optional[str], active_only: bool
    ) -> dict:
        async with self.uow as uow:
            proj_uuid = UUID(project_id)
            user_uuid = UUID(user_id)
            await self._verify_project_access(proj_uuid, user_uuid)
            
            product_repo = ProductRepository(uow.session)
            # Use raw query for active_only toggle since the repo method enforces active_only=True
            from sqlalchemy import select
            
            query = select(Product).where(Product.project_id == proj_uuid)
            if active_only:
                query = query.where(Product.is_active == True)
            if category:
                query = query.where(Product.category == category)
                
            query = query.offset(skip).limit(limit)
            result = await uow.session.execute(query)
            products = result.scalars().all()
            
            # Format results
            product_list = []
            for p in products:
                p_dict = {
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
                product_list.append(p_dict)
                
            return {
                "products": product_list,
                "total": len(products)
            }

    async def get_product(self, project_id: str, product_id: str, user_id: str) -> dict:
        async with self.uow as uow:
            proj_uuid = UUID(project_id)
            prod_uuid = UUID(product_id)
            user_uuid = UUID(user_id)
            await self._verify_project_access(proj_uuid, user_uuid)
            
            product_repo = ProductRepository(uow.session)
            product = await product_repo.get(prod_uuid)
            if not product or product.project_id != proj_uuid:
                raise HTTPException(status_code=404, detail="Product not found")
                
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

    async def update_product(self, project_id: str, product_id: str, user_id: str, update_data: ProductUpdate) -> dict:
        async with self.uow as uow:
            proj_uuid = UUID(project_id)
            prod_uuid = UUID(product_id)
            user_uuid = UUID(user_id)
            await self._verify_project_access(proj_uuid, user_uuid)
            
            product_repo = ProductRepository(uow.session)
            product = await product_repo.get(prod_uuid)
            if not product or product.project_id != proj_uuid:
                raise HTTPException(status_code=404, detail="Product not found")
                
            update_dict = update_data.dict(exclude_unset=True)
            for field, value in update_dict.items():
                setattr(product, field, value)
                
            await uow.commit()
            return {"message": "Product updated successfully"}

    async def delete_product(self, project_id: str, product_id: str, user_id: str) -> dict:
        async with self.uow as uow:
            proj_uuid = UUID(project_id)
            prod_uuid = UUID(product_id)
            user_uuid = UUID(user_id)
            await self._verify_project_access(proj_uuid, user_uuid)
            
            product_repo = ProductRepository(uow.session)
            product = await product_repo.get(prod_uuid)
            if not product or product.project_id != proj_uuid:
                raise HTTPException(status_code=404, detail="Product not found")
                
            await product_repo.delete(product)
            await uow.commit()
            return {"message": "Product deleted successfully"}

    async def bulk_upload_products(self, project_id: str, user_id: str, file: UploadFile) -> dict:
        async with self.uow as uow:
            proj_uuid = UUID(project_id)
            user_uuid = UUID(user_id)
            await self._verify_project_access(proj_uuid, user_uuid)
            
            if not file.filename.endswith('.csv'):
                raise HTTPException(status_code=400, detail="File must be a CSV")
                
            contents = await file.read()
            csv_data = contents.decode('utf-8')
            csv_file = io.StringIO(csv_data)
            csv_reader = csv.DictReader(csv_file)
            
            product_repo = ProductRepository(uow.session)
            products_created = 0
            errors = []
            
            for row_num, row in enumerate(csv_reader, start=2):
                try:
                    product = Product(
                        project_id=proj_uuid,
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
                        
                    product_repo.add(product)
                    products_created += 1
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
                    
            if products_created > 0:
                await uow.commit()
                
            return {
                "message": f"Successfully uploaded {products_created} products",
                "created": products_created,
                "errors": errors if errors else None
            }

    async def upload_product_image(self, project_id: str, product_id: str, user_id: str, file: UploadFile, description: str) -> dict:
        async with self.uow as uow:
            proj_uuid = UUID(project_id)
            prod_uuid = UUID(product_id)
            user_uuid = UUID(user_id)
            await self._verify_project_access(proj_uuid, user_uuid)
            
            product_repo = ProductRepository(uow.session)
            product = await product_repo.get(prod_uuid)
            if not product or product.project_id != proj_uuid:
                raise HTTPException(status_code=404, detail="Product not found")
                
            try:
                upload_result = await FileStorageService.upload_image(
                    file=file, project_id=project_id, product_id=product_id
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
                
    async def delete_product_image(self, project_id: str, product_id: str, image_index: int, user_id: str) -> None:
        async with self.uow as uow:
            proj_uuid = UUID(project_id)
            prod_uuid = UUID(product_id)
            user_uuid = UUID(user_id)
            await self._verify_project_access(proj_uuid, user_uuid)
            
            product_repo = ProductRepository(uow.session)
            product = await product_repo.get(prod_uuid)
            if not product or product.project_id != proj_uuid:
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

    async def update_product_image(self, project_id: str, product_id: str, image_index: int, description: str, order: int, user_id: str) -> dict:
        async with self.uow as uow:
            proj_uuid = UUID(project_id)
            prod_uuid = UUID(product_id)
            user_uuid = UUID(user_id)
            await self._verify_project_access(proj_uuid, user_uuid)
            
            product_repo = ProductRepository(uow.session)
            product = await product_repo.get(prod_uuid)
            if not product or product.project_id != proj_uuid:
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
