import React from 'react';
import { TrendingUp, Users, DollarSign, ShieldAlert, Award, Clock } from 'lucide-react';

export default function ExecutiveOverviewCards({ overview }) {
  if (!overview) return null;

  const actualMrr = parseFloat(overview.current_actual_mrr || 0);
  const actualArr = parseFloat(overview.current_actual_arr || 0);
  const customers = overview.current_paying_customers || 0;
  const grossMargin = parseFloat(overview.current_gross_margin_pct || 0);
  const burn = parseFloat(overview.current_monthly_burn || 0);
  const runway = parseFloat(overview.current_runway_months || 0);
  
  const valLow = parseFloat(overview.valuation?.defensible_range_low || 0);
  const valHigh = parseFloat(overview.valuation?.defensible_range_high || 0);

  const formatCurrency = (val) =>
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {/* MRR & ARR Card */}
      <div className="bg-[#0b1022]/80 backdrop-blur-xl border border-white/10 rounded-2xl p-5 shadow-lg relative overflow-hidden group hover:border-sky-500/40 transition-all">
        <div className="flex items-center justify-between mb-3">
          <span className="text-xs font-semibold text-slate-400 tracking-wider uppercase">Recurring Revenue</span>
          <div className="w-8 h-8 rounded-lg bg-sky-500/10 flex items-center justify-center text-sky-400">
            <DollarSign className="w-4 h-4" />
          </div>
        </div>
        <div className="text-2xl font-bold text-white mb-1">
          {actualMrr > 0 ? formatCurrency(actualMrr) : '$0'} <span className="text-xs text-slate-400 font-normal">/mo</span>
        </div>
        <div className="flex items-center justify-between text-xs text-slate-400">
          <span>ARR: <strong className="text-slate-200">{formatCurrency(actualArr)}</strong></span>
          <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px]">
            {actualMrr > 0 ? 'Live Actual' : 'Pre-revenue'}
          </span>
        </div>
      </div>

      {/* Customer Scale & Break-Even Card */}
      <div className="bg-[#0b1022]/80 backdrop-blur-xl border border-white/10 rounded-2xl p-5 shadow-lg relative overflow-hidden group hover:border-sky-500/40 transition-all">
        <div className="flex items-center justify-between mb-3">
          <span className="text-xs font-semibold text-slate-400 tracking-wider uppercase">Customer Scale</span>
          <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center text-blue-400">
            <Users className="w-4 h-4" />
          </div>
        </div>
        <div className="text-2xl font-bold text-white mb-1">
          {customers} <span className="text-xs text-slate-400 font-normal">paying tenants</span>
        </div>
        <div className="flex items-center justify-between text-xs text-slate-400">
          <span>Break-even: <strong className="text-slate-200">{overview.unit_economics?.breakeven_customers || 0}</strong></span>
          <span className="text-[10px] text-sky-400 font-medium">Target</span>
        </div>
      </div>

      {/* Profitability & Burn Card */}
      <div className="bg-[#0b1022]/80 backdrop-blur-xl border border-white/10 rounded-2xl p-5 shadow-lg relative overflow-hidden group hover:border-sky-500/40 transition-all">
        <div className="flex items-center justify-between mb-3">
          <span className="text-xs font-semibold text-slate-400 tracking-wider uppercase">Unit Margins</span>
          <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-400">
            <TrendingUp className="w-4 h-4" />
          </div>
        </div>
        <div className="text-2xl font-bold text-white mb-1">
          {grossMargin.toFixed(1)}% <span className="text-xs text-slate-400 font-normal">gross margin</span>
        </div>
        <div className="flex items-center justify-between text-xs text-slate-400">
          <span>Net Burn: <strong className="text-rose-400">{formatCurrency(burn)}</strong></span>
          <span className="text-[10px] text-slate-300 font-medium">{runway > 120 ? '> 10Y Runway' : `${runway.toFixed(1)} Mo Runway`}</span>
        </div>
      </div>

      {/* Company Valuation Band Card */}
      <div className="bg-[#0b1022]/80 backdrop-blur-xl border border-white/10 rounded-2xl p-5 shadow-lg relative overflow-hidden group hover:border-amber-500/40 transition-all">
        <div className="flex items-center justify-between mb-3">
          <span className="text-xs font-semibold text-slate-400 tracking-wider uppercase">Defensible Valuation</span>
          <div className="w-8 h-8 rounded-lg bg-amber-500/10 flex items-center justify-center text-amber-400">
            <Award className="w-4 h-4" />
          </div>
        </div>
        <div className="text-xl font-bold text-amber-300 mb-1">
          {formatCurrency(valLow)} – {formatCurrency(valHigh)}
        </div>
        <div className="flex items-center justify-between text-xs text-slate-400">
          <span>Method: <strong>ARR & DCF Band</strong></span>
          <span className="px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-300 border border-amber-500/20 text-[10px]">
            Illustrative
          </span>
        </div>
      </div>
    </div>
  );
}
