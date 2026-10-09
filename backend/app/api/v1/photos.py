"""
Photo upload endpoint for about section.
Stores photos with sequential names (1.jpg, 2.jpg, 3.jpg, 4.jpg) in a static folder.
Photos are scoped per-project.
"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
import structlog
import os
from pathlib import Path

from app.api.dependencies.tenant import get_tenant_context, TenantContext
from app.domains.projects.models import ProjectRole

router = APIRouter()
logger = structlog.get_logger(__name__)

STATIC_DIR = Path(__file__).parent.parent.parent / "static" / "about"
try:
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
except (PermissionError, OSError):
    pass

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_PHOTOS = 4

def get_project_dir(project_id: str) -> Path:
    proj_dir = STATIC_DIR / project_id
    proj_dir.mkdir(parents=True, exist_ok=True)
    return proj_dir

@router.post("/{project_id}/about/photos")
async def upload_about_photos(
    project_id: UUID,
    photos: List[UploadFile] = File(...),
    tenant: TenantContext = Depends(get_tenant_context)
):
    if tenant.role not in [ProjectRole.OWNER.value, ProjectRole.MODERATOR.value]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owners and moderators can modify photos")
    
    if len(photos) > MAX_PHOTOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum {MAX_PHOTOS} photos allowed"
        )
    
    proj_dir = get_project_dir(str(tenant.project_id))
    
    # Clear existing photos for THIS project
    for existing_file in proj_dir.glob("*"):
        if existing_file.is_file():
            existing_file.unlink()
    
    uploaded_files = []
    
    try:
        for index, photo in enumerate(photos, start=1):
            file_ext = Path(photo.filename).suffix.lower()
            if file_ext not in ALLOWED_EXTENSIONS:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File {photo.filename} has invalid extension. Allowed: {ALLOWED_EXTENSIONS}"
                )
            
            content = await photo.read()
            
            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File {photo.filename} exceeds maximum size of 5MB"
                )
            
            filename = f"{index}{file_ext}"
            file_path = proj_dir / filename
            
            with open(file_path, "wb") as f:
                f.write(content)
            
            uploaded_files.append({
                "index": index,
                "filename": filename,
                "path": f"static/about/{tenant.project_id}/{filename}",
                "url": f"/static/about/{tenant.project_id}/{filename}"
            })
            
            logger.info("About photo uploaded", filename=filename, project_id=str(tenant.project_id))
        
        return {
            "success": True,
            "photos": uploaded_files,
            "count": len(uploaded_files),
            "message": "Photos uploaded"
        }
        
    except HTTPException:
        for file_info in uploaded_files:
            file_path = proj_dir / file_info["filename"]
            if file_path.exists():
                file_path.unlink()
        raise
    except Exception as e:
        for file_info in uploaded_files:
            file_path = proj_dir / file_info["filename"]
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
    tenant: TenantContext = Depends(get_tenant_context)
):
    proj_dir = get_project_dir(str(tenant.project_id))
    photos = []
    for i in range(1, MAX_PHOTOS + 1):
        for ext in [".jpg", ".jpeg", ".png", ".webp"]:
            file_path = proj_dir / f"{i}{ext}"
            if file_path.exists():
                photos.append({
                    "index": i,
                    "filename": f"{i}{ext}",
                    "url": f"/static/about/{tenant.project_id}/{i}{ext}"
                })
                break
    
    return {
        "photos": photos,
        "count": len(photos),
        "message": "Photos retrieved"
    }

@router.delete("/{project_id}/about/photos")
async def delete_about_photos(
    project_id: UUID,
    tenant: TenantContext = Depends(get_tenant_context)
):
    if tenant.role not in [ProjectRole.OWNER.value, ProjectRole.MODERATOR.value]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owners and moderators can delete photos")
    
    proj_dir = get_project_dir(str(tenant.project_id))
    deleted_count = 0
    for file_path in proj_dir.glob("*"):
        if file_path.is_file():
            file_path.unlink()
            deleted_count += 1
    
    logger.info("About photos deleted", count=deleted_count, project_id=str(tenant.project_id))
    
    return {
        "success": True,
        "message": f"Deleted {deleted_count} photos",
        "count": deleted_count
    }
