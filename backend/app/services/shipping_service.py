"""
Shipping and Tax calculation service for AI Bot tools.
"""

from typing import Dict, Any, Optional
from decimal import Decimal
import structlog

logger = structlog.get_logger(__name__)

class ShippingService:
    """
    Handles calculation of shipping rates and taxes based on location and order details.
    """
    
    def __init__(self, projects_settings: Optional[Dict[str, Any]] = None):
        # Default settings if none provided
        self.settings = projects_settings or {
            "default_tax_rate": 0.05,  # 5% default
            "base_shipping_fee": 10.0,
            "free_shipping_threshold": 100.0,
            "international_multiplier": 2.5
        }

    async def calculate(
        self, 
        destination: str, 
        items_total: float, 
        currency: str = "USD"
    ) -> Dict[str, Any]:
        """
        Calculate shipping and tax for an order.
        
        Args:
            destination: The shipping address or city/country
            items_total: Total value of items
            currency: Currency code
            
        Returns:
            Dict containing shipping_fee, tax_amount, total, and estimated_delivery
        """
        try:
            logger.info("Calculating shipping and tax", destination=destination, total=items_total)
            
            # 1. Tax Calculation
            tax_rate = self.settings.get("default_tax_rate", 0.05)
            tax_amount = items_total * tax_rate
            
            # 2. Shipping Calculation
            shipping_fee = self.settings.get("base_shipping_fee", 10.0)
            
            # Apply discounts/thresholds
            if items_total >= self.settings.get("free_shipping_threshold", 100.0):
                shipping_fee = 0.0
            
            # Destination-based logic (simple heuristic for now)
            is_local = any(local in destination.lower() for local in ["local", "nearby", "here"])
            # Multiplier for international/long distance
            if not is_local and len(destination) > 5:
                 # If destination looks like a full address or specific far city
                 shipping_fee = shipping_fee * self.settings.get("international_multiplier", 1.5)

            # 3. Final Total
            grand_total = items_total + tax_amount + shipping_fee
            
            # 4. Delivery Estimation
            days = 2 if is_local else 5
            estimated_delivery = f"Expected delivery in {days}-{days+2} business days."

            return {
                "success": True,
                "items_total": round(items_total, 2),
                "shipping_fee": round(shipping_fee, 2),
                "tax_amount": round(tax_amount, 2),
                "tax_rate_used": f"{tax_rate * 100}%",
                "total": round(grand_total, 2),
                "currency": currency,
                "destination": destination,
                "estimated_delivery": estimated_delivery
            }

        except Exception as e:
            logger.error("Shipping calculation failed", error=str(e))
            return {
                "success": False,
                "error": f"Failed to calculate shipping: {str(e)}"
            }
