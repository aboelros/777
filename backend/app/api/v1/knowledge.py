"""
Knowledge base management endpoints.
"""

from typing import List, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.core.context import TenantContext
from app.api.dependencies.tenant import get_tenant_context
from app.core.uow import UnitOfWork
from app.domains.ai.service import AIService
from app.services.scraper_service import scraper
from app.domains.ai.schemas import KnowledgeBaseCreate, KnowledgeBaseUpdate, KnowledgeBaseResponse

router = APIRouter()
logger = structlog.get_logger(__name__)


async def get_ai_service(db: AsyncSession = Depends(get_db)) -> AIService:
    return AIService(UnitOfWork(db))


@router.get("/{project_id}", response_model=List[KnowledgeBaseResponse])
async def list_knowledge_items(
    project_id: UUID,
    context: TenantContext = Depends(get_tenant_context),
    service: AIService = Depends(get_ai_service)
) -> Any:
    """List all knowledge base items for a specific project."""
    return await service.list_knowledge_items(context)


@router.post("/{project_id}", response_model=KnowledgeBaseResponse, status_code=status.HTTP_201_CREATED)
async def create_knowledge_item(
    project_id: UUID,
    item_data: KnowledgeBaseCreate,
    context: TenantContext = Depends(get_tenant_context),
    service: AIService = Depends(get_ai_service)
) -> Any:
    """Create a new knowledge base item for a project."""
    data = item_data.model_dump()
    return await service.create_knowledge_item(context, data)


@router.patch("/{project_id}/{item_id}", response_model=KnowledgeBaseResponse)
async def update_knowledge_item(
    project_id: UUID,
    item_id: UUID,
    item_data: KnowledgeBaseUpdate,
    context: TenantContext = Depends(get_tenant_context),
    service: AIService = Depends(get_ai_service)
) -> Any:
    """Update an existing knowledge base item."""
    update_data = item_data.model_dump(exclude_unset=True)
    return await service.update_knowledge_item(item_id, context, update_data)


@router.delete("/{project_id}/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_knowledge_item(
    project_id: UUID,
    item_id: UUID,
    context: TenantContext = Depends(get_tenant_context),
    service: AIService = Depends(get_ai_service)
) -> None:
    """Delete a knowledge base item."""
    await service.delete_knowledge_item(item_id, context)


@router.post("/{project_id}/scrape", response_model=KnowledgeBaseResponse)
async def scrape_knowledge_from_url(
    project_id: UUID,
    url_data: dict,  # {"url": "..."}
    context: TenantContext = Depends(get_tenant_context),
    service: AIService = Depends(get_ai_service)
) -> Any:
    """Scrape content from a URL and create a knowledge item."""
    url = url_data.get("url")
    if not url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL is required"
        )
        
    logger.info("Scraping URL for knowledge", url=url, project_id=str(context.project_id))
    
    scraped_data = await scraper.scrape_url(url)
    if not scraped_data:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not extract content from the provided URL"
        )
        
    data = {
        "title": scraped_data["title"],
        "content": scraped_data["content"],
        "source_type": "url",
        "source_url": url,
        "is_active": True
    }
    return await service.create_knowledge_item(context, data)
