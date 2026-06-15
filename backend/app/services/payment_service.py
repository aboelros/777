from datetime import datetime
from uuid import UUID
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import Invoice, PaymentLink, Project
# import stripe 

class PaymentService:
    """Handles payments and invoicing (Mock Stripe Implementation)."""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_payment_link(self, project_id: UUID, amount: float, currency: str = "USD", description: str = "") -> PaymentLink:
        """Generate a payment link (Mock)."""
        
        # In a real app:
        # stripe_key = await self._get_stripe_key(project_id)
        # stripe.api_key = stripe_key
        # session = stripe.checkout.Session.create(...)
        # url = session.url
        
        # Mocking for MVP
        mock_url = f"https://buy.stripe.com/test_{project_id}_{datetime.now().timestamp()}"
        
        link = PaymentLink(
            project_id=project_id,
            url=mock_url,
            amount=amount,
            currency=currency,
            description=description,
            status="active"
        )
        self.db.add(link)
        await self.db.commit()
        await self.db.refresh(link)
        return link

    async def create_invoice(self, project_id: UUID, customer_id: UUID, items: List[dict], notes: str = None) -> Invoice:
        """Create an invoice."""
        
        total_amount = sum(item.get("price", 0) * item.get("quantity", 1) for item in items)
        
        # Generate Invoice Number (Simple Auto-increment logic or UUID)
        invoice_number = f"INV-{int(datetime.now().timestamp())}"
        
        invoice = Invoice(
            project_id=project_id,
            customer_id=customer_id,
            invoice_number=invoice_number,
            items=items,
            amount=total_amount,
            total_amount=total_amount, # Tax calc logic could go here
            notes=notes,
            status="draft"
        )
        self.db.add(invoice)
        await self.db.commit()
        await self.db.refresh(invoice)
        return invoice
        
    async def get_project_invoices(self, project_id: UUID):
         result = await self.db.execute(
             select(Invoice).where(Invoice.project_id == project_id)
         )
         return result.scalars().all()
