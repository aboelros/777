from typing import Dict, Any, List
from decimal import Decimal, ROUND_HALF_UP


class GrowthEngine:
    """
    Cohort growth, retention, churn, CAC, and LTV calculation engine.
    Ensures mathematical consistency between acquisition velocity and customer lifetime value.
    """

    @staticmethod
    def calculate_cohort_turn(
        starting_customers: int,
        monthly_growth_rate_pct: Decimal,
        monthly_churn_rate_pct: Decimal,
        saturation_ceiling: int = 100_000
    ) -> Dict[str, int]:
        """
        Advance customer count by one month with realistic churn and saturation damping.
        """
        if starting_customers <= 0:
            return {"beginning": 0, "new": 0, "churned": 0, "ending": 0}

        churn_rate = monthly_churn_rate_pct / Decimal("100.0")
        growth_rate = monthly_growth_rate_pct / Decimal("100.0")

        # Saturation damping: growth rate naturally decelerates as base approaches addressable ceiling
        if starting_customers > 5000:
            damping_factor = max(Decimal("0.2"), Decimal("1.0") - (Decimal(starting_customers) / Decimal(saturation_ceiling)))
            growth_rate = growth_rate * damping_factor

        churned = int((Decimal(starting_customers) * churn_rate).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        # Ensure at least 1 new customer if growth rate > 0
        raw_new = (Decimal(starting_customers) * growth_rate).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        new_cust = max(1 if growth_rate > Decimal("0.0") else 0, int(raw_new))

        ending = max(0, starting_customers + new_cust - churned)
        return {
            "beginning": starting_customers,
            "new": new_cust,
            "churned": churned,
            "ending": ending
        }

    @staticmethod
    def calculate_annualized_churn(monthly_churn_pct: Decimal) -> Decimal:
        """
        Convert monthly churn rate to compound annualized churn.
        Annual Churn = 1 - (1 - monthly_churn)^12.
        """
        if monthly_churn_pct <= Decimal("0.0"):
            return Decimal("0.0")
        if monthly_churn_pct >= Decimal("100.0"):
            return Decimal("100.0")

        m_rate = float(monthly_churn_pct) / 100.0
        ann_rate = 1.0 - ((1.0 - m_rate) ** 12)
        return Decimal(str(round(ann_rate * 100.0, 1)))

    @staticmethod
    def calculate_unit_economics(
        arpu_monthly: Decimal,
        gross_margin_pct: Decimal,
        monthly_churn_pct: Decimal,
        cac_usd: Decimal
    ) -> Dict[str, Decimal]:
        """
        Compute SaaS unit economics: Lifetime, LTV, LTV/CAC, and Payback.
        Division-by-zero safe.
        """
        if arpu_monthly <= Decimal("0.0") or monthly_churn_pct <= Decimal("0.0"):
            return {
                "customer_lifetime_months": Decimal("0.0"),
                "ltv": Decimal("0.00"),
                "ltv_cac_ratio": Decimal("0.0"),
                "cac_payback_months": Decimal("0.0")
            }

        churn_decimal = monthly_churn_pct / Decimal("100.0")
        lifetime_months = (Decimal("1.0") / churn_decimal).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)

        # Gross margin per customer monthly
        gm_decimal = gross_margin_pct / Decimal("100.0")
        monthly_contribution = arpu_monthly * gm_decimal

        # LTV = Monthly Contribution / Monthly Churn
        ltv = (monthly_contribution / churn_decimal).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # LTV / CAC Ratio
        ltv_cac = Decimal("0.0")
        payback_months = Decimal("0.0")
        if cac_usd > Decimal("0.0"):
            ltv_cac = (ltv / cac_usd).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
            if monthly_contribution > Decimal("0.0"):
                payback_months = (cac_usd / monthly_contribution).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)

        return {
            "customer_lifetime_months": lifetime_months,
            "ltv": ltv,
            "ltv_cac_ratio": ltv_cac,
            "cac_payback_months": payback_months
        }
