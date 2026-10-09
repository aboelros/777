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
    
    async def upload_image(self, file: UploadFile, key: str, content_type: str, project_id: str = None) -> str:
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

    async def delete_image(self, key: str, project_id: str = None) -> bool:
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


