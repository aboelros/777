from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

class PaymentLinkResponse(BaseModel):
    id: UUID
    project_id: UUID
    url: str
    amount: float
    currency: str
    status: str
    
    class Config:
        from_attributes = True

class InvoiceResponse(BaseModel):
    id: UUID
    project_id: UUID
    customer_id: Optional[UUID] = None
    invoice_number: str
    status: str
    amount: float
    total_amount: float
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True
