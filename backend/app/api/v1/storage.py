from fastapi import APIRouter, HTTPException, Depends, Response
import structlog
from app.services.file_storage import FileStorageService, PostgresStorageService
from app.core.config import settings

router = APIRouter()
logger = structlog.get_logger(__name__)

@router.get("/images/{key:path}")
async def get_storage_image(key: str):
    """
    Fetch image from storage (Postgres or S3) and serve it.
    This endpoint handles the retrieval of binary data stored in the database.
    """
    provider = FileStorageService._get_storage_provider()
    
    if isinstance(provider, PostgresStorageService):
        image = await provider.get_image(key)
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")
        
        return Response(
            content=image["data"],
            media_type=image["content_type"],
            headers={"Cache-Control": "public, max-age=31536000"}  # Cache for 1 year
        )
    
    # Fallback/Default behavior if not using Postgres
    raise HTTPException(status_code=404, detail="Image retrieval not supported through this endpoint for current provider")
