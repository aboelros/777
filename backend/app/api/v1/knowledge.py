"""
Knowledge base management endpoints.
"""

from typing import List, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.domains.ai.models import KnowledgeBase
from app.domains.projects.models import ProjectRole
from app.core.access_control import verify_project_access
from app.services.scraper_service import scraper
from app.domains.ai.schemas import KnowledgeBaseCreate, KnowledgeBaseUpdate, KnowledgeBaseResponse

router = APIRouter()
logger = structlog.get_logger(__name__)


@router.get("/{project_id}", response_model=List[KnowledgeBaseResponse])
async def list_knowledge_items(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
) -> Any:
    """
    List all knowledge base items for a specific project.
    """
    await verify_project_access(project_id, user_id, db)
    
    result = await db.execute(
        select(KnowledgeBase)
        .where(KnowledgeBase.project_id == project_id)
        .order_by(KnowledgeBase.created_at.desc())
    )
    return result.scalars().all()


@router.post("/{project_id}", response_model=KnowledgeBaseResponse, status_code=status.HTTP_201_CREATED)
async def create_knowledge_item(
    project_id: UUID,
    item_data: KnowledgeBaseCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
) -> Any:
    """
    Create a new knowledge base item for a project.
    """
    await verify_project_access(
        project_id, 
        user_id, 
        db, 
        required_roles=[ProjectRole.OWNER, ProjectRole.MODERATOR]
    )
    
    new_item = KnowledgeBase(
        project_id=project_id,
        title=item_data.title,
        content=item_data.content,
        source_type=item_data.source_type,
        source_url=item_data.source_url,
        is_active=item_data.is_active,
        tags=item_data.tags,
        metadata_info=item_data.metadata_info
    )
    
    db.add(new_item)
    await db.commit()
    await db.refresh(new_item)
    
    logger.info(
        "Knowledge item created", 
        item_id=str(new_item.id), 
        project_id=str(project_id),
        user_id=user_id
    )
    
    return new_item


@router.patch("/{project_id}/{item_id}", response_model=KnowledgeBaseResponse)
async def update_knowledge_item(
    project_id: UUID,
    item_id: UUID,
    item_data: KnowledgeBaseUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
) -> Any:
    """
    Update an existing knowledge base item.
    """
    await verify_project_access(
        project_id, 
        user_id, 
        db, 
        required_roles=[ProjectRole.OWNER, ProjectRole.MODERATOR]
    )
    
    result = await db.execute(
        select(KnowledgeBase).where(
            KnowledgeBase.id == item_id, 
            KnowledgeBase.project_id == project_id
        )
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge item not found"
        )
        
    update_data = item_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)
        
    await db.commit()
    await db.refresh(item)
    
    logger.info(
        "Knowledge item updated", 
        item_id=str(item_id), 
        project_id=str(project_id)
    )
    
    return item


@router.delete("/{project_id}/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_knowledge_item(
    project_id: UUID,
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
) -> None:
    """
    Delete a knowledge base item.
    """
    await verify_project_access(
        project_id, 
        user_id, 
        db, 
        required_roles=[ProjectRole.OWNER, ProjectRole.MODERATOR]
    )
    
    result = await db.execute(
        select(KnowledgeBase).where(
            KnowledgeBase.id == item_id, 
            KnowledgeBase.project_id == project_id
        )
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge item not found"
        )
        
    await db.delete(item)
    await db.commit()
    
    logger.info(
        "Knowledge item deleted", 
        item_id=str(item_id), 
        project_id=str(project_id)
    )
    
    return None

@router.post("/{project_id}/scrape", response_model=KnowledgeBaseResponse)
async def scrape_knowledge_from_url(
    project_id: UUID,
    url_data: dict,  # {"url": "..."}
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
) -> Any:
    """
    Scrape content from a URL and create a knowledge item.
    """
    await verify_project_access(
        project_id, 
        user_id, 
        db, 
        required_roles=[ProjectRole.OWNER, ProjectRole.MODERATOR]
    )
    
    url = url_data.get("url")
    if not url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL is required"
        )
        
    logger.info("Scraping URL for knowledge", url=url, project_id=str(project_id))
    
    scraped_data = await scraper.scrape_url(url)
    if not scraped_data:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not extract content from the provided URL"
        )
        
    new_item = KnowledgeBase(
        project_id=project_id,
        title=scraped_data["title"],
        content=scraped_data["content"],
        source_type="url",
        source_url=url,
        is_active=True
    )
    
    db.add(new_item)
    await db.commit()
    await db.refresh(new_item)
    
    logger.info(
        "Knowledge item created from scrape", 
        item_id=str(new_item.id), 
        url=url
    )
    
    return new_item
