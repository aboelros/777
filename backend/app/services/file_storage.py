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


class S3StorageService:
    """
    Generic S3 compatible storage service (Cloudflare R2, Backblaze B2, AWS S3, etc).
    """
    
    def __init__(self):
        if not BOTO3_AVAILABLE:
            raise ImportError("boto3 is required for S3 storage")
            
        self.bucket_name = settings.S3_BUCKET_NAME
        self.public_domain = settings.S3_PUBLIC_DOMAIN
        
        if not self.bucket_name:
            raise ValueError("S3_BUCKET_NAME not configured")
            
        self.s3_client = boto3.client(
            's3',
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION or 'auto'
        )
    
    async def upload_image(self, file: UploadFile, key: str, content_type: str) -> str:
        """Upload image to S3 and return the key."""
        try:
            logger.info(
                "🚀 Starting S3 upload",
                key=key,
                content_type=content_type,
                bucket=self.bucket_name,
                endpoint=settings.S3_ENDPOINT_URL
            )
            
            # Read file content
            file_content = await file.read()
            logger.info(f"📦 File read: {len(file_content)} bytes")
            
            # Reset file pointer for subsequent reads if any
            await file.seek(0)
            
            # Upload to S3
            logger.info("📤 Uploading to S3...")
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=file_content,
                ContentType=content_type,
                # ACL='private' # Explicitly private
            )
            
            logger.info(
                "✅ S3 upload successful",
                key=key,
                size=len(file_content)
            )
            
            return key
            
        except ClientError as e:
            logger.error(
                "❌ S3 upload failed - ClientError",
                error=str(e),
                error_code=e.response.get('Error', {}).get('Code') if hasattr(e, 'response') else None,
                error_message=e.response.get('Error', {}).get('Message') if hasattr(e, 'response') else None,
                key=key,
                bucket=self.bucket_name
            )
            raise e
        except Exception as e:
            logger.error(
                "❌ S3 upload failed - Unexpected",
                error=str(e),
                error_type=type(e).__name__,
                key=key
            )
            raise e

    def generate_presigned_url(self, key: str, expiration: int = 900) -> str:
        """Generate a presigned URL for a file."""
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': key
                },
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            logger.error("Failed to generate presigned URL", error=str(e))
            return ""

    async def delete_image(self, key: str) -> bool:
        """Delete image from S3."""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )
            return True
        except ClientError as e:
            logger.error("S3 delete failed", error=str(e))
            return False


class PostgresStorageService:
    """
    Storage service that stores images as binary data in a dedicated PostgreSQL database.
    """
    
    def __init__(self):
        self.db_url = settings.IMAGE_STORAGE_DATABASE_URL
        if not self.db_url:
            raise ValueError("IMAGE_STORAGE_DATABASE_URL not configured")
        
        # Create a dedicated engine for image storage
        # Supabase/pgbouncer compatibility: Disable prepared statement caching
        self.engine = create_async_engine(
            self.db_url,
            connect_args={"statement_cache_size": 0}
        )
        display_host = self.db_url.split("@")[-1].split("/")[0] if "@" in self.db_url else "unknown"
        print(f"LOUD_DEBUG: Initialized PostgresStorageService connecting to: {display_host}")
        logger.info("🐘 Initialized PostgresStorageService", db_host=display_host)

    async def upload_image(self, file: UploadFile, key: str, content_type: str) -> str:
        """Upload image to Postgres and return the key."""
        try:
            # Read file content
            file_content = await file.read()
            size = len(file_content)
            
            # Reset file pointer
            await file.seek(0)
            
            async with self.engine.begin() as conn:
                await conn.execute(
                    text("""
                        INSERT INTO public.product_images (key, data, content_type, size)
                        VALUES (:key, :data, :content_type, :size)
                        ON CONFLICT (key) DO UPDATE 
                        SET data = EXCLUDED.data, 
                            content_type = EXCLUDED.content_type, 
                            size = EXCLUDED.size,
                            created_at = CURRENT_TIMESTAMP
                    """),
                    {
                        "key": key,
                        "data": file_content,
                        "content_type": content_type,
                        "size": size
                    }
                )
            
            logger.info("✅ Image stored in Postgres", key=key, size=size)
            return key
            
        except Exception as e:
            # Check if it's a missing table error
            error_str = str(e).lower()
            if "relation" in error_str and "does not exist" in error_str:
                try:
                    logger.warning("⚠️ Table 'product_images' missing, attempting to create...")
                    async with self.engine.begin() as conn:
                        await conn.execute(text("""
                            CREATE TABLE IF NOT EXISTS public.product_images (
                                key VARCHAR(500) PRIMARY KEY,
                                data BYTEA NOT NULL,
                                content_type VARCHAR(100) NOT NULL,
                                size INTEGER NOT NULL,
                                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                                updated_at TIMESTAMPTZ
                            );
                        """))
                    logger.info("✅ Table 'product_images' created successfully. Retrying upload...")
                    
                    # Retry upload once
                    async with self.engine.begin() as conn:
                        await conn.execute(
                            text("""
                                INSERT INTO public.product_images (key, data, content_type, size)
                                VALUES (:key, :data, :content_type, :size)
                                ON CONFLICT (key) DO UPDATE 
                                SET data = EXCLUDED.data, 
                                    content_type = EXCLUDED.content_type, 
                                    size = EXCLUDED.size,
                                    updated_at = CURRENT_TIMESTAMP
                            """),
                            {
                                "key": key,
                                "data": file_content,
                                "content_type": content_type,
                                "size": size
                            }
                        )
                    logger.info("✅ Image stored in Postgres (after retry)", key=key, size=size)
                    return key
                except Exception as retry_err:
                    logger.error("❌ Postgres upload failed after retry", error=str(retry_err), key=key)
                    # Fallback to local storage would happen if we raised, but we are inside retries.
                    # Actually, we should raise so caller knows it failed.
                    raise retry_err
            
            logger.error("❌ Postgres upload failed", error=str(e), key=key)
            raise e

    async def get_image(self, key: str) -> Optional[dict]:
        """Retrieve image from Postgres."""
        try:
            async with self.engine.connect() as conn:
                result = await conn.execute(
                    text("SELECT data, content_type FROM public.product_images WHERE key = :key"),
                    {"key": key}
                )
                row = result.fetchone()
                if row:
                    return {
                        "data": row[0],
                        "content_type": row[1]
                    }
                return None
        except Exception as e:
            logger.error("❌ Postgres fetch failed", error=str(e), key=key)
            return None

    async def delete_image(self, key: str) -> bool:
        """Delete image from Postgres."""
        try:
            async with self.engine.begin() as conn:
                await conn.execute(
                    text("DELETE FROM public.product_images WHERE key = :key"),
                    {"key": key}
                )
            return True
        except Exception as e:
            logger.error("❌ Postgres delete failed", error=str(e), key=key)
            return False


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
                    stored_key = await s3_service.upload_image(file, key, file.content_type)
                    
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
            
            else:
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
    async def delete_image(url: str) -> bool:
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
                
                return await s3_service.delete_image(key)
            
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
