import React from 'react';
import { Layers, ShieldCheck, Zap, AlertTriangle } from 'lucide-react';

export default function ScenarioComparisonTable({ scenarios }) {
  if (!scenarios) return null;

  const formatCurrency = (val) =>
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);

  const keys = ['conservative', 'base_case', 'aggressive'];

  const getBadge = (key) => {
    if (key === 'conservative') {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-slate-800 text-slate-300 border border-slate-700">
          <ShieldCheck className="w-3.5 h-3.5 text-slate-400" /> Conservative Floor
        </span>
      );
    }
    if (key === 'base_case') {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-sky-950/80 text-sky-300 border border-sky-800/60">
          <Layers className="w-3.5 h-3.5 text-sky-400" /> Target Plan (Base)
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-amber-950/80 text-amber-300 border border-amber-800/60">
        <Zap className="w-3.5 h-3.5 text-amber-400" /> High Upside (Aggressive)
      </span>
    );
  };

  return (
    <div className="bg-[#0b1022]/80 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-xl mb-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <Layers className="w-5 h-5 text-sky-400" /> Strategic Scenario Simulation Matrix
          </h3>
          <p className="text-xs text-slate-400">
            Side-by-side comparison of 36-month growth trajectories, unit margins, and capital requirements.
          </p>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm text-slate-300">
          <thead className="bg-[#0f172a]/60 text-xs text-slate-400 uppercase tracking-wider border-b border-white/10">
            <tr>
              <th className="py-3 px-4">Financial Metric</th>
              {keys.map((k) => (
                <th key={k} className="py-3 px-4 text-center">
                  {getBadge(k)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            <tr>
              <td className="py-3 px-4 font-medium text-slate-300">Starting Paying Tenants</td>
              {keys.map((k) => (
                <td key={k} className="py-3 px-4 text-center font-semibold text-white">
                  {scenarios[k]?.starting_customers}
                </td>
              ))}
            </tr>
            <tr>
              <td className="py-3 px-4 font-medium text-slate-300">Year 1 Ending Customers</td>
              {keys.map((k) => (
                <td key={k} className="py-3 px-4 text-center text-slate-200">
                  {scenarios[k]?.y1_ending_customers}
                </td>
              ))}
            </tr>
            <tr>
              <td className="py-3 px-4 font-medium text-slate-300">Year 3 Ending Customers</td>
              {keys.map((k) => (
                <td key={k} className="py-3 px-4 text-center font-bold text-sky-400">
                  {scenarios[k]?.y3_ending_customers}
                </td>
              ))}
            </tr>
            <tr>
              <td className="py-3 px-4 font-medium text-slate-300">Year 1 Annual Run-rate (ARR)</td>
              {keys.map((k) => (
                <td key={k} className="py-3 px-4 text-center text-slate-200">
                  {formatCurrency(scenarios[k]?.y1_arr_usd || 0)}
                </td>
              ))}
            </tr>
            <tr className="bg-sky-500/5">
              <td className="py-3 px-4 font-medium text-white">Year 3 Annual Run-rate (ARR)</td>
              {keys.map((k) => (
                <td key={k} className="py-3 px-4 text-center font-bold text-emerald-400 text-base">
                  {formatCurrency(scenarios[k]?.y3_arr_usd || 0)}
                </td>
              ))}
            </tr>
            <tr>
              <td className="py-3 px-4 font-medium text-slate-300">Year 3 Gross Margin %</td>
              {keys.map((k) => (
                <td key={k} className="py-3 px-4 text-center text-slate-200">
                  {scenarios[k]?.y3_gross_margin_pct}%
                </td>
              ))}
            </tr>
            <tr>
              <td className="py-3 px-4 font-medium text-slate-300">Year 3 Annual Net Income</td>
              {keys.map((k) => (
                <td key={k} className="py-3 px-4 text-center font-semibold text-emerald-300">
                  {formatCurrency(scenarios[k]?.y3_net_income_usd || 0)}
                </td>
              ))}
            </tr>
            <tr>
              <td className="py-3 px-4 font-medium text-slate-300">Break-Even Milestone</td>
              {keys.map((k) => (
                <td key={k} className="py-3 px-4 text-center font-medium text-amber-300">
                  {scenarios[k]?.breakeven_month ? `Month ${scenarios[k].breakeven_month}` : 'Pending'}
                </td>
              ))}
            </tr>
            <tr>
              <td className="py-3 px-4 font-medium text-slate-300">Peak Capital Deficit (Cash Trough)</td>
              {keys.map((k) => (
                <td key={k} className="py-3 px-4 text-center font-medium text-rose-300">
                  {formatCurrency(scenarios[k]?.capital_required_usd || 0)}
                </td>
              ))}
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
