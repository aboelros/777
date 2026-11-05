from fastapi import APIRouter, HTTPException, Depends, Response
from uuid import UUID
import structlog
from app.services.file_storage import FileStorageService, PostgresStorageService
from app.core.config import settings
from app.api.dependencies.tenant import get_tenant_context, TenantContext

router = APIRouter()
logger = structlog.get_logger(__name__)

@router.get("/images/products/{project_id}/{key:path}")
async def get_storage_image(
    project_id: UUID,
    key: str,
    tenant: TenantContext = Depends(get_tenant_context)
):
    """
    Fetch image from storage (Postgres or S3) and serve it.
    This endpoint handles the retrieval of binary data stored in the database.
    """
    provider = FileStorageService._get_storage_provider()
    full_key = f"products/{project_id}/{key}"
    
    if isinstance(provider, PostgresStorageService):
        # Enforce tenant ownership by passing project_id
        image = await provider.get_image(full_key, project_id=str(tenant.project_id))
        if not image:
            raise HTTPException(status_code=404, detail="Image not found or access denied")
        
        return Response(
            content=image["data"],
            media_type=image["content_type"],
            headers={"Cache-Control": "private, max-age=3600"}  # Cache private for 1 hour
        )
    
    # Fallback/Default behavior if not using Postgres
    raise HTTPException(status_code=404, detail="Image retrieval not supported through this endpoint for current provider")


@router.get("/images/avatars/{project_id}/{key:path}")
async def get_avatar_image(
    project_id: UUID,
    key: str
) -> Response:
    """
    Fetch avatar image from storage and serve it publicly.
    Accessible by <img> tags directly without authorization headers.
    """
    provider = FileStorageService._get_storage_provider()
    full_key = f"avatars/{project_id}/{key}"
    
    if isinstance(provider, PostgresStorageService):
        image = await provider.get_image(full_key)
        if not image:
            raise HTTPException(status_code=404, detail="Avatar image not found")
        
        return Response(
            content=image["data"],
            media_type=image["content_type"],
            headers={
                "Cache-Control": "public, max-age=86400",
                "Access-Control-Allow-Origin": "*"
            }
        )
    
    raise HTTPException(status_code=404, detail="Image retrieval not supported for current provider")

