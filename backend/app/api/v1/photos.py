"""
Photo upload endpoint for about section.
Stores photos with sequential names (1.jpg, 2.jpg, 3.jpg, 4.jpg) in a static folder.
Photos are shared across all projects (not per-project).
"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog
import os
from pathlib import Path

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.domains.projects.models import Project

router = APIRouter()
logger = structlog.get_logger(__name__)

# Static directory for about photos (committed to GitHub)
# Using backend/static/about folder which is part of the repository
STATIC_DIR = Path(__file__).parent.parent.parent / "static" / "about"
try:
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
except (PermissionError, OSError):
    # If we can't create the directory (e.g., in production), use it anyway
    # It should already exist from the repository
    pass

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_PHOTOS = 4


@router.post("/{project_id}/about/photos")
async def upload_about_photos(
    project_id: UUID,
    photos: List[UploadFile] = File(...),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload photos for about section.
    Photos are stored in static/about/ with sequential names: 1.jpg, 2.jpg, 3.jpg, 4.jpg
    These photos are shared across all projects (not per-project).
    Maximum 4 photos allowed.
    """
    # Verify project access
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
    
    # Validate number of photos
    if len(photos) > MAX_PHOTOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum {MAX_PHOTOS} photos allowed"
        )
    
    # Clear existing photos in static folder
    for existing_file in STATIC_DIR.glob("*"):
        if existing_file.is_file():
            existing_file.unlink()
    
    uploaded_files = []
    
    try:
        for index, photo in enumerate(photos, start=1):
            # Validate file extension
            file_ext = Path(photo.filename).suffix.lower()
            if file_ext not in ALLOWED_EXTENSIONS:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File {photo.filename} has invalid extension. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
                )
            
            # Read file content
            content = await photo.read()
            
            # Validate file size
            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File {photo.filename} exceeds maximum size of 5MB"
                )
            
            # Save with sequential name in static folder
            filename = f"{index}{file_ext}"
            file_path = STATIC_DIR / filename
            
            with open(file_path, "wb") as f:
                f.write(content)
            
            uploaded_files.append({
                "index": index,
                "filename": filename,
                "path": f"static/about/{filename}",
                "url": f"/static/about/{filename}"
            })
            
            logger.info(
                "About photo uploaded to static folder",
                filename=filename,
                size=len(content)
            )
        
        return {
            "success": True,
            "photos": uploaded_files,
            "count": len(uploaded_files),
            "message": "Photos uploaded to static folder (shared across all projects)"
        }
        
    except HTTPException:
        # Clean up on validation error
        for file_info in uploaded_files:
            file_path = STATIC_DIR / file_info["filename"]
            if file_path.exists():
                file_path.unlink()
        raise
    except Exception as e:
        # Clean up on unexpected error
        for file_info in uploaded_files:
            file_path = STATIC_DIR / file_info["filename"]
            if file_path.exists():
                file_path.unlink()
        logger.error("Failed to upload about photos", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload photos: {str(e)}"
        )


@router.get("/{project_id}/about/photos")
async def get_about_photos(
    project_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get list of about photos from static folder."""
    # Verify project access
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
    
    # Get photos from static folder
    photos = []
    for i in range(1, MAX_PHOTOS + 1):
        for ext in [".jpg", ".jpeg", ".png", ".webp"]:
            file_path = STATIC_DIR / f"{i}{ext}"
            if file_path.exists():
                photos.append({
                    "index": i,
                    "filename": f"{i}{ext}",
                    "url": f"/static/about/{i}{ext}"
                })
                break
    
    return {
        "photos": photos,
        "count": len(photos),
        "message": "Photos from static folder (shared across all projects)"
    }


@router.delete("/{project_id}/about/photos")
async def delete_about_photos(
    project_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Delete all about photos from static folder."""
    # Verify project access
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
    
    # Delete physical files from static folder
    deleted_count = 0
    for file_path in STATIC_DIR.glob("*"):
        if file_path.is_file():
            file_path.unlink()
            deleted_count += 1
    
    logger.info("About photos deleted from static folder", count=deleted_count)
    
    return {
        "success": True,
        "message": f"Deleted {deleted_count} photos from static folder",
        "count": deleted_count
    }

