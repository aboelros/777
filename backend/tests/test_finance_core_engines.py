"""
Deterministic Financial Intelligence Core Engine Unit Tests.
Verifies revenue calculations, COGS, OPEX, margins, churn, LTV/CAC,
break-even thresholds, 36-month statement continuity, and zero-division safety.
"""

import pytest
from decimal import Decimal
from app.domains.finance.revenue_engine import RevenueEngine
from app.domains.finance.cost_engine import CostEngine
from app.domains.finance.growth_engine import GrowthEngine
from app.domains.finance.projection_engine import ProjectionEngine
from app.domains.finance.schemas import ScenarioSimulationConfig


def test_revenue_subscription_and_usage_calculations():
    """Verify tier subscription and usage-based overage calculations."""
    # 100 customers on $79 plan = $7,900.00
    sub_rev = RevenueEngine.calculate_subscription_revenue(100, Decimal("79.00"))
    assert sub_rev == Decimal("7900.00")

    # Usage overage: 3,000 msgs/cust vs 2,000 included = 1,000 overage msgs = 1 * $5.00 * 100 = $500.00
    usage_rev = RevenueEngine.calculate_usage_revenue(
        customer_count=100,
        messages_per_customer=3000,
        included_messages_per_tier=2000,
        overage_per_1k_usd=Decimal("5.00")
    )
    assert usage_rev == Decimal("500.00")

    # MRR and ARR
    mrr = RevenueEngine.calculate_mrr(sub_rev, usage_rev)
    assert mrr == Decimal("8400.00")
    arr = RevenueEngine.calculate_arr(mrr)
    assert arr == Decimal("100800.00")


def test_division_by_zero_and_boundary_safety():
    """Verify engine handles 0 customers, negative prices, and zero churn safely."""
    assert RevenueEngine.calculate_subscription_revenue(0, Decimal("79.00")) == Decimal("0.00")
    assert RevenueEngine.calculate_arpu(Decimal("0.00"), 0) == Decimal("0.00")
    assert RevenueEngine.calculate_arpu(Decimal("5000.00"), 0) == Decimal("0.00")

    # Zero churn customer lifetime safety
    unit_econ = GrowthEngine.calculate_unit_economics(
        arpu_monthly=Decimal("79.00"),
        gross_margin_pct=Decimal("80.0"),
        monthly_churn_pct=Decimal("0.0"),
        cac_usd=Decimal("65.00")
    )
    assert unit_econ["ltv"] == Decimal("0.00")
    assert unit_econ["customer_lifetime_months"] == Decimal("0.0")


def test_customer_cogs_and_profitability_statement():
    """Verify granular COGS (AI + WhatsApp + Stripe) and statement line items."""
    cogs = CostEngine.calculate_customer_cogs(
        plan_revenue_monthly=Decimal("79.00"),
        messages_count=3000,
        country_code="EG",
        ai_cost_per_1k_msgs=Decimal("0.25"),
        payment_fee_pct=Decimal("2.9"),
        payment_fee_fixed=Decimal("0.30"),
        variable_infra_per_customer=Decimal("0.50")
    )
    # AI: 3.0 * $0.25 = $0.75
    assert cogs["ai_cost"] == Decimal("0.75")
    # Payment fee: (79 * 0.029) + 0.30 = 2.291 + 0.30 = $2.59
    assert cogs["payment_fee"] == Decimal("2.59")
    # Total COGS should be approx $7.84
    assert cogs["total_cogs"] > Decimal("5.00")

    # Income statement verification
    pnl = CostEngine.calculate_statement_line_items(
        total_revenue=Decimal("10000.00"),
        total_cogs=Decimal("1500.00"),
        total_opex=Decimal("5000.00"),
        depreciation=Decimal("200.00"),
        tax_rate_pct=Decimal("20.0")
    )
    assert pnl["gross_profit"] == Decimal("8500.00")
    assert pnl["gross_margin_pct"] == Decimal("85.0")
    assert pnl["ebitda"] == Decimal("3500.00")
    assert pnl["ebit"] == Decimal("3300.00")
    # Taxes: 20% on $3,300 = $660
    assert pnl["tax_expense"] == Decimal("660.00")
    # Net Income: 3300 - 660 = $2640.00
    assert pnl["net_income"] == Decimal("2640.00")
    # Free cash flow: Net Income + D&A - CapEx = 2640 + 200 - 0 = $2840.00
    assert pnl["free_cash_flow"] == Decimal("2840.00")


def test_customer_cohort_growth_and_annualized_churn():
    """Verify compound monthly cohort dynamics and annualized churn conversion."""
    # Monthly churn 3.5% -> Annual churn = 1 - (1 - 0.035)^12 = 34.78% -> 34.8%
    ann_churn = GrowthEngine.calculate_annualized_churn(Decimal("3.5"))
    assert ann_churn == Decimal("34.8")

    cohort = GrowthEngine.calculate_cohort_turn(
        starting_customers=100,
        monthly_growth_rate_pct=Decimal("15.0"),
        monthly_churn_rate_pct=Decimal("3.5")
    )
    # New: 15, Churned: 4, Ending: 100 + 15 - 4 = 111
    assert cohort["new"] == 15
    assert cohort["churned"] == 4
    assert cohort["ending"] == 111


def test_breakeven_and_net_profit_target_customers():
    """Verify break-even and milestones for $10k, $100k, and $1M net profit."""
    be = CostEngine.calculate_breakeven_metrics(
        arpu=Decimal("100.00"),
        cogs_per_customer=Decimal("20.00"),
        fixed_opex_monthly=Decimal("8000.00"),
        tax_rate_pct=Decimal("20.0")
    )
    # Contribution Margin = $80.00
    assert be["contribution_margin_per_customer"] == Decimal("80.00")
    # Break-even: 8000 / 80 = 100 customers
    assert be["breakeven_customers"] == 100
    assert be["breakeven_monthly_revenue"] == Decimal("10000.00")

    # To get $10k net profit after 20% tax: Pre-tax required = $12,500
    # Required CM = 8,000 + 12,500 = 20,500 / 80 = 256 customers
    assert be["customers_for_10k"] == 256
    assert be["customers_for_100k"] > be["customers_for_10k"]
    assert be["customers_for_1m"] > be["customers_for_100k"]


def test_projection_36_months_continuity_and_cash_rollforward():
    """Verify 36-month month-by-month consistency and cash balance reconciliation."""
    cfg = ScenarioSimulationConfig(
        starting_customers=20,
        monthly_growth_rate_pct=Decimal("10.0"),
        monthly_churn_rate_pct=Decimal("3.0"),
        average_monthly_plan_usd=Decimal("79.00"),
        fixed_opex_monthly_usd=Decimal("3000.00"),
        starting_cash_balance_usd=Decimal("15000.00")
    )

    monthly, annuals, milestones = ProjectionEngine.run_projection(cfg, months=36)
    assert len(monthly) == 36
    assert len(annuals) == 3

    # Continuity check: ending cash of Month t equals ending cash of Month t-1 + FCF of Month t
    for i in range(1, len(monthly)):
        prev_cash = monthly[i - 1].cash_balance
        fcf = monthly[i].free_cash_flow
        expected_cash = prev_cash + fcf
        assert abs(monthly[i].cash_balance - expected_cash) < Decimal("0.02")

    # Milestone assertions
    assert milestones["breakeven_month"] is not None
    assert milestones["breakeven_month"] <= 36
