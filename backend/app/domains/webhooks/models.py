from datetime import datetime
from uuid import uuid4
from sqlalchemy import (
    Column, String, Boolean, DateTime, ForeignKey, Index, Text
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.domains.apps.models import AppInstallation

class WebhookEndpoint(Base):
    """External endpoints subscribed to receive platform events."""
    __tablename__ = "webhook_endpoints"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    # If the webhook was created by a 3rd party app
    app_installation_id = Column(UUID(as_uuid=True), ForeignKey("app_installations.id", ondelete="CASCADE"), nullable=True)
    
    url = Column(String(1000), nullable=False)
    secret = Column(String(255), nullable=False)  # Used to sign the payload (HMAC-SHA256)
    
    # Subscribed events (e.g., ["order.created", "customer.updated", "message.received"])
    events = Column(JSONB, default=[])
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project")
    app_installation = relationship("AppInstallation")


class WebhookDelivery(Base):
    """Log of webhook delivery attempts for observability and retry logic."""
    __tablename__ = "webhook_deliveries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    endpoint_id = Column(UUID(as_uuid=True), ForeignKey("webhook_endpoints.id", ondelete="CASCADE"), nullable=False)
    
    event_type = Column(String(255), nullable=False)
    payload = Column(JSONB, nullable=False)
    
    status = Column(String(50), nullable=False)  # pending, success, failed
    status_code = Column(String(10)) # HTTP status code
    response_body = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    endpoint = relationship("WebhookEndpoint")
