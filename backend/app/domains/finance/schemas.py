from typing import List, Dict, Any, Optional
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field
from .parameters import FinancialParameter, SourceType


class FinancialStatementMonthly(BaseModel):
    """
    Standard GAAP/SaaS monthly income statement & cash flow line items.
    Enforces strict mathematical separation between revenue, margins, and cash.
    """
    month: int
    active_customers: int
    new_customers: int
    churned_customers: int
    
    # Revenue lines
    subscription_revenue: Decimal
    usage_revenue: Decimal
    total_revenue: Decimal
    
    # Cost lines
    cogs: Decimal  # Cost of Goods Sold (AI, messaging, hosting variable, payment fees)
    gross_profit: Decimal  # Total Revenue - COGS
    gross_margin_pct: Decimal  # (Gross Profit / Total Revenue) * 100
    
    # Operating Expenses (OPEX)
    rd_expense: Decimal
    sm_expense: Decimal
    ga_expense: Decimal
    total_opex: Decimal
    
    # Profitability tiers
    ebitda: Decimal  # Gross Profit - Total OPEX
    depreciation_amortization: Decimal
    ebit: Decimal  # EBITDA - D&A (Operating Profit)
    interest_expense: Decimal
    tax_expense: Decimal
    net_income: Decimal  # EBIT - Interest - Taxes (Net Profit)
    net_margin_pct: Decimal
    
    # Cash flow & Balance
    capex: Decimal
    free_cash_flow: Decimal  # Net Income + D&A - CapEx (simplified un-levered)
    cash_balance: Decimal
    burn_rate: Decimal  # Positive burn if net cash outflow


class FinancialStatementAnnual(BaseModel):
    """Annual aggregated summary of financials."""
    year: int
    ending_customers: int
    total_revenue: Decimal
    total_cogs: Decimal
    gross_profit: Decimal
    gross_margin_pct: Decimal
    total_opex: Decimal
    ebitda: Decimal
    ebit: Decimal
    total_taxes: Decimal
    net_income: Decimal
    net_margin_pct: Decimal
    free_cash_flow: Decimal
    ending_cash_balance: Decimal


class UnitEconomicsBreakdown(BaseModel):
    """Granular per-customer and per-message microeconomics."""
    arpu_monthly: Decimal
    cogs_per_customer_monthly: Decimal
    ai_cost_per_customer: Decimal
    messaging_cost_per_customer: Decimal
    payment_fee_per_customer: Decimal
    contribution_margin_per_customer: Decimal
    contribution_margin_pct: Decimal
    cac: Decimal
    ltv: Decimal
    ltv_cac_ratio: Decimal
    cac_payback_months: Decimal
    breakeven_customers: int
    breakeven_monthly_revenue: Decimal
    customers_for_10k_net_profit: int
    customers_for_100k_net_profit: int
    customers_for_1m_net_profit: int


class ValuationMethodResult(BaseModel):
    """Valuation result for a specific methodology with assumption transparency."""
    method_name: str
    enterprise_value: Decimal
    equity_value: Decimal
    multiple_or_discount_rate: Decimal
    is_applicable: bool = True
    inapplicable_reason: Optional[str] = None
    source_type: SourceType = SourceType.ILLUSTRATIVE_DEFAULT
    methodology_notes: str
    parameters: Dict[str, FinancialParameter] = Field(default_factory=dict)


class ValuationSummary(BaseModel):
    """Independent 5-method valuation analysis with EV and Equity values."""
    arr_multiple_valuation: ValuationMethodResult
    revenue_multiple_valuation: ValuationMethodResult
    ebitda_multiple_valuation: ValuationMethodResult
    dcf_valuation: ValuationMethodResult
    comparable_company_valuation: ValuationMethodResult
    defensible_range_low: Decimal
    defensible_range_high: Decimal
    currency: str = "USD"
    disclaimer: str = "Valuations are illustrative financial models and do not constitute certified fairness opinions or transaction offerings."


class MarketOpportunityRegion(BaseModel):
    """Regional international market TAM / SAM / SOM with citations."""
    country: str
    currency: str
    addressable_merchants: int
    serviceable_pct: Decimal
    target_market_share_som_pct: Decimal
    local_annual_arpu_usd: Decimal
    local_cac_usd: Decimal
    tam_usd: Decimal
    sam_usd: Decimal
    som_annual_usd: Decimal
    source_citation: str
    source_type: SourceType = SourceType.VERIFIED_EXTERNAL
    notes: Optional[str] = None


class ScenarioSimulationConfig(BaseModel):
    """User-editable scenario assumptions."""
    scenario_name: str = "Base Case"
    starting_customers: int = 25
    monthly_growth_rate_pct: Decimal = Decimal("15.0")
    monthly_churn_rate_pct: Decimal = Decimal("3.5")
    average_monthly_plan_usd: Decimal = Decimal("79.0")
    messages_per_customer_monthly: int = 3000
    ai_cost_per_1k_messages: Decimal = Decimal("0.25")
    whatsapp_cost_per_conversation: Decimal = Decimal("0.02")
    payment_gateway_pct: Decimal = Decimal("2.9")
    payment_gateway_fixed_usd: Decimal = Decimal("0.30")
    fixed_opex_monthly_usd: Decimal = Decimal("5000.0")
    starting_cash_balance_usd: Decimal = Decimal("25000.0")
    annual_tax_rate_pct: Decimal = Decimal("22.5")
    blended_cac_usd: Decimal = Decimal("65.0")


class FinancialOverviewResponse(BaseModel):
    """Comprehensive executive dashboard payload."""
    current_actual_mrr: Decimal
    current_actual_arr: Decimal
    current_paying_customers: int
    current_gross_margin_pct: Decimal
    current_monthly_burn: Decimal
    current_runway_months: Decimal
    unit_economics: UnitEconomicsBreakdown
    projections_36_months: List[FinancialStatementMonthly]
    annual_summaries: List[FinancialStatementAnnual]
    valuation: ValuationSummary
    regional_opportunities: List[MarketOpportunityRegion]
    parameters: Dict[str, FinancialParameter]
