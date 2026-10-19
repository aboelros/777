from datetime import datetime
from uuid import UUID
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domains.billing.models import Invoice, PaymentLink
from app.domains.projects.models import Project
from app.core.context import TenantContext

class PaymentService:
    """Handles payments and invoicing (Mock Stripe Implementation)."""
    
    def __init__(self, db: AsyncSession, context: TenantContext):
        self.db = db
        self.context = context
        self.project_id = context.project_id

    async def create_payment_link(
        self,
        amount: float,
        currency: str = "USD",
        description: str = "",
        invoice_id: Optional[UUID] = None,
    ) -> PaymentLink:
        """Generate a payment link using Stripe or deterministic mock fallback."""
        from app.services.stripe_service import StripePaymentProvider

        metadata = {}
        if invoice_id:
            metadata["invoice_id"] = str(invoice_id)

        session_res = await StripePaymentProvider.create_checkout_session(
            project_id=self.project_id,
            amount=amount,
            currency=currency,
            description=description,
            metadata=metadata,
        )

        link = PaymentLink(
            project_id=self.project_id,
            invoice_id=invoice_id,
            url=session_res["url"],
            stripe_payment_link_id=session_res["session_id"],
            amount=amount,
            currency=currency,
            description=description,
            status="active",
        )
        self.db.add(link)
        await self.db.commit()
        await self.db.refresh(link)
        return link

    async def create_invoice(self, customer_id: UUID, items: List[dict], notes: str = None) -> Invoice:
        """Create an invoice."""
        from app.domains.customers.repository import CustomerProfileRepository
        from fastapi import HTTPException, status

        customer_repo = CustomerProfileRepository(self.db)
        customer = await customer_repo.get_profile_by_context(self.context, customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        total_amount = sum(item.get("price", 0) * item.get("quantity", 1) for item in items)
        
        invoice_number = f"INV-{int(datetime.now().timestamp())}"
        
        invoice = Invoice(
            project_id=self.project_id,
            customer_id=customer_id,
            invoice_number=invoice_number,
            items=items,
            amount=total_amount,
            total_amount=total_amount,
            notes=notes,
            status="draft"
        )
        self.db.add(invoice)
        await self.db.commit()
        await self.db.refresh(invoice)
        return invoice
        
    async def get_project_invoices(self):
         result = await self.db.execute(
             select(Invoice).where(Invoice.project_id == self.project_id)
         )
         return result.scalars().all()
