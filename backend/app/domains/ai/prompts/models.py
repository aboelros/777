from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class BrandProfile(BaseModel):
    """Brand identity configuration isolated per tenant."""
    store_name: str = Field(..., min_length=1, max_length=100)
    bot_name: str = Field(default="Sales Specialist", max_length=50)
    brand_tone: str = Field(default="Warm, natural, charismatic, and genuinely helpful", max_length=200)
    primary_language: str = Field(default="Arabic", max_length=30)
    supported_languages: List[str] = Field(default_factory=lambda: ["Arabic", "English"])
    greeting_message: Optional[str] = None


class SalesPolicy(BaseModel):
    """Operational business policies and boundary constraints."""
    max_discount_percent: float = Field(default=0.0, ge=0.0, le=50.0)
    return_window_days: int = Field(default=14, ge=0, le=90)
    free_shipping_threshold: Optional[float] = Field(default=None, ge=0.0)
    allow_competitor_comparison: bool = Field(default=False)
    prohibited_claims: List[str] = Field(
        default_factory=lambda: [
            "Do not promise delivery dates not confirmed by tools",
            "Do not promise discounts beyond approved policy",
            "Do not claim stock that is not verified in inventory",
            "Do not invent return or refund terms"
        ]
    )
    escalation_triggers: List[str] = Field(
        default_factory=lambda: [
            "Customer repeatedly requests human agent",
            "Dispute regarding order payment or refund",
            "Unresolved complaint or legal threat"
        ]
    )


class ChannelConfig(BaseModel):
    """Channel-specific behavioral constraints."""
    channel_name: str = Field(default="whatsapp")
    max_sentences_per_turn: int = Field(default=3, ge=1, le=10)
    use_emojis: bool = Field(default=True)
    suggest_next_step: bool = Field(default=True)


class TenantPromptConfig(BaseModel):
    """Complete tenant-isolated prompt specification."""
    project_id: UUID
    brand: BrandProfile
    policy: SalesPolicy = Field(default_factory=SalesPolicy)
    channel: ChannelConfig = Field(default_factory=ChannelConfig)
    custom_instructions: List[str] = Field(default_factory=list)
    version: str = Field(default="1.0.0")


class PromptVersionInfo(BaseModel):
    """Metadata representing an immutable prompt version snapshot."""
    version: str
    sha256_hash: str
    project_id: UUID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
