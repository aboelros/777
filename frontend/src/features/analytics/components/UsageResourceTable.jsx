import React from 'react';
import PropTypes from 'prop-types';
import { MessageSquare, ShoppingCart, Cpu, FolderOpen, Activity } from 'lucide-react';
import GlassCard from '@/components/ui/GlassCard';

/**
 * UsageResourceTable - Tabular breakdown of consumption by resource type
 */
export default function UsageResourceTable({ limitsStatus, percentages }) {
  const getResourceIcon = (resource) => {
    const icons = {
      messages: MessageSquare,
      orders: ShoppingCart,
      ai_requests: Cpu,
      projects: FolderOpen
    };
    const Icon = icons[resource] || Activity;
    return <Icon className="w-4 h-4 text-sky-400" />;
  };

  return (
    <GlassCard className="p-6 overflow-x-auto">
      <h3 className="text-lg font-bold text-[var(--color-text-primary)] mb-4">
        Resource Quotas & Status
      </h3>
      <table className="w-full text-left text-sm border-collapse">
        <thead>
          <tr className="border-b border-[var(--color-border)] text-xs text-[var(--color-text-muted)] uppercase tracking-wider">
            <th className="py-3 px-4 font-semibold">Resource</th>
            <th className="text-center py-3 px-4 font-semibold">Current Used</th>
            <th className="text-center py-3 px-4 font-semibold">Tier Limit</th>
            <th className="text-center py-3 px-4 font-semibold">Remaining</th>
            <th className="text-center py-3 px-4 font-semibold">Status</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-[var(--color-border)]">
          {Object.entries(limitsStatus || {}).map(([resource, status]) => {
            const isUnlimited = status.limit === 'unlimited' || status.limit >= 999999;
            const remaining = Math.max(0, status.remaining || 0);

            return (
              <tr key={resource} className="hover:bg-[var(--color-surface-hover)]">
                <td className="py-3 px-4">
                  <div className="flex items-center gap-2.5">
                    {getResourceIcon(resource)}
                    <span className="font-medium text-[var(--color-text-primary)] capitalize">
                      {resource.replace('_', ' ')}
                    </span>
                  </div>
                </td>
                <td className="text-center py-3 px-4 font-numeric font-medium text-[var(--color-text-primary)]">
                  {(status.current || 0).toLocaleString()}
                </td>
                <td className="text-center py-3 px-4 font-numeric text-[var(--color-text-secondary)]">
                  {isUnlimited ? 'Unlimited' : (status.limit || 0).toLocaleString()}
                </td>
                <td className="text-center py-3 px-4 font-numeric text-[var(--color-text-secondary)]">
                  {isUnlimited ? '∞' : remaining.toLocaleString()}
                </td>
                <td className="text-center py-3 px-4">
                  {status.allowed ? (
                    <span className="px-2.5 py-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-full text-xs font-semibold">
                      Nominal
                    </span>
                  ) : (
                    <span className="px-2.5 py-1 bg-rose-500/10 text-rose-400 border border-rose-500/20 rounded-full text-xs font-semibold">
                      Exceeded
                    </span>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </GlassCard>
  );
}

UsageResourceTable.propTypes = {
  limitsStatus: PropTypes.object,
  percentages: PropTypes.object
};
