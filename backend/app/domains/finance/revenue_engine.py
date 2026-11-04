from typing import Dict, Any, Optional
from decimal import Decimal, ROUND_HALF_UP


class RevenueEngine:
    """
    Deterministic SaaS recurring and usage revenue computation engine.
    Calculates MRR, ARR, ARPU, ARPA, and net new revenue dynamics.
    """

    # Baseline tier monthly prices in USD (from subscription_plans.py)
    TIER_PRICES = {
        "starter": Decimal("29.00"),
        "growth": Decimal("59.00"),
        "professional": Decimal("119.00"),
        "scale": Decimal("199.00"),
        "business": Decimal("349.00"),
        "enterprise": Decimal("799.00"),
    }

    @staticmethod
    def calculate_subscription_revenue(
        customer_count: int,
        average_plan_usd: Decimal
    ) -> Decimal:
        """Calculate total base subscription revenue for a customer cohort."""
        if customer_count <= 0 or average_plan_usd <= Decimal("0.0"):
            return Decimal("0.00")
        return (Decimal(customer_count) * average_plan_usd).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def calculate_usage_revenue(
        customer_count: int,
        messages_per_customer: int,
        included_messages_per_tier: int = 2000,
        overage_per_1k_usd: Decimal = Decimal("5.00")
    ) -> Decimal:
        """
        Calculate usage-based overage revenue.
        Overage applies when customer volume exceeds plan quota.
        """
        if customer_count <= 0 or messages_per_customer <= included_messages_per_tier:
            return Decimal("0.00")
        
        excess_messages = messages_per_customer - included_messages_per_tier
        overage_thousands = Decimal(excess_messages) / Decimal("1000.0")
        overage_per_cust = overage_thousands * overage_per_1k_usd
        total = Decimal(customer_count) * overage_per_cust
        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def calculate_mrr(
        subscription_rev: Decimal,
        predictable_usage_rev: Decimal = Decimal("0.00")
    ) -> Decimal:
        """Compute total Monthly Recurring Revenue (MRR)."""
        return (subscription_rev + predictable_usage_rev).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def calculate_arr(mrr: Decimal) -> Decimal:
        """Annual Recurring Revenue = MRR * 12."""
        return (mrr * Decimal("12.0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def calculate_arpu(total_revenue: Decimal, active_customers: int) -> Decimal:
        """Average Revenue Per User (monthly). Division-by-zero safe."""
        if active_customers <= 0 or total_revenue <= Decimal("0.0"):
            return Decimal("0.00")
        return (total_revenue / Decimal(active_customers)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def calculate_mrr_movements(
        prior_mrr: Decimal,
        new_mrr: Decimal,
        expansion_mrr: Decimal = Decimal("0.00"),
        contraction_mrr: Decimal = Decimal("0.00"),
        churned_mrr: Decimal = Decimal("0.00")
    ) -> Dict[str, Decimal]:
        """
        Detailed SaaS MRR waterfall accounting.
        Net New MRR = New + Expansion - Contraction - Churned.
        """
        net_new = new_mrr + expansion_mrr - contraction_mrr - churned_mrr
        ending_mrr = prior_mrr + net_new
        return {
            "beginning_mrr": prior_mrr.quantize(Decimal("0.01")),
            "new_mrr": new_mrr.quantize(Decimal("0.01")),
            "expansion_mrr": expansion_mrr.quantize(Decimal("0.01")),
            "contraction_mrr": contraction_mrr.quantize(Decimal("0.01")),
            "churned_mrr": churned_mrr.quantize(Decimal("0.01")),
            "net_new_mrr": net_new.quantize(Decimal("0.01")),
            "ending_mrr": max(Decimal("0.00"), ending_mrr).quantize(Decimal("0.01"))
        }
