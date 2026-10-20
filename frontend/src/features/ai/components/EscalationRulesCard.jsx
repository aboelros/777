import React from 'react';
import PropTypes from 'prop-types';
import { AlertTriangle, CheckCircle } from 'lucide-react';
import GlassCard from '@/components/ui/GlassCard';

/**
 * EscalationRulesCard - Controls rule-based human escalation criteria
 * @param {Object} props
 * @param {Object} props.settings Current escalation settings
 * @param {Function} props.setSettings Settings update dispatcher
 */
export default function EscalationRulesCard({ settings, setSettings }) {
  const rules = [
    {
      key: 'escalateOnLowConfidence',
      title: 'Low Confidence Responses',
      desc: 'Escalate when confidence score drops below target threshold'
    },
    {
      key: 'escalateFinancial',
      title: 'Financial Queries',
      desc: 'Pricing, payments, billing, discounts, and refund discussions'
    },
    {
      key: 'escalatePolicy',
      title: 'Policy Questions',
      desc: 'Terms of service, privacy, data usage, and compliance'
    },
    {
      key: 'escalateLegal',
      title: 'Legal Matters',
      desc: 'Contract liabilities, disputes, and formal regulatory queries'
    }
  ];

  return (
    <GlassCard>
      <div className="p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 to-amber-600 flex items-center justify-center">
            <AlertTriangle className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-[var(--color-text-primary)]">Escalation Rules</h2>
            <p className="text-sm text-[var(--color-text-muted)]">
              Automatically route high-risk query categories to human agents
            </p>
          </div>
        </div>

        <div className="space-y-3">
          {rules.map((rule) => {
            const isChecked = !!settings[rule.key];
            return (
              <label
                key={rule.key}
                className="flex items-center justify-between p-3.5 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] hover:bg-[var(--color-surface-hover)] cursor-pointer transition-colors"
              >
                <div className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    checked={isChecked}
                    onChange={(e) =>
                      setSettings({
                        ...settings,
                        [rule.key]: e.target.checked
                      })
                    }
                    className="w-4 h-4 rounded border-[var(--color-border)] text-sky-500 focus:ring-sky-500/30"
                  />
                  <div>
                    <div className="font-medium text-sm text-[var(--color-text-primary)]">
                      {rule.title}
                    </div>
                    <div className="text-xs text-[var(--color-text-muted)]">
                      {rule.desc}
                    </div>
                  </div>
                </div>
                {isChecked && <CheckCircle className="w-5 h-5 text-emerald-400" />}
              </label>
            );
          })}
        </div>
      </div>
    </GlassCard>
  );
}

EscalationRulesCard.propTypes = {
  settings: PropTypes.object.isRequired,
  setSettings: PropTypes.func.isRequired
};
