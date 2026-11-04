from typing import Dict, Any, Optional
from decimal import Decimal, ROUND_HALF_UP


class CostEngine:
    """
    Granular COGS, OPEX, profitability, and unit-economics calculation engine.
    Adheres strictly to standard GAAP/SaaS income statement accounting rules.
    """

    # Upstream AI Provider Token Rates per Million (USD)
    AI_RATES_PER_MILLION = {
        "gemini-2.0-flash": {"input": Decimal("0.10"), "output": Decimal("0.40"), "cached": Decimal("0.025")},
        "gemini-1.5-flash": {"input": Decimal("0.075"), "output": Decimal("0.30"), "cached": Decimal("0.01875")},
        "gemini-1.5-pro": {"input": Decimal("1.25"), "output": Decimal("5.00"), "cached": Decimal("0.3125")},
        "openrouter-standard": {"input": Decimal("0.50"), "output": Decimal("1.50"), "cached": Decimal("0.10")},
    }

    # WhatsApp Business API per-conversation rates (USD) by regional market
    WHATSAPP_RATES_BY_COUNTRY = {
        "EG": Decimal("0.015"),   # Egypt: service conversation approx $0.015
        "SA": Decimal("0.032"),   # Saudi Arabia: approx $0.032
        "AE": Decimal("0.030"),   # UAE: approx $0.030
        "US": Decimal("0.015"),   # United States: approx $0.015
        "UK": Decimal("0.025"),   # United Kingdom: approx $0.025
        "EU": Decimal("0.028"),   # European Union: approx $0.028
        "DEFAULT": Decimal("0.020")
    }

    @classmethod
    def calculate_ai_token_cost(
        cls,
        input_tokens: int,
        output_tokens: int,
        cached_tokens: int = 0,
        model_name: str = "gemini-2.0-flash"
    ) -> Decimal:
        """Calculate token cost given exact prompt, completion, and cache stats."""
        rates = cls.AI_RATES_PER_MILLION.get(model_name, cls.AI_RATES_PER_MILLION["gemini-2.0-flash"])
        in_cost = (Decimal(input_tokens) / Decimal("1000000.0")) * rates["input"]
        out_cost = (Decimal(output_tokens) / Decimal("1000000.0")) * rates["output"]
        cache_cost = (Decimal(cached_tokens) / Decimal("1000000.0")) * rates["cached"]
        return (in_cost + out_cost + cache_cost).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)

    @classmethod
    def calculate_customer_cogs(
        cls,
        plan_revenue_monthly: Decimal,
        messages_count: int,
        country_code: str = "EG",
        ai_cost_per_1k_msgs: Decimal = Decimal("0.25"),
        payment_fee_pct: Decimal = Decimal("2.9"),
        payment_fee_fixed: Decimal = Decimal("0.30"),
        variable_infra_per_customer: Decimal = Decimal("0.50")
    ) -> Dict[str, Decimal]:
        """Calculate COGS breakdown for a single customer in a given month."""
        # 1. AI cost
        ai_cost = (Decimal(messages_count) / Decimal("1000.0")) * ai_cost_per_1k_msgs
        
        # 2. WhatsApp messaging conversation cost
        wa_rate = cls.WHATSAPP_RATES_BY_COUNTRY.get(country_code.upper(), cls.WHATSAPP_RATES_BY_COUNTRY["DEFAULT"])
        # Assume ~1 conversation per 15 customer messages
        conversations = Decimal(max(1, messages_count // 15))
        messaging_cost = conversations * wa_rate
        
        # 3. Payment Gateway fee (Stripe or regional equivalent)
        gateway_fee = Decimal("0.00")
        if plan_revenue_monthly > Decimal("0.00"):
            gateway_fee = (plan_revenue_monthly * (payment_fee_pct / Decimal("100.0"))) + payment_fee_fixed
            
        total_cogs = ai_cost + messaging_cost + gateway_fee + variable_infra_per_customer
        
        return {
            "ai_cost": ai_cost.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            "messaging_cost": messaging_cost.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            "payment_fee": gateway_fee.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            "variable_infra": variable_infra_per_customer.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            "total_cogs": total_cogs.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        }

    @staticmethod
    def calculate_statement_line_items(
        total_revenue: Decimal,
        total_cogs: Decimal,
        total_opex: Decimal,
        depreciation: Decimal = Decimal("0.00"),
        interest: Decimal = Decimal("0.00"),
        tax_rate_pct: Decimal = Decimal("22.5"),
        capex: Decimal = Decimal("0.00")
    ) -> Dict[str, Decimal]:
        """Compute full P&L and Free Cash Flow from top-line revenue down to cash."""
        gross_profit = total_revenue - total_cogs
        gross_margin_pct = Decimal("0.00")
        if total_revenue > Decimal("0.00"):
            gross_margin_pct = ((gross_profit / total_revenue) * Decimal("100.0")).quantize(Decimal("0.1"))

        ebitda = gross_profit - total_opex
        ebit = ebitda - depreciation
        
        # Taxes apply only on positive pre-tax earnings (EBIT - Interest)
        pre_tax_income = ebit - interest
        tax_expense = Decimal("0.00")
        if pre_tax_income > Decimal("0.00"):
            tax_expense = (pre_tax_income * (tax_rate_pct / Decimal("100.0"))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            
        net_income = pre_tax_income - tax_expense
        net_margin_pct = Decimal("0.00")
        if total_revenue > Decimal("0.00"):
            net_margin_pct = ((net_income / total_revenue) * Decimal("100.0")).quantize(Decimal("0.1"))

        # Unlevered Free Cash Flow (FCF) = Net Income + D&A - CapEx
        free_cash_flow = net_income + depreciation - capex
        burn_rate = Decimal("0.00")
        if free_cash_flow < Decimal("0.00"):
            burn_rate = abs(free_cash_flow)

        return {
            "gross_profit": gross_profit.quantize(Decimal("0.01")),
            "gross_margin_pct": gross_margin_pct,
            "ebitda": ebitda.quantize(Decimal("0.01")),
            "ebit": ebit.quantize(Decimal("0.01")),
            "tax_expense": tax_expense.quantize(Decimal("0.01")),
            "net_income": net_income.quantize(Decimal("0.01")),
            "net_margin_pct": net_margin_pct,
            "free_cash_flow": free_cash_flow.quantize(Decimal("0.01")),
            "burn_rate": burn_rate.quantize(Decimal("0.01")),
        }

    @staticmethod
    def calculate_breakeven_metrics(
        arpu: Decimal,
        cogs_per_customer: Decimal,
        fixed_opex_monthly: Decimal,
        tax_rate_pct: Decimal = Decimal("22.5")
    ) -> Dict[str, Any]:
        """
        Calculate break-even customer count and targets for $10k, $100k, and $1M net profit.
        Contribution Margin = ARPU - COGS.
        """
        contribution_margin = arpu - cogs_per_customer
        if contribution_margin <= Decimal("0.00"):
            return {
                "contribution_margin_per_customer": contribution_margin.quantize(Decimal("0.01")),
                "breakeven_customers": 0,
                "breakeven_monthly_revenue": Decimal("0.00"),
                "customers_for_10k": 0,
                "customers_for_100k": 0,
                "customers_for_1m": 0,
            }

        # Break-even: Fixed OPEX / CM
        be_cust = int((fixed_opex_monthly / contribution_margin).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        be_rev = Decimal(be_cust) * arpu

        # Pre-tax required for target net profit: Target / (1 - Tax Rate)
        tax_mult = Decimal("1.0") - (tax_rate_pct / Decimal("100.0"))
        if tax_mult <= Decimal("0.0"):
            tax_mult = Decimal("1.0")

        def calc_target_customers(target_net: Decimal) -> int:
            pre_tax = target_net / tax_mult
            required_cm = fixed_opex_monthly + pre_tax
            return int((required_cm / contribution_margin).quantize(Decimal("1"), rounding=ROUND_HALF_UP))

        return {
            "contribution_margin_per_customer": contribution_margin.quantize(Decimal("0.01")),
            "breakeven_customers": be_cust,
            "breakeven_monthly_revenue": be_rev.quantize(Decimal("0.01")),
            "customers_for_10k": calc_target_customers(Decimal("10000.0")),
            "customers_for_100k": calc_target_customers(Decimal("100000.0")),
            "customers_for_1m": calc_target_customers(Decimal("1000000.0")),
        }
