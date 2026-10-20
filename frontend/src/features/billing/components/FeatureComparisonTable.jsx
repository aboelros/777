import React from 'react';
import PropTypes from 'prop-types';
import { Check, X } from 'lucide-react';
import GlassCard from '@/components/ui/GlassCard';

/**
 * FeatureComparisonTable - Complete tabular breakdown of tier limits and features
 */
export default function FeatureComparisonTable({ plans, t }) {
  const numericFeatures = [
    { label: 'Connected Projects', key: 'projects' },
    { label: 'Monthly Messages', key: 'messages' },
    { label: 'Tracked Orders', key: 'orders' },
    { label: 'AI Operations', key: 'ai_requests' },
    { label: 'Channel Integrations', key: 'integrations' },
    { label: 'Asset Storage', key: 'storage_gb' },
    { label: 'Workspace Seats', key: 'team_members' }
  ];

  const booleanFeatures = [
    { label: 'AI Sales Automation', key: 'ai_automation' },
    { label: 'Advanced Analytics & Exports', key: 'advanced_reports' },
    { label: 'Unified Social Inbox', key: 'social_media_management' },
    { label: 'Long-term Customer Memory', key: 'conversation_memory' },
    { label: 'Automatic Order Routing', key: 'order_automation' },
    { label: 'REST & Webhook API Access', key: 'api_access' },
    { label: 'Custom Domain & Branding', key: 'white_label' },
    { label: 'Fine-tuned Enterprise AI Models', key: 'custom_ai' }
  ];

  return (
    <div className="mt-12">
      <h2 className="text-2xl font-bold text-[var(--color-text-primary)] text-center mb-6">
        Full Feature Comparison
      </h2>
      <GlassCard className="p-6 overflow-x-auto">
        <table className="w-full text-left text-sm border-collapse">
          <thead>
            <tr className="border-b border-[var(--color-border)]">
              <th className="py-3 px-4 font-semibold text-[var(--color-text-primary)]">Feature</th>
              {plans.map((plan) => (
                <th key={plan.tier} className="text-center py-3 px-4 font-semibold text-[var(--color-text-primary)] capitalize">
                  {plan.name}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-[var(--color-border)]">
            {numericFeatures.map((f) => (
              <tr key={f.key} className="hover:bg-[var(--color-surface-hover)]">
                <td className="py-3 px-4 text-[var(--color-text-secondary)]">{f.label}</td>
                {plans.map((plan) => {
                  const val = plan.limits?.[f.key];
                  const isUnlimited = val >= 999999;
                  return (
                    <td key={plan.tier} className="text-center py-3 px-4 font-medium text-[var(--color-text-primary)] font-numeric">
                      {isUnlimited ? (
                        <span className="text-sky-400 font-semibold">Unlimited</span>
                      ) : f.key === 'storage_gb' ? (
                        `${val} GB`
                      ) : (
                        val?.toLocaleString() ?? '-'
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
            {booleanFeatures.map((f) => (
              <tr key={f.key} className="hover:bg-[var(--color-surface-hover)]">
                <td className="py-3 px-4 text-[var(--color-text-secondary)]">{f.label}</td>
                {plans.map((plan) => (
                  <td key={plan.tier} className="text-center py-3 px-4">
                    {plan.limits?.[f.key] ? (
                      <Check className="w-4 h-4 text-emerald-400 mx-auto" />
                    ) : (
                      <X className="w-4 h-4 text-slate-500 mx-auto" />
                    )}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </GlassCard>
    </div>
  );
}

FeatureComparisonTable.propTypes = {
  plans: PropTypes.array.isRequired,
  t: PropTypes.func.isRequired
};
