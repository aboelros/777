import React, { useState } from 'react';
import { Sliders, RefreshCw, Play, Sparkles } from 'lucide-react';

export default function InteractiveSimulator({ onSimulate, isLoading }) {
  const [params, setParams] = useState({
    scenario_name: 'Custom Interactive Forecast',
    starting_customers: 25,
    monthly_growth_rate_pct: 15.0,
    monthly_churn_rate_pct: 3.5,
    average_monthly_plan_usd: 79.0,
    messages_per_customer_monthly: 3500,
    fixed_opex_monthly_usd: 5000.0,
    starting_cash_balance_usd: 25000.0,
  });

  const handleChange = (field, val) => {
    setParams((prev) => ({ ...prev, [field]: parseFloat(val) }));
  };

  const handleRun = () => {
    if (onSimulate) onSimulate(params);
  };

  const handleReset = () => {
    const defaults = {
      scenario_name: 'Custom Interactive Forecast',
      starting_customers: 25,
      monthly_growth_rate_pct: 15.0,
      monthly_churn_rate_pct: 3.5,
      average_monthly_plan_usd: 79.0,
      messages_per_customer_monthly: 3500,
      fixed_opex_monthly_usd: 5000.0,
      starting_cash_balance_usd: 25000.0,
    };
    setParams(defaults);
    if (onSimulate) onSimulate(defaults);
  };

  return (
    <div className="bg-[#0b1022]/80 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-xl mb-6">
      <div className="flex items-center justify-between mb-5">
        <div>
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <Sliders className="w-5 h-5 text-sky-400" /> Interactive Financial Scenario Simulator
          </h3>
          <p className="text-xs text-slate-400">
            Adjust core growth, pricing, and cost parameters to test business sensitivity in real time.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleReset}
            className="px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-xs text-slate-300 border border-white/10 flex items-center gap-1.5 transition-all"
          >
            <RefreshCw className="w-3.5 h-3.5" /> Reset
          </button>
          <button
            onClick={handleRun}
            disabled={isLoading}
            className="px-4 py-1.5 rounded-lg bg-sky-500 hover:bg-sky-600 disabled:opacity-50 text-xs font-semibold text-white shadow-md flex items-center gap-1.5 transition-all"
          >
            {isLoading ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5" />}
            Run Simulation
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        {/* Starting Customers */}
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-slate-400">Starting Tenants</span>
            <span className="font-bold text-white">{params.starting_customers}</span>
          </div>
          <input
            type="range"
            min="5"
            max="300"
            step="5"
            value={params.starting_customers}
            onChange={(e) => handleChange('starting_customers', e.target.value)}
            className="w-full accent-sky-400 cursor-pointer"
          />
        </div>

        {/* Growth Rate */}
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-slate-400">Monthly Growth Rate</span>
            <span className="font-bold text-sky-400">{params.monthly_growth_rate_pct}%</span>
          </div>
          <input
            type="range"
            min="2"
            max="40"
            step="0.5"
            value={params.monthly_growth_rate_pct}
            onChange={(e) => handleChange('monthly_growth_rate_pct', e.target.value)}
            className="w-full accent-sky-400 cursor-pointer"
          />
        </div>

        {/* Churn Rate */}
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-slate-400">Monthly Churn Rate</span>
            <span className="font-bold text-rose-400">{params.monthly_churn_rate_pct}%</span>
          </div>
          <input
            type="range"
            min="1"
            max="12"
            step="0.25"
            value={params.monthly_churn_rate_pct}
            onChange={(e) => handleChange('monthly_churn_rate_pct', e.target.value)}
            className="w-full accent-rose-400 cursor-pointer"
          />
        </div>

        {/* Monthly Plan Price */}
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-slate-400">Average Plan ARPU</span>
            <span className="font-bold text-emerald-400">${params.average_monthly_plan_usd}</span>
          </div>
          <input
            type="range"
            min="29"
            max="349"
            step="5"
            value={params.average_monthly_plan_usd}
            onChange={(e) => handleChange('average_monthly_plan_usd', e.target.value)}
            className="w-full accent-emerald-400 cursor-pointer"
          />
        </div>

        {/* Messages per customer */}
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-slate-400">Messages / Customer</span>
            <span className="font-bold text-white">{params.messages_per_customer_monthly.toLocaleString()}</span>
          </div>
          <input
            type="range"
            min="1000"
            max="15000"
            step="500"
            value={params.messages_per_customer_monthly}
            onChange={(e) => handleChange('messages_per_customer_monthly', e.target.value)}
            className="w-full accent-sky-400 cursor-pointer"
          />
        </div>

        {/* Fixed Monthly OPEX */}
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-slate-400">Monthly Fixed OPEX</span>
            <span className="font-bold text-white">${params.fixed_opex_monthly_usd.toLocaleString()}</span>
          </div>
          <input
            type="range"
            min="2000"
            max="25000"
            step="500"
            value={params.fixed_opex_monthly_usd}
            onChange={(e) => handleChange('fixed_opex_monthly_usd', e.target.value)}
            className="w-full accent-sky-400 cursor-pointer"
          />
        </div>

        {/* Initial Cash Balance */}
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-slate-400">Starting Cash Reserve</span>
            <span className="font-bold text-white">${params.starting_cash_balance_usd.toLocaleString()}</span>
          </div>
          <input
            type="range"
            min="5000"
            max="150000"
            step="5000"
            value={params.starting_cash_balance_usd}
            onChange={(e) => handleChange('starting_cash_balance_usd', e.target.value)}
            className="w-full accent-sky-400 cursor-pointer"
          />
        </div>
      </div>
    </div>
  );
}
