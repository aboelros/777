from typing import List, Dict, Any, Tuple
from decimal import Decimal, ROUND_HALF_UP

from .schemas import (
    FinancialStatementMonthly,
    FinancialStatementAnnual,
    ScenarioSimulationConfig,
    UnitEconomicsBreakdown
)
from .revenue_engine import RevenueEngine
from .cost_engine import CostEngine
from .growth_engine import GrowthEngine


class ProjectionEngine:
    """
    Multi-period financial projection and cash balance simulation engine.
    Produces month-by-month statements and annual rollups for 12, 36, or 60 months.
    """

    @classmethod
    def run_projection(
        cls,
        config: ScenarioSimulationConfig,
        months: int = 36
    ) -> Tuple[List[FinancialStatementMonthly], List[FinancialStatementAnnual], Dict[str, Any]]:
        """Execute deterministic month-by-month income statement & cash flow projection."""
        monthly_statements: List[FinancialStatementMonthly] = []
        current_customers = config.starting_customers
        current_cash = config.starting_cash_balance_usd
        peak_deficit = Decimal("0.00")
        
        milestones = {
            "breakeven_month": None,
            "month_10k_net_profit": None,
            "month_100k_net_profit": None,
            "month_1m_net_profit": None,
            "capital_required_usd": Decimal("0.00")
        }

        # Progressive OPEX scale: fixed costs gradually expand as customer volume grows
        base_opex = config.fixed_opex_monthly_usd

        for m in range(1, months + 1):
            # 1. Customer cohort movement
            cohort = GrowthEngine.calculate_cohort_turn(
                starting_customers=current_customers,
                monthly_growth_rate_pct=config.monthly_growth_rate_pct,
                monthly_churn_rate_pct=config.monthly_churn_rate_pct
            )
            active_cust = cohort["ending"]

            # 2. Revenue calculation
            sub_rev = RevenueEngine.calculate_subscription_revenue(
                customer_count=active_cust,
                average_plan_usd=config.average_monthly_plan_usd
            )
            usage_rev = RevenueEngine.calculate_usage_revenue(
                customer_count=active_cust,
                messages_per_customer=config.messages_per_customer_monthly
            )
            tot_rev = sub_rev + usage_rev

            # 3. Cost of Goods Sold (COGS)
            cogs_breakdown = CostEngine.calculate_customer_cogs(
                plan_revenue_monthly=config.average_monthly_plan_usd,
                messages_count=config.messages_per_customer_monthly,
                country_code="DEFAULT",
                ai_cost_per_1k_msgs=config.ai_cost_per_1k_messages,
                payment_fee_pct=config.payment_gateway_pct,
                payment_fee_fixed=config.payment_gateway_fixed_usd
            )
            total_cogs = cogs_breakdown["total_cogs"] * Decimal(active_cust)

            # 4. OPEX scaling with business maturity
            # Headcount and support scale with customer milestones
            scale_mult = Decimal("1.0") + (Decimal(active_cust) / Decimal("2000.0"))
            month_opex = (base_opex * scale_mult).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            rd = (month_opex * Decimal("0.45")).quantize(Decimal("0.01"))
            sm = (month_opex * Decimal("0.35")).quantize(Decimal("0.01"))
            ga = (month_opex * Decimal("0.20")).quantize(Decimal("0.01"))

            # 5. Full Statement line items
            pnl = CostEngine.calculate_statement_line_items(
                total_revenue=tot_rev,
                total_cogs=total_cogs,
                total_opex=month_opex,
                tax_rate_pct=config.annual_tax_rate_pct
            )

            # 6. Cash balance update
            fcf = pnl["free_cash_flow"]
            current_cash = current_cash + fcf
            if current_cash < Decimal("0.00"):
                deficit = abs(current_cash)
                if deficit > peak_deficit:
                    peak_deficit = deficit

            # Check milestones
            if pnl["net_income"] > Decimal("0.00") and milestones["breakeven_month"] is None:
                milestones["breakeven_month"] = m
            if pnl["net_income"] >= Decimal("10000.00") and milestones["month_10k_net_profit"] is None:
                milestones["month_10k_net_profit"] = m
            if pnl["net_income"] >= Decimal("100000.00") and milestones["month_100k_net_profit"] is None:
                milestones["month_100k_net_profit"] = m
            if pnl["net_income"] >= Decimal("1000000.00") and milestones["month_1m_net_profit"] is None:
                milestones["month_1m_net_profit"] = m

            stmt = FinancialStatementMonthly(
                month=m,
                active_customers=active_cust,
                new_customers=cohort["new"],
                churned_customers=cohort["churned"],
                subscription_revenue=sub_rev,
                usage_revenue=usage_rev,
                total_revenue=tot_rev,
                cogs=total_cogs,
                gross_profit=pnl["gross_profit"],
                gross_margin_pct=pnl["gross_margin_pct"],
                rd_expense=rd,
                sm_expense=sm,
                ga_expense=ga,
                total_opex=month_opex,
                ebitda=pnl["ebitda"],
                depreciation_amortization=Decimal("0.00"),
                ebit=pnl["ebit"],
                interest_expense=Decimal("0.00"),
                tax_expense=pnl["tax_expense"],
                net_income=pnl["net_income"],
                net_margin_pct=pnl["net_margin_pct"],
                capex=Decimal("0.00"),
                free_cash_flow=fcf,
                cash_balance=current_cash.quantize(Decimal("0.01")),
                burn_rate=pnl["burn_rate"]
            )
            monthly_statements.append(stmt)
            current_customers = active_cust

        milestones["capital_required_usd"] = peak_deficit.quantize(Decimal("0.01"))

        # Generate annual summaries
        annual_summaries = cls._aggregate_annuals(monthly_statements)
        return monthly_statements, annual_summaries, milestones

    @staticmethod
    def _aggregate_annuals(monthly: List[FinancialStatementMonthly]) -> List[FinancialStatementAnnual]:
        """Aggregate monthly projections into standard annual summaries."""
        annuals: List[FinancialStatementAnnual] = []
        total_months = len(monthly)
        total_years = (total_months + 11) // 12

        for y in range(1, total_years + 1):
            slice_start = (y - 1) * 12
            slice_end = min(total_months, y * 12)
            y_months = monthly[slice_start:slice_end]
            if not y_months:
                continue

            rev = sum(m.total_revenue for m in y_months)
            cogs = sum(m.cogs for m in y_months)
            gp = rev - cogs
            gm = ((gp / rev) * Decimal("100.0")).quantize(Decimal("0.1")) if rev > Decimal("0.0") else Decimal("0.0")
            opex = sum(m.total_opex for m in y_months)
            ebitda = sum(m.ebitda for m in y_months)
            ebit = sum(m.ebit for m in y_months)
            taxes = sum(m.tax_expense for m in y_months)
            net_inc = sum(m.net_income for m in y_months)
            nm = ((net_inc / rev) * Decimal("100.0")).quantize(Decimal("0.1")) if rev > Decimal("0.0") else Decimal("0.0")
            fcf = sum(m.free_cash_flow for m in y_months)
            end_cash = y_months[-1].cash_balance
            end_cust = y_months[-1].active_customers

            annuals.append(FinancialStatementAnnual(
                year=y,
                ending_customers=end_cust,
                total_revenue=rev.quantize(Decimal("0.01")),
                total_cogs=cogs.quantize(Decimal("0.01")),
                gross_profit=gp.quantize(Decimal("0.01")),
                gross_margin_pct=gm,
                total_opex=opex.quantize(Decimal("0.01")),
                ebitda=ebitda.quantize(Decimal("0.01")),
                ebit=ebit.quantize(Decimal("0.01")),
                total_taxes=taxes.quantize(Decimal("0.01")),
                net_income=net_inc.quantize(Decimal("0.01")),
                net_margin_pct=nm,
                free_cash_flow=fcf.quantize(Decimal("0.01")),
                ending_cash_balance=end_cash.quantize(Decimal("0.01"))
            ))

        return annuals
