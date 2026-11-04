import React from 'react';
import { Target, Calculator, CheckCircle2, ArrowRight } from 'lucide-react';

export default function UnitEconomicsCard({ unitEcon }) {
  if (!unitEcon) return null;

  const formatCurrency = (val) =>
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 2 }).format(val);

  const ltvCac = parseFloat(unitEcon.ltv_cac_ratio || 0);

  return (
    <div className="bg-[#0b1022]/80 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-xl mb-6">
      <div className="flex items-center justify-between mb-5">
        <div>
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <Calculator className="w-5 h-5 text-emerald-400" /> Granular Unit Economics & Target Milestones
          </h3>
          <p className="text-xs text-slate-400">
            Per-tenant margin architecture, payback velocity, and customer scale required for profitability.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-[#0f172a]/70 border border-white/5 p-4 rounded-xl">
          <div className="text-xs text-slate-400 mb-1">Blended ARPU (Monthly)</div>
          <div className="text-xl font-bold text-white">{formatCurrency(unitEcon.arpu_monthly || 0)}</div>
          <div className="text-[11px] text-slate-500 mt-1">Average monthly contract value</div>
        </div>

        <div className="bg-[#0f172a]/70 border border-white/5 p-4 rounded-xl">
          <div className="text-xs text-slate-400 mb-1">Monthly COGS / Customer</div>
          <div className="text-xl font-bold text-rose-300">{formatCurrency(unitEcon.cogs_per_customer_monthly || 0)}</div>
          <div className="text-[11px] text-slate-500 mt-1">
            AI: {formatCurrency(unitEcon.ai_cost_per_customer || 0)} | WA: {formatCurrency(unitEcon.messaging_cost_per_customer || 0)}
          </div>
        </div>

        <div className="bg-[#0f172a]/70 border border-white/5 p-4 rounded-xl">
          <div className="text-xs text-slate-400 mb-1">Contribution Margin</div>
          <div className="text-xl font-bold text-emerald-400">
            {formatCurrency(unitEcon.contribution_margin_per_customer || 0)} <span className="text-xs font-normal text-slate-400">({unitEcon.contribution_margin_pct}%)</span>
          </div>
          <div className="text-[11px] text-slate-500 mt-1">Net gross dollar per customer</div>
        </div>

        <div className="bg-[#0f172a]/70 border border-white/5 p-4 rounded-xl">
          <div className="text-xs text-slate-400 mb-1">LTV / CAC Ratio</div>
          <div className="text-xl font-bold text-sky-400">
            {ltvCac.toFixed(1)}x
          </div>
          <div className="text-[11px] text-slate-500 mt-1">
            Payback: <strong className="text-slate-300">{unitEcon.cac_payback_months} mos</strong> | CAC: {formatCurrency(unitEcon.cac || 0)}
          </div>
        </div>
      </div>

      {/* Required Scale Milestones */}
      <div className="border-t border-white/10 pt-4">
        <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-1.5">
          <Target className="w-4 h-4 text-sky-400" /> Customer Scale Targets to Monthly Net Profit
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          <div className="p-3 rounded-lg bg-sky-950/30 border border-sky-800/40 flex items-center justify-between">
            <div>
              <div className="text-xs text-slate-400">Break-Even (0 Profit)</div>
              <div className="text-lg font-bold text-white">{unitEcon.breakeven_customers} tenants</div>
            </div>
            <CheckCircle2 className="w-5 h-5 text-sky-400" />
          </div>

          <div className="p-3 rounded-lg bg-emerald-950/30 border border-emerald-800/40 flex items-center justify-between">
            <div>
              <div className="text-xs text-slate-400">$10,000 / mo Profit</div>
              <div className="text-lg font-bold text-emerald-300">{unitEcon.customers_for_10k_net_profit} tenants</div>
            </div>
            <ArrowRight className="w-4 h-4 text-emerald-400" />
          </div>

          <div className="p-3 rounded-lg bg-indigo-950/30 border border-indigo-800/40 flex items-center justify-between">
            <div>
              <div className="text-xs text-slate-400">$100,000 / mo Profit</div>
              <div className="text-lg font-bold text-indigo-300">{unitEcon.customers_for_100k_net_profit} tenants</div>
            </div>
            <ArrowRight className="w-4 h-4 text-indigo-400" />
          </div>

          <div className="p-3 rounded-lg bg-amber-950/30 border border-amber-800/40 flex items-center justify-between">
            <div>
              <div className="text-xs text-slate-400">$1,000,000 / mo Profit</div>
              <div className="text-lg font-bold text-amber-300">{unitEcon.customers_for_1m_net_profit} tenants</div>
            </div>
            <ArrowRight className="w-4 h-4 text-amber-400" />
          </div>
        </div>
      </div>
    </div>
  );
}
