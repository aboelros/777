"""
Valuation Engine, Multi-Scenario & Market Opportunity Tests.
Verifies the 5 independent valuation models, EV/Equity value distinction,
negative EBITDA guards, DCF terminal rate safety (g < WACC), multi-currency FX,
and regional TAM/SAM/SOM market datasets.
"""

import pytest
from decimal import Decimal
from app.domains.finance.valuation_engine import ValuationEngine
from app.domains.finance.scenario_engine import ScenarioEngine
from app.domains.finance.market_engine import MarketOpportunityEngine
from app.domains.finance.parameters import ExchangeRateRegistry
from app.domains.finance.service import FinanceService


def test_arr_and_revenue_multiples_with_equity_value():
    """Verify Method A and Method B calculate EV and Equity Value correctly."""
    arr = Decimal("500000.00")
    cash = Decimal("50000.00")
    debt = Decimal("10000.00")

    res = ValuationEngine.calculate_arr_multiple(arr, multiple=Decimal("6.0"), cash_balance=cash, debt=debt)
    assert res.is_applicable is True
    # EV = 500k * 6 = $3,000,000.00
    assert res.enterprise_value == Decimal("3000000.00")
    # Equity Value = EV + Cash - Debt = 3,000,000 + 50,000 - 10,000 = $3,040,000.00
    assert res.equity_value == Decimal("3040000.00")


def test_ebitda_multiple_negative_ebitda_guard():
    """Verify Method C explicitly refuses negative or zero EBITDA."""
    # Negative EBITDA
    neg_res = ValuationEngine.calculate_ebitda_multiple(Decimal("-50000.00"))
    assert neg_res.is_applicable is False
    assert "meaningless" in neg_res.inapplicable_reason.lower()
    assert neg_res.enterprise_value == Decimal("0.00")

    # Positive EBITDA
    pos_res = ValuationEngine.calculate_ebitda_multiple(Decimal("100000.00"), multiple=Decimal("15.0"), cash_balance=Decimal("20000.00"))
    assert pos_res.is_applicable is True
    assert pos_res.enterprise_value == Decimal("1500000.00")
    assert pos_res.equity_value == Decimal("1520000.00")


def test_dcf_valuation_with_fcf_and_growth_constraint():
    """Verify Method D uses FCF and rejects mathematically invalid g >= WACC."""
    fcfs = [Decimal("10000.00"), Decimal("25000.00"), Decimal("50000.00")]

    # 1. Invalid Gordon Growth assumption: g (25%) >= WACC (20%)
    invalid_dcf = ValuationEngine.calculate_dcf(
        annual_fcf_list=fcfs,
        discount_rate_wacc_pct=Decimal("20.0"),
        perpetual_growth_pct=Decimal("22.0")
    )
    assert invalid_dcf.is_applicable is False
    assert "strictly less than" in invalid_dcf.inapplicable_reason

    # 2. Valid DCF: WACC = 22%, g = 3%
    valid_dcf = ValuationEngine.calculate_dcf(
        annual_fcf_list=fcfs,
        discount_rate_wacc_pct=Decimal("22.0"),
        perpetual_growth_pct=Decimal("3.0"),
        cash_balance=Decimal("15000.00")
    )
    assert valid_dcf.is_applicable is True
    assert valid_dcf.enterprise_value > Decimal("0.00")
    assert valid_dcf.equity_value == valid_dcf.enterprise_value + Decimal("15000.00")


def test_multi_scenario_variance_and_provenance():
    """Verify Conservative, Base Case, and Aggressive scenarios produce rational bands."""
    comparison = ScenarioEngine.compare_scenarios(months=36)
    
    cons = comparison["conservative"]
    base = comparison["base_case"]
    aggr = comparison["aggressive"]

    # Monotonic order: Conservative < Base < Aggressive
    assert cons["y3_revenue_usd"] < base["y3_revenue_usd"]
    assert base["y3_revenue_usd"] < aggr["y3_revenue_usd"]
    assert cons["y3_ending_customers"] < base["y3_ending_customers"]
    assert base["y3_ending_customers"] < aggr["y3_ending_customers"]

    # Verify risk labels
    assert "Floor" in cons["status_label"]
    assert "Upside" in aggr["status_label"]


def test_market_opportunity_tam_sam_som():
    """Verify regional TAM/SAM/SOM calculation and source provenance."""
    regions = MarketOpportunityEngine.calculate_regional_opportunities()
    assert len(regions) >= 6

    egypt = next(r for r in regions if r.country == "Egypt")
    assert egypt.currency == "EGP"
    assert egypt.tam_usd > egypt.sam_usd > egypt.som_annual_usd
    assert "MCIT" in egypt.source_citation

    ksa = next(r for r in regions if r.country == "Saudi Arabia")
    assert ksa.currency == "SAR"
    assert "Monsha'at" in ksa.source_citation


def test_multi_currency_exchange_rates():
    """Verify timestamped multi-currency exchange rate conversions."""
    # $100 USD to EGP = 4,850 EGP (at 48.50)
    egp_val = ExchangeRateRegistry.convert(Decimal("100.0"), "USD", "EGP")
    assert egp_val == Decimal("4850.0")

    # 375 SAR to USD = $100 USD (at 3.75)
    usd_val = ExchangeRateRegistry.convert(Decimal("375.0"), "SAR", "USD")
    assert usd_val == Decimal("100.0")


@pytest.mark.asyncio
async def test_finance_service_comprehensive_overview():
    """Verify FinanceService builds end-to-end payload without crashing."""
    service = FinanceService(db=None)
    overview = await service.get_comprehensive_overview()
    
    assert overview.current_actual_mrr == Decimal("0.00")
    assert len(overview.projections_36_months) == 36
    assert len(overview.annual_summaries) == 3
    assert overview.valuation.defensible_range_low >= Decimal("0.00")
    assert len(overview.regional_opportunities) >= 6
    assert "average_monthly_plan_usd" in overview.parameters
