from typing import Any, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.core.access_control import verify_project_access
from app.services.payment_service import PaymentService

router = APIRouter()

@router.post("/{project_id}/payment-links")
async def create_payment_link(
    project_id: UUID,
    amount: float = Body(...),
    description: str = Body(""),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Create a quick payment link."""
    await verify_project_access(project_id, user_id, db)
    
    service = PaymentService(db)
    link = await service.create_payment_link(project_id, amount, description=description)
    return link

@router.get("/{project_id}/invoices")
async def get_invoices(
    project_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get all invoices for a project."""
    await verify_project_access(project_id, user_id, db)
    
    service = PaymentService(db)
    invoices = await service.get_project_invoices(project_id)
    return invoices

@router.post("/{project_id}/invoices")
async def create_invoice(
    project_id: UUID,
    customer_id: UUID = Body(...),
    items: List[dict] = Body(...),
    notes: str = Body(None),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Create a formal invoice."""
    await verify_project_access(project_id, user_id, db)
    
    service = PaymentService(db)
    invoice = await service.create_invoice(project_id, customer_id, items, notes)
    return invoice
