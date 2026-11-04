import React from 'react';
import { Award, AlertCircle, Info, Landmark } from 'lucide-react';

export default function ValuationBreakdown({ valuation }) {
  if (!valuation) return null;

  const formatCurrency = (val) =>
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);

  const methods = [
    valuation.arr_multiple_valuation,
    valuation.revenue_multiple_valuation,
    valuation.ebitda_multiple_valuation,
    valuation.dcf_valuation,
    valuation.comparable_company_valuation,
  ].filter(Boolean);

  return (
    <div className="bg-[#0b1022]/80 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-xl mb-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <Award className="w-5 h-5 text-amber-400" /> Multi-Methodology Company Valuation Engine
          </h3>
          <p className="text-xs text-slate-400">
            5 independent valuation models distinguishing Enterprise Value (EV) from Equity Value.
          </p>
        </div>
        <div className="text-right">
          <div className="text-xs text-slate-400">Defensible Range (Seed / A)</div>
          <div className="text-lg font-bold text-amber-300">
            {formatCurrency(valuation.defensible_range_low)} – {formatCurrency(valuation.defensible_range_high)}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
        {methods.map((m, idx) => (
          <div
            key={idx}
            className={`p-4 rounded-xl border transition-all ${
              m.is_applicable
                ? 'bg-[#0f172a]/70 border-white/10 hover:border-amber-500/40'
                : 'bg-rose-950/10 border-rose-900/30'
            }`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold text-slate-300">{m.method_name}</span>
              <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-white/5 text-amber-300 border border-white/10">
                {m.multiple_or_discount_rate}x / %
              </span>
            </div>

            {m.is_applicable ? (
              <>
                <div className="mb-2">
                  <div className="text-xs text-slate-400">Enterprise Value (EV)</div>
                  <div className="text-xl font-bold text-white">{formatCurrency(m.enterprise_value)}</div>
                </div>
                <div className="pt-2 border-t border-white/5 flex items-center justify-between text-xs">
                  <span className="text-slate-400">Equity Value:</span>
                  <span className="font-semibold text-emerald-400">{formatCurrency(m.equity_value)}</span>
                </div>
              </>
            ) : (
              <div className="py-2">
                <div className="text-xs text-rose-300 font-medium flex items-center gap-1.5 mb-1">
                  <AlertCircle className="w-4 h-4 text-rose-400" /> Inapplicable Model
                </div>
                <div className="text-[11px] text-slate-400 leading-relaxed">{m.inapplicable_reason}</div>
              </div>
            )}

            <div className="text-[11px] text-slate-500 mt-3 pt-2 border-t border-white/5 leading-snug">
              {m.methodology_notes}
            </div>
          </div>
        ))}
      </div>

      <div className="bg-amber-500/5 border border-amber-500/20 rounded-xl p-3 flex items-start gap-2.5 text-xs text-amber-200/80">
        <Info className="w-4 h-4 text-amber-400 mt-0.5 flex-shrink-0" />
        <div>
          <strong>Valuation Provenance Notice:</strong> {valuation.disclaimer} Each method operates independently and reflects different risk-adjusted capital structures.
        </div>
      </div>
    </div>
  );
}
