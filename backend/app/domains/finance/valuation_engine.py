from typing import Dict, Any, List, Optional
from decimal import Decimal, ROUND_HALF_UP

from .schemas import ValuationMethodResult, ValuationSummary
from .parameters import FinancialParameter, SourceType


class ValuationEngine:
    """
    Independent 5-method company valuation engine.
    Calculates Enterprise Value (EV) and Equity Value without conflating models.
    """

    @classmethod
    def calculate_arr_multiple(
        cls,
        arr_usd: Decimal,
        multiple: Decimal = Decimal("6.5"),
        cash_balance: Decimal = Decimal("25000.00"),
        debt: Decimal = Decimal("0.00")
    ) -> ValuationMethodResult:
        """Method A: ARR Multiple valuation with EV to Equity Value conversion."""
        ev = (arr_usd * multiple).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        eq = (ev + cash_balance - debt).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        
        return ValuationMethodResult(
            method_name="ARR Multiple (Forward 12M)",
            enterprise_value=ev,
            equity_value=eq,
            multiple_or_discount_rate=multiple,
            is_applicable=True,
            source_type=SourceType.ILLUSTRATIVE_DEFAULT,
            methodology_notes="Standard early-stage B2B SaaS multiple (range: 4.0x - 10.0x ARR). Adjusted for AI margin profile."
        )

    @classmethod
    def calculate_revenue_multiple(
        cls,
        annual_revenue_usd: Decimal,
        multiple: Decimal = Decimal("5.5"),
        cash_balance: Decimal = Decimal("25000.00"),
        debt: Decimal = Decimal("0.00")
    ) -> ValuationMethodResult:
        """Method B: LTM / NTM Top-line Revenue Multiple."""
        ev = (annual_revenue_usd * multiple).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        eq = (ev + cash_balance - debt).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        
        return ValuationMethodResult(
            method_name="Revenue Multiple (LTM)",
            enterprise_value=ev,
            equity_value=eq,
            multiple_or_discount_rate=multiple,
            is_applicable=True,
            source_type=SourceType.ILLUSTRATIVE_DEFAULT,
            methodology_notes="Multiplied against trailing or projected 12-month gross revenue."
        )

    @classmethod
    def calculate_ebitda_multiple(
        cls,
        annual_ebitda_usd: Decimal,
        multiple: Decimal = Decimal("15.0"),
        cash_balance: Decimal = Decimal("25000.00"),
        debt: Decimal = Decimal("0.00")
    ) -> ValuationMethodResult:
        """Method C: EBITDA Multiple. Inapplicable if EBITDA <= 0."""
        if annual_ebitda_usd <= Decimal("0.00"):
            return ValuationMethodResult(
                method_name="EBITDA Multiple",
                enterprise_value=Decimal("0.00"),
                equity_value=Decimal("0.00"),
                multiple_or_discount_rate=multiple,
                is_applicable=False,
                inapplicable_reason="EBITDA is zero or negative during early-stage scaling. Earnings multiples are economically meaningless for pre-profit ventures.",
                source_type=SourceType.ILLUSTRATIVE_DEFAULT,
                methodology_notes="Only applicable once business reaches sustained operational profitability."
            )

        ev = (annual_ebitda_usd * multiple).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        eq = (ev + cash_balance - debt).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        
        return ValuationMethodResult(
            method_name="EBITDA Multiple",
            enterprise_value=ev,
            equity_value=eq,
            multiple_or_discount_rate=multiple,
            is_applicable=True,
            source_type=SourceType.ILLUSTRATIVE_DEFAULT,
            methodology_notes="Applied to normalized positive annual EBITDA (typical range: 12.0x - 20.0x for high-growth tech)."
        )

    @classmethod
    def calculate_dcf(
        cls,
        annual_fcf_list: List[Decimal],
        discount_rate_wacc_pct: Decimal = Decimal("22.0"),
        perpetual_growth_pct: Decimal = Decimal("3.0"),
        cash_balance: Decimal = Decimal("25000.00"),
        debt: Decimal = Decimal("0.00")
    ) -> ValuationMethodResult:
        """
        Method D: Discounted Free Cash Flow (DCF).
        Strictly uses Free Cash Flow (not EBITDA) and validates g < WACC.
        """
        wacc = discount_rate_wacc_pct / Decimal("100.0")
        g = perpetual_growth_pct / Decimal("100.0")

        if g >= wacc:
            return ValuationMethodResult(
                method_name="Discounted Cash Flow (DCF)",
                enterprise_value=Decimal("0.00"),
                equity_value=Decimal("0.00"),
                multiple_or_discount_rate=discount_rate_wacc_pct,
                is_applicable=False,
                inapplicable_reason="Mathematical violation: perpetual growth rate (g) must be strictly less than discount rate (WACC).",
                source_type=SourceType.ILLUSTRATIVE_DEFAULT,
                methodology_notes="Gordon Growth formula requires WACC > g to prevent infinite valuation."
            )

        # 1. Discount explicit forecast period FCFs
        pv_fcfs = Decimal("0.00")
        for idx, fcf in enumerate(annual_fcf_list, start=1):
            discount_factor = (Decimal("1.0") + wacc) ** idx
            pv_fcfs += (fcf / discount_factor)

        # 2. Terminal Value based on last period FCF
        terminal_fcf = annual_fcf_list[-1] if annual_fcf_list else Decimal("0.00")
        # If terminal FCF is negative, terminal value cannot be reasonably computed
        if terminal_fcf <= Decimal("0.00"):
            ev = max(Decimal("0.00"), pv_fcfs).quantize(Decimal("0.01"))
            eq = (ev + cash_balance - debt).quantize(Decimal("0.01"))
            return ValuationMethodResult(
                method_name="Discounted Cash Flow (DCF)",
                enterprise_value=ev,
                equity_value=eq,
                multiple_or_discount_rate=discount_rate_wacc_pct,
                is_applicable=True,
                source_type=SourceType.ILLUSTRATIVE_DEFAULT,
                methodology_notes="Terminal FCF is negative; DCF reflects only discounted explicit cash flows."
            )

        tv = (terminal_fcf * (Decimal("1.0") + g)) / (wacc - g)
        t = len(annual_fcf_list)
        pv_tv = tv / ((Decimal("1.0") + wacc) ** t)

        ev = max(Decimal("0.00"), pv_fcfs + pv_tv).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        eq = (ev + cash_balance - debt).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return ValuationMethodResult(
            method_name="Discounted Cash Flow (DCF)",
            enterprise_value=ev,
            equity_value=eq,
            multiple_or_discount_rate=discount_rate_wacc_pct,
            is_applicable=True,
            source_type=SourceType.ILLUSTRATIVE_DEFAULT,
            methodology_notes=f"Unlevered DCF: WACC={discount_rate_wacc_pct}%, perpetual growth={perpetual_growth_pct}%, horizon={len(annual_fcf_list)}Y."
        )

    @classmethod
    def calculate_comparables(
        cls,
        arr_usd: Decimal,
        cash_balance: Decimal = Decimal("25000.00"),
        debt: Decimal = Decimal("0.00")
    ) -> ValuationMethodResult:
        """
        Method E: Comparable Company Analysis.
        Illustrative benchmarking against early-stage conversational AI & support platforms.
        """
        # Benchmark median multiple for comparable AI customer support seed/Series A is ~7.2x ARR
        peer_multiple = Decimal("7.2")
        ev = (arr_usd * peer_multiple).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        eq = (ev + cash_balance - debt).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return ValuationMethodResult(
            method_name="Comparable Peer Benchmark",
            enterprise_value=ev,
            equity_value=eq,
            multiple_or_discount_rate=peer_multiple,
            is_applicable=True,
            source_type=SourceType.ILLUSTRATIVE_DEFAULT,
            methodology_notes="Benchmarked against illustrative private peer transactions in AI conversational commerce (Gorgias, Ada, Chatfuel)."
        )

    @classmethod
    def build_valuation_summary(
        cls,
        arr_usd: Decimal,
        annual_revenue_usd: Decimal,
        annual_ebitda_usd: Decimal,
        annual_fcf_list: List[Decimal],
        cash_balance: Decimal = Decimal("25000.00")
    ) -> ValuationSummary:
        """Compute all 5 methods and compile defensible valuation range."""
        m_arr = cls.calculate_arr_multiple(arr_usd, cash_balance=cash_balance)
        m_rev = cls.calculate_revenue_multiple(annual_revenue_usd, cash_balance=cash_balance)
        m_ebitda = cls.calculate_ebitda_multiple(annual_ebitda_usd, cash_balance=cash_balance)
        m_dcf = cls.calculate_dcf(annual_fcf_list, cash_balance=cash_balance)
        m_comps = cls.calculate_comparables(arr_usd, cash_balance=cash_balance)

        # Defensible range: conservative ARR multiple (4.5x) to upper base multiple (7.5x)
        range_low = max(Decimal("0.00"), (arr_usd * Decimal("4.5") + cash_balance).quantize(Decimal("0.01")))
        range_high = max(Decimal("0.00"), (arr_usd * Decimal("8.0") + cash_balance).quantize(Decimal("0.01")))

        return ValuationSummary(
            arr_multiple_valuation=m_arr,
            revenue_multiple_valuation=m_rev,
            ebitda_multiple_valuation=m_ebitda,
            dcf_valuation=m_dcf,
            comparable_company_valuation=m_comps,
            defensible_range_low=range_low,
            defensible_range_high=range_high
        )
