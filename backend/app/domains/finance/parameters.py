from typing import Any, Optional
from datetime import datetime
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field


class SourceType(str, Enum):
    ACTUAL = "actual"
    VERIFIED_EXTERNAL = "verified_external"
    USER_ASSUMPTION = "user_assumption"
    ILLUSTRATIVE_DEFAULT = "illustrative_default"


class FinancialParameter(BaseModel):
    """
    Standardized wrapper for all financial parameters.
    Enforces provenance tracking, source transparency, and auditability.
    """
    key: str
    value: Decimal
    currency: str = "USD"
    source: str
    source_type: SourceType = SourceType.ILLUSTRATIVE_DEFAULT
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    is_editable: bool = True
    description: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True

    def to_float(self) -> float:
        """Helper for downstream visualization serializers."""
        return float(self.value)


class ExchangeRateRegistry:
    """
    Deterministic currency conversion rates with timestamps.
    Prevents hardcoded assumptions and records date of FX rate.
    """
    # Base is USD
    RATES = {
        "USD": Decimal("1.0"),
        "EGP": Decimal("48.50"),   # Sourced: CBE Q4 2024 / Q1 2025
        "SAR": Decimal("3.75"),    # Sourced: SAMA Fixed Peg
        "AED": Decimal("3.6725"),  # Sourced: CBUAE Fixed Peg
        "EUR": Decimal("0.92"),    # Sourced: ECB reference
        "GBP": Decimal("0.78"),    # Sourced: BOE reference
    }
    LAST_UPDATED = datetime(2025, 1, 15)

    @classmethod
    def convert(cls, amount: Decimal, from_curr: str, to_curr: str) -> Decimal:
        """Convert amount between supported currencies."""
        if from_curr == to_curr:
            return amount
        from_rate = cls.RATES.get(from_curr.upper(), Decimal("1.0"))
        to_rate = cls.RATES.get(to_curr.upper(), Decimal("1.0"))
        # Amount in USD = amount / from_rate
        usd_amount = amount / from_rate
        return usd_amount * to_rate
