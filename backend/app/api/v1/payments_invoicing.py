from typing import Any, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Body, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.context import TenantContext
from app.api.dependencies.tenant import get_tenant_context
from app.services.payment_service import PaymentService
from app.domains.billing.schemas import PaymentLinkResponse, InvoiceResponse

router = APIRouter()

@router.post("/{project_id}/payment-links", response_model=PaymentLinkResponse)
async def create_payment_link(
    amount: Optional[float] = Body(None),
    description: str = Body(""),
    invoice_id: Optional[UUID] = Body(None),
    tenant: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Create a payment link with server-enforced pricing when linked to an invoice."""
    from sqlalchemy import select
    from app.domains.billing.models import Invoice

    final_amount = amount or 0.0
    if invoice_id:
        res = await db.execute(
            select(Invoice).where(
                Invoice.id == invoice_id,
                Invoice.project_id == tenant.project_id
            )
        )
        invoice = res.scalars().first()
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found in project")
        # Enforce server-side authoritative invoice price to prevent client tampering
        final_amount = invoice.total_amount or invoice.amount

    if final_amount <= 0:
        raise HTTPException(status_code=400, detail="Payment amount must be greater than zero")

    service = PaymentService(db, tenant)
    link = await service.create_payment_link(
        final_amount,
        description=description,
        invoice_id=invoice_id
    )
    return link

@router.get("/{project_id}/invoices", response_model=List[InvoiceResponse])
async def get_invoices(
    tenant: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get all invoices for a project."""
    service = PaymentService(db, tenant)
    invoices = await service.get_project_invoices()
    return invoices

@router.post("/{project_id}/invoices", response_model=InvoiceResponse)
async def create_invoice(
    customer_id: UUID = Body(...),
    items: List[dict] = Body(...),
    notes: str = Body(None),
    tenant: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Create a formal invoice."""
    service = PaymentService(db, tenant)
    invoice = await service.create_invoice(customer_id, items, notes)
    return invoice

@router.post("/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Stripe webhook receiver for asynchronous payment confirmations."""
    from app.services.stripe_service import (
        StripePaymentProvider,
        reconcile_stripe_checkout_completed,
        reconcile_stripe_checkout_failed,
    )

    body = await request.body()
    sig_header = request.headers.get("stripe-signature")

    event = StripePaymentProvider.verify_webhook_signature(body, sig_header)
    if not event:
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_type = event.get("type")
    session_obj = event.get("data", {}).get("object", {})

    if event_type == "checkout.session.completed":
        return await reconcile_stripe_checkout_completed(db, session_obj)

    if event_type in ("checkout.session.expired", "payment_intent.payment_failed"):
        return await reconcile_stripe_checkout_failed(db, session_obj)

    return {"status": "ignored", "event_type": event_type}
