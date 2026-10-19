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


class PostgresStorageService:
    """
    Storage service that stores images as binary data in a dedicated PostgreSQL database.
    """
    
    def __init__(self):
        from app.core.image_storage_guard import resolve_image_storage_database_url
        from app.core.db_identity import normalize_db_identity

        self.db_url = resolve_image_storage_database_url()
        if not self.db_url:
            raise ValueError("IMAGE_STORAGE_DATABASE_URL not configured")

        # Create a dedicated engine for image storage
        # Supabase/pgbouncer compatibility: Disable prepared statement caching
        self.engine = create_async_engine(
            self.db_url,
            connect_args={"statement_cache_size": 0}
        )
        norm_id = normalize_db_identity(self.db_url, "IMAGE_STORAGE_DATABASE_URL")
        logger.info("Initialized PostgresStorageService", db_host=f"{norm_id.host}:{norm_id.port}/{norm_id.database}")

    async def upload_image(self, file: UploadFile, key: str, content_type: str, project_id: str = None) -> str:
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
                        INSERT INTO public.product_images (key, project_id, data, content_type, size)
                        VALUES (:key, :project_id, :data, :content_type, :size)
                        ON CONFLICT (key) DO UPDATE 
                        SET data = EXCLUDED.data,
                            project_id = EXCLUDED.project_id,
                            content_type = EXCLUDED.content_type, 
                            size = EXCLUDED.size,
                            created_at = CURRENT_TIMESTAMP
                    """),
                    {
                        "key": key,
                        "project_id": project_id,
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
                                project_id UUID,
                                data BYTEA NOT NULL,
                                content_type VARCHAR(100) NOT NULL,
                                size INTEGER NOT NULL,
                                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                                updated_at TIMESTAMPTZ,
                                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
                            );
                        """))
                    logger.info("✅ Table 'product_images' created successfully. Retrying upload...")
                    
                    # Retry upload once
                    async with self.engine.begin() as conn:
                        await conn.execute(
                            text("""
                                INSERT INTO public.product_images (key, project_id, data, content_type, size)
                                VALUES (:key, :project_id, :data, :content_type, :size)
                                ON CONFLICT (key) DO UPDATE 
                                SET data = EXCLUDED.data, project_id = EXCLUDED.project_id, content_type = EXCLUDED.content_type, 
                                    size = EXCLUDED.size,
                                    updated_at = CURRENT_TIMESTAMP
                            """),
                            {
                                "key": key, "project_id": project_id, "data": file_content,
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

    async def get_image(self, key: str, project_id: str = None) -> Optional[dict]:
        """Retrieve image from Postgres."""
        try:
            async with self.engine.connect() as conn:
                result = await conn.execute(
                    text("SELECT data, content_type FROM public.product_images WHERE key = :key AND (:project_id IS NULL OR project_id = :project_id::uuid)"),
                    {"key": key, "project_id": project_id}
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

    async def delete_image(self, key: str, project_id: str = None) -> bool:
        """Delete image from Postgres."""
        try:
            async with self.engine.begin() as conn:
                await conn.execute(
                    text("DELETE FROM public.product_images WHERE key = :key AND (:project_id IS NULL OR project_id = :project_id::uuid)"),
                    {"key": key, "project_id": project_id}
                )
            return True
        except Exception as e:
            logger.error("❌ Postgres delete failed", error=str(e), key=key)
            return False


