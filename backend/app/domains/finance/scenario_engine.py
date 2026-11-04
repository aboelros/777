from typing import Dict, Any, List
from decimal import Decimal

from .schemas import ScenarioSimulationConfig
from .parameters import FinancialParameter, SourceType
from .projection_engine import ProjectionEngine


class ScenarioEngine:
    """
    Multi-scenario simulation and variance analysis engine.
    Preconfigures Conservative, Base Case, and Aggressive baselines.
    """

    @classmethod
    def get_default_scenarios(cls) -> Dict[str, ScenarioSimulationConfig]:
        """Return pre-configured baseline scenarios with audited assumption ranges."""
        return {
            "conservative": ScenarioSimulationConfig(
                scenario_name="Conservative Case",
                starting_customers=10,
                monthly_growth_rate_pct=Decimal("8.0"),
                monthly_churn_rate_pct=Decimal("6.5"),
                average_monthly_plan_usd=Decimal("49.00"),
                messages_per_customer_monthly=2000,
                ai_cost_per_1k_messages=Decimal("0.28"),
                whatsapp_cost_per_conversation=Decimal("0.025"),
                fixed_opex_monthly_usd=Decimal("4000.00"),
                starting_cash_balance_usd=Decimal("20000.00"),
                blended_cac_usd=Decimal("95.00"),
                annual_tax_rate_pct=Decimal("22.5")
            ),
            "base_case": ScenarioSimulationConfig(
                scenario_name="Base Case",
                starting_customers=25,
                monthly_growth_rate_pct=Decimal("15.0"),
                monthly_churn_rate_pct=Decimal("3.5"),
                average_monthly_plan_usd=Decimal("79.00"),
                messages_per_customer_monthly=3500,
                ai_cost_per_1k_messages=Decimal("0.25"),
                whatsapp_cost_per_conversation=Decimal("0.020"),
                fixed_opex_monthly_usd=Decimal("5000.00"),
                starting_cash_balance_usd=Decimal("25000.00"),
                blended_cac_usd=Decimal("65.00"),
                annual_tax_rate_pct=Decimal("22.5")
            ),
            "aggressive": ScenarioSimulationConfig(
                scenario_name="Aggressive Case (Upside)",
                starting_customers=50,
                monthly_growth_rate_pct=Decimal("25.0"),
                monthly_churn_rate_pct=Decimal("2.0"),
                average_monthly_plan_usd=Decimal("119.00"),
                messages_per_customer_monthly=5000,
                ai_cost_per_1k_messages=Decimal("0.22"),
                whatsapp_cost_per_conversation=Decimal("0.018"),
                fixed_opex_monthly_usd=Decimal("8500.00"),
                starting_cash_balance_usd=Decimal("40000.00"),
                blended_cac_usd=Decimal("45.00"),
                annual_tax_rate_pct=Decimal("22.5")
            )
        }

    @classmethod
    def compare_scenarios(cls, months: int = 36) -> Dict[str, Any]:
        """Run all 3 default scenarios and return a side-by-side comparison matrix."""
        scenarios = cls.get_default_scenarios()
        comparison = {}

        for key, cfg in scenarios.items():
            monthly, annuals, milestones = ProjectionEngine.run_projection(cfg, months=months)
            y1 = annuals[0] if len(annuals) > 0 else None
            y2 = annuals[1] if len(annuals) > 1 else None
            y3 = annuals[2] if len(annuals) > 2 else None

            comparison[key] = {
                "name": cfg.scenario_name,
                "starting_customers": cfg.starting_customers,
                "y1_ending_customers": y1.ending_customers if y1 else 0,
                "y3_ending_customers": y3.ending_customers if y3 else 0,
                "y1_revenue_usd": y1.total_revenue if y1 else Decimal("0.00"),
                "y2_revenue_usd": y2.total_revenue if y2 else Decimal("0.00"),
                "y3_revenue_usd": y3.total_revenue if y3 else Decimal("0.00"),
                "y1_arr_usd": (monthly[11].total_revenue * Decimal("12.0")).quantize(Decimal("0.01")) if len(monthly) >= 12 else Decimal("0.00"),
                "y3_arr_usd": (monthly[-1].total_revenue * Decimal("12.0")).quantize(Decimal("0.01")),
                "y3_gross_margin_pct": y3.gross_margin_pct if y3 else Decimal("0.0"),
                "y3_net_income_usd": y3.net_income if y3 else Decimal("0.00"),
                "breakeven_month": milestones["breakeven_month"],
                "capital_required_usd": milestones["capital_required_usd"],
                "ending_cash_balance_usd": annuals[-1].ending_cash_balance if annuals else Decimal("0.00"),
                "status_label": "High Risk / Upside Only" if key == "aggressive" else ("Conservative Floor" if key == "conservative" else "Target Base")
            }

        return comparison
