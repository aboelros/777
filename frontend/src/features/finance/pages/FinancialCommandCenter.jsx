import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { TrendingUp, Layers, Calculator, Award, Globe, Table as TableIcon } from 'lucide-react';
import { toast } from 'sonner';

import { useProjectStore } from '@/store/projectStore';
import financeApi from '@/features/finance/api/financeApi';
import ExecutiveOverviewCards from '@/features/finance/components/ExecutiveOverviewCards';
import UnitEconomicsCard from '@/features/finance/components/UnitEconomicsCard';
import ScenarioComparisonTable from '@/features/finance/components/ScenarioComparisonTable';
import ValuationBreakdown from '@/features/finance/components/ValuationBreakdown';
import RegionalMarketTable from '@/features/finance/components/RegionalMarketTable';
import InteractiveSimulator from '@/features/finance/components/InteractiveSimulator';
import { PageLoader } from '@/components/ui/LoadingSpinner';

export default function FinancialCommandCenter() {
  const { currentProject } = useProjectStore();
  const projectId = currentProject?.id;
  const [activeTab, setActiveTab] = useState('overview'); // overview, simulator, statements, market
  const [simulatedOverview, setSimulatedOverview] = useState(null);

  // 1. Fetch live overview data
  const { data: overview, isLoading: isOverviewLoading, error: overviewError } = useQuery({
    queryKey: ['finance-overview', projectId],
    queryFn: () => financeApi.getOverview(projectId),
    enabled: !!projectId,
  });

  // 2. Fetch default scenarios comparison
  const { data: scenarios, isLoading: isScenariosLoading } = useQuery({
    queryKey: ['finance-scenarios', projectId],
    queryFn: () => financeApi.getScenarios(projectId, 36),
    enabled: !!projectId,
  });

  // 3. Interactive simulation mutation
  const simulateMutation = useMutation({
    mutationFn: (config) => financeApi.simulate(projectId, config),
    onSuccess: (data) => {
      setSimulatedOverview(data);
      toast.success('Simulation updated successfully');
    },
    onError: (err) => {
      toast.error(err?.message || 'Simulation failed');
    },
  });

  const activeData = simulatedOverview || overview;

  if (isOverviewLoading && !activeData) {
    return <PageLoader text="Loading Financial Intelligence Engine..." />;
  }

  const formatCurrency = (val) =>
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-white/10 pb-5">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2.5">
            <TrendingUp className="w-6 h-6 text-sky-400" /> Financial Intelligence & Valuation Engine
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Automind strategic forecasting, unit margins, GAAP statements, and independent company valuations.
          </p>
        </div>

        {/* Tab Switcher */}
        <div className="flex items-center gap-1.5 p-1 bg-[#0b1022]/90 border border-white/10 rounded-xl">
          {[
            { id: 'overview', label: 'Overview', icon: TrendingUp },
            { id: 'simulator', label: 'Simulator & Scenarios', icon: Layers },
            { id: 'statements', label: '36-Month Statements', icon: TableIcon },
            { id: 'market', label: 'Global Opportunity', icon: Globe },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium flex items-center gap-1.5 transition-all ${
                  isActive
                    ? 'bg-sky-500/20 text-sky-300 border border-sky-500/30'
                    : 'text-slate-400 hover:text-white hover:bg-white/5'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                {tab.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Primary Overview Cards */}
      <ExecutiveOverviewCards overview={activeData} />

      {/* Tab: Executive Overview */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          <UnitEconomicsCard unitEcon={activeData?.unit_economics} />
          <ValuationBreakdown valuation={activeData?.valuation} />
          <ScenarioComparisonTable scenarios={scenarios} />
        </div>
      )}

      {/* Tab: Interactive Simulator & Scenarios */}
      {activeTab === 'simulator' && (
        <div className="space-y-6">
          <InteractiveSimulator
            onSimulate={(cfg) => simulateMutation.mutate(cfg)}
            isLoading={simulateMutation.isPending}
          />
          <ScenarioComparisonTable scenarios={scenarios} />
          <UnitEconomicsCard unitEcon={activeData?.unit_economics} />
        </div>
      )}

      {/* Tab: 36-Month Projections Statements */}
      {activeTab === 'statements' && (
        <div className="bg-[#0b1022]/80 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-xl overflow-x-auto">
          <div className="mb-4">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <TableIcon className="w-5 h-5 text-sky-400" /> 36-Month Financial Statement Forecast
            </h3>
            <p className="text-xs text-slate-400">Deterministic income statement and free cash flow line items.</p>
          </div>
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-[#0f172a]/60 text-slate-400 uppercase tracking-wider border-b border-white/10">
              <tr>
                <th className="py-2.5 px-3">Month</th>
                <th className="py-2.5 px-3">Tenants</th>
                <th className="py-2.5 px-3">Revenue</th>
                <th className="py-2.5 px-3">COGS</th>
                <th className="py-2.5 px-3">Gross Profit</th>
                <th className="py-2.5 px-3">OPEX</th>
                <th className="py-2.5 px-3">EBITDA</th>
                <th className="py-2.5 px-3">Net Income</th>
                <th className="py-2.5 px-3">Cash Balance</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {(activeData?.projections_36_months || []).slice(0, 36).map((m) => (
                <tr key={m.month} className="hover:bg-white/[0.02]">
                  <td className="py-2 px-3 font-semibold text-slate-300">M{m.month}</td>
                  <td className="py-2 px-3 text-slate-200">{m.active_customers}</td>
                  <td className="py-2 px-3 font-medium text-white">{formatCurrency(m.total_revenue)}</td>
                  <td className="py-2 px-3 text-rose-300">{formatCurrency(m.cogs)}</td>
                  <td className="py-2 px-3 text-emerald-300">{formatCurrency(m.gross_profit)}</td>
                  <td className="py-2 px-3 text-slate-400">{formatCurrency(m.total_opex)}</td>
                  <td className="py-2 px-3 text-slate-200">{formatCurrency(m.ebitda)}</td>
                  <td className={`py-2 px-3 font-semibold ${parseFloat(m.net_income) >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                    {formatCurrency(m.net_income)}
                  </td>
                  <td className="py-2 px-3 font-mono text-slate-300">{formatCurrency(m.cash_balance)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Tab: Global Market Opportunity */}
      {activeTab === 'market' && (
        <div className="space-y-6">
          <RegionalMarketTable regions={activeData?.regional_opportunities} />
        </div>
      )}
    </div>
  );
}
