from pydantic import BaseModel
from typing import List, Optional

class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    sku: str | None = None
    price: float | None = None
    currency: str = "USD"
    stock_quantity: int = 0
    in_stock: bool = True
    images: List[dict] = []
    category: str | None = None
    tags: List[str] = []
    specifications: dict = {}
    faq: List[dict] = []
    keywords: List[str] = []
    storage_locations: List[dict] = []
    reorder_point: int = 0
    safety_stock: int = 0
    storage_notes: Optional[str] = None
    storage_attachments: List[str] = []


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    sku: str | None = None
    price: float | None = None
    currency: str | None = None
    stock_quantity: int | None = None
    in_stock: bool | None = None
    images: List[dict] | None = None
    category: str | None = None
    tags: List[str] | None = None
    specifications: dict | None = None
    faq: List[dict] | None = None
    keywords: List[str] | None = None
    is_active: bool | None = None
    storage_locations: List[dict] | None = None
    reorder_point: int | None = None
    safety_stock: int | None = None
    storage_notes: Optional[str] = None
    storage_attachments: List[str] | None = None


class ProductResponse(BaseModel):
    id: str
    name: str
    description: str | None
    sku: str | None
    price: float | None
    currency: str
    stock_quantity: int
    in_stock: bool
    images: List[dict]
    category: str | None
    tags: List[str]
    specifications: dict
    faq: List[dict]
    keywords: List[str]
    storage_locations: List[dict]
    reorder_point: int
    safety_stock: int
    storage_notes: Optional[str]
    storage_attachments: List[str]
    is_active: bool
    created_at: str
    updated_at: str | None

    class Config:
        from_attributes = True
