import React from 'react';
import { Globe, ExternalLink, ShieldCheck } from 'lucide-react';

export default function RegionalMarketTable({ regions }) {
  if (!regions || regions.length === 0) return null;

  const formatCurrency = (val) =>
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);

  return (
    <div className="bg-[#0b1022]/80 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-xl mb-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <Globe className="w-5 h-5 text-sky-400" /> Sourced Global Market Opportunity (TAM / SAM / SOM)
          </h3>
          <p className="text-xs text-slate-400">
            Bottom-up market sizing across primary launch and expansion jurisdictions with verified citations.
          </p>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm text-slate-300">
          <thead className="bg-[#0f172a]/60 text-xs text-slate-400 uppercase tracking-wider border-b border-white/10">
            <tr>
              <th className="py-3 px-3">Jurisdiction</th>
              <th className="py-3 px-3">Addressable Base</th>
              <th className="py-3 px-3">Serviceable (SAM)</th>
              <th className="py-3 px-3">Target SOM %</th>
              <th className="py-3 px-3">Total Market (TAM)</th>
              <th className="py-3 px-3">Serviceable (SAM)</th>
              <th className="py-3 px-3 text-right">SOM Annual ARR</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {regions.map((r, idx) => (
              <tr key={idx} className="hover:bg-white/[0.02] transition-colors">
                <td className="py-3 px-3">
                  <div className="font-semibold text-white flex items-center gap-1.5">
                    {r.country} <span className="text-[10px] text-slate-500 font-normal">({r.currency})</span>
                  </div>
                  <div className="text-[11px] text-slate-400 mt-0.5 flex items-center gap-1">
                    <ShieldCheck className="w-3 h-3 text-emerald-400" />
                    <span className="truncate max-w-[280px]" title={r.source_citation}>{r.source_citation}</span>
                  </div>
                </td>
                <td className="py-3 px-3 font-medium text-slate-200">
                  {r.addressable_merchants.toLocaleString()}
                </td>
                <td className="py-3 px-3 text-slate-300">
                  {r.serviceable_pct}%
                </td>
                <td className="py-3 px-3 text-sky-400 font-semibold">
                  {r.target_market_share_som_pct}%
                </td>
                <td className="py-3 px-3 text-slate-300">
                  {formatCurrency(r.tam_usd)}
                </td>
                <td className="py-3 px-3 text-slate-200 font-medium">
                  {formatCurrency(r.sam_usd)}
                </td>
                <td className="py-3 px-3 text-right font-bold text-emerald-400">
                  {formatCurrency(r.som_annual_usd)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
