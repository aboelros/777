"""
File storage service for product images.
Supports local storage and Cloudflare R2 (S3 compatible).
"""

import os
import uuid
from typing import Optional
from pathlib import Path
import shutil
import structlog
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text, select
from app.core.config import settings

logger = structlog.get_logger(__name__)

# Storage configuration
# Storage configuration
# Use /tmp for uploads to ensure write permissions in read-only containers
import tempfile
UPLOAD_DIR = Path(tempfile.gettempdir()) / "ai_commander_uploads"
# UPLOAD_DIR.mkdir(parents=True, exist_ok=True) - Moved to lazy creation to avoid permission errors

# Allowed image types
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    logger.warning("boto3 not installed, S3/R2 storage disabled")


from app.services.s3_storage_provider import S3StorageService
from app.services.postgres_storage_provider import PostgresStorageService

class FileStorageService:
    """
    File storage service that supports both local and S3 compatible storage.
    """
    
    @staticmethod
    def _get_storage_provider():
        """Get the configured storage provider."""
        # Priority 1: Postgres Storage (Requested by user)
        if settings.IMAGE_STORAGE_DATABASE_URL:
            try:
                return PostgresStorageService()
            except Exception as e:
                logger.error("Failed to initialize Postgres storage, falling back", error=str(e))
        
        # Priority 2: S3/R2 Storage
        if settings.S3_BUCKET_NAME and settings.S3_ENDPOINT_URL and BOTO3_AVAILABLE:
            try:
                return S3StorageService()
            except Exception as e:
                logger.error("Failed to initialize S3 service, falling back to local", error=str(e))
                return None
        return None
    
    @staticmethod
    def generate_presigned_url(url: str, expiration: int = 900) -> str:
        """
        Generate a presigned URL if the storage is S3 and the URL is a key.
        If local, returns the URL as is (assuming it's served statically).
        """
        if url.startswith("/uploads/"):
            return url
            
        s3_service = FileStorageService._get_storage_provider()
        if isinstance(s3_service, S3StorageService):
            # Existing S3 logic
            key = url
            if settings.S3_PUBLIC_DOMAIN and settings.S3_PUBLIC_DOMAIN in key:
                key = key.replace(f"{settings.S3_PUBLIC_DOMAIN}/", "")
            elif settings.S3_ENDPOINT_URL:
                 endpoint_domain = settings.S3_ENDPOINT_URL.split("://")[-1]
                 if endpoint_domain in key:
                     if key.startswith("http"):
                         parts = key.split('/')
                         if "products" in parts:
                             idx = parts.index("products")
                             key = "/".join(parts[idx:])
            
            return s3_service.generate_presigned_url(key, expiration)

        # Priority 3: Postgres Storage
        if isinstance(s3_service, PostgresStorageService):
             return f"/api/{settings.API_VERSION}/storage/images/{url}"
            
        return url

    @staticmethod
    async def upload_image(
        file: UploadFile,
        project_id: str,
        product_id: str
    ) -> dict:
        """
        Upload an image file.
        """
        try:
            # Validate file extension
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in ALLOWED_EXTENSIONS:
                raise ValueError(f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")
            
            # Generate unique filename/key
            unique_id = str(uuid.uuid4())
            filename = f"{product_id}_{unique_id}{file_ext}"
            
            # Check for S3 storage
            s3_service = FileStorageService._get_storage_provider()
            
            if s3_service:
                logger.info("📦 Using S3 storage for upload")
            else:
                logger.info("💾 Using local storage for upload (S3 not configured or unavailable)")
            
            if s3_service:
                # Upload to S3
                logger.info(
                    "📤 Attempting S3 upload",
                    project_id=project_id,
                    product_id=product_id,
                    filename=filename,
                    content_type=file.content_type
                )
                
                key = f"products/{project_id}/{filename}"
                
                try:
                    # Return the key, not the full URL
                    stored_key = await s3_service.upload_image(file, key, file.content_type, project_id)
                    
                    # Get file size (approximate from read)
                    file.file.seek(0, 2)
                    file_size = file.file.tell()
                    file.file.seek(0)
                    
                    logger.info(
                        "✅ Image uploaded to S3 successfully",
                        key=stored_key,
                        size=file_size,
                        project_id=project_id
                    )
                    
                    return {
                        "url": stored_key, # Storing the key
                        "filename": filename,
                        "size": file_size,
                        "storage": "s3"
                    }
                except Exception as s3_error:
                    logger.error(
                        "❌ S3 upload failed, falling back to local storage",
                        error=str(s3_error),
                        error_type=type(s3_error).__name__,
                        key=key
                    )
                    # Fall through to local storage
                    s3_service = None
            
            if not s3_service:
                # Local Storage
                # Create project directory
                project_dir = UPLOAD_DIR / project_id
                project_dir.mkdir(parents=True, exist_ok=True)
                
                file_path = project_dir / filename
                
                # Save file
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                
                # Get file size
                file_size = os.path.getsize(file_path)
                
                # Check file size
                if file_size > MAX_FILE_SIZE:
                    os.remove(file_path)
                    raise ValueError(f"File too large. Max size: {MAX_FILE_SIZE / 1024 / 1024}MB")
                
                # Generate URL (relative path)
                url = f"/uploads/products/{project_id}/{filename}"
                
                logger.info(
                    "Image uploaded locally",
                    filename=filename,
                    size=file_size,
                    project_id=project_id
                )
                
                return {
                    "url": url,
                    "filename": filename,
                    "size": file_size,
                    "storage": "local"
                }
            
        except Exception as e:
            logger.error("Failed to upload image", error=str(e))
            raise
    
    @staticmethod
    async def delete_image(url: str, project_id: str = None) -> bool:
        """
        Delete an image file.
        """
        try:
            s3_service = FileStorageService._get_storage_provider()
            
            # Check if URL is S3 or Local
            if s3_service and not url.startswith("/uploads/"):
                # Assume it's a key if it's not a local path
                # Also handle legacy full URLs if possible
                key = url
                if settings.S3_PUBLIC_DOMAIN and settings.S3_PUBLIC_DOMAIN in url:
                    key = url.replace(f"{settings.S3_PUBLIC_DOMAIN}/", "")
                elif settings.S3_ENDPOINT_URL and settings.S3_ENDPOINT_URL in url:
                     # Fallback extraction
                    parts = url.split('/')
                    if "products" in parts:
                        idx = parts.index("products")
                        key = "/".join(parts[idx:])
                
                return await s3_service.delete_image(key, project_id)
            
            elif url.startswith("/uploads/"):
                # Local storage
                file_path = Path(url[1:])  # Remove leading /
                
                if file_path.exists():
                    os.remove(file_path)
                    logger.info("Image deleted locally", url=url)
                    return True
            
            return False
            
        except Exception as e:
            logger.error("Failed to delete image", error=str(e), url=url)
            return False
