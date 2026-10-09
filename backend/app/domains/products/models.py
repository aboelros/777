from datetime import datetime
from uuid import uuid4
from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean, DateTime, 
    ForeignKey, Index, JSON, Enum as SQLEnum, LargeBinary, ARRAY
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class ProductImage(Base):
    """
    Dedicated storage for product images/binary data.
    Used by PostgresStorageService when not using S3/Local.
    """
    __tablename__ = "product_images"
    
    # We use a text key as primary key (e.g. products/uuid/image.jpg)
    key = Column(String(500), primary_key=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True)
    
    # Binary data
    data = Column(LargeBinary, nullable=False)
    content_type = Column(String(100), nullable=False)
    size = Column(Integer, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<ProductImage {self.key}>"



class Product(Base):
    """Product catalog for AI-powered social media responses."""
    __tablename__ = "products"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    # Product information
    name = Column(String(255), nullable=False)
    description = Column(Text)
    sku = Column(String(100))
    price = Column(Float)
    currency = Column(String(3), default="USD")
    
    # Inventory
    stock_quantity = Column(Integer, default=0)
    in_stock = Column(Boolean, default=True)
    # Storage
    storage_locations = Column(JSONB, default=[])
    reorder_point = Column(Integer, default=0)
    safety_stock = Column(Integer, default=0)
    storage_notes = Column(Text)
    storage_attachments = Column(JSONB, default=[])
    
    # Media
    images = Column(JSONB, default=[])  # Array of image URLs
    
    # Categories and tags
    category = Column(String(100))
    tags = Column(JSONB, default=[])
    
    # Specifications
    specifications = Column(JSONB, default={})  # Size, color, material, etc.
    
    # FAQ and common questions
    faq = Column(JSONB, default=[])  # [{question: "", answer: ""}]
    
    # SEO and marketing
    keywords = Column(JSONB, default=[])  # Keywords for AI matching
    
    # Extra data
    extra_data = Column(JSONB, default={})
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", backref="products")
    
    # Indexes
    __table_args__ = (
        Index("idx_product_project", "project_id"),
        Index("idx_product_sku", "sku"),
        Index("idx_product_name", "name"),
    )
    
    def __repr__(self):
        return f"<Product {self.name}>"

