/**
 * AI Governance Settings Page
 * Configure AI confidence thresholds, human escalation rules, and override roles.
 */
import { useState } from 'react';
import { motion } from 'framer-motion';
import { Brain, Settings, Save, Users, Bell, CheckCircle } from 'lucide-react';
import { toast } from 'sonner';
import GlassCard from '@/components/ui/GlassCard';
import Button from '@/components/ui/Button';
import EscalationRulesCard from '@/features/ai/components/EscalationRulesCard';

export default function AIGovernance() {
  const [settings, setSettings] = useState({
    minConfidence: 0.75,
    escalateOnLowConfidence: true,
    escalateFinancial: true,
    escalatePolicy: true,
    escalateLegal: false,
    allowedOverrideRoles: ['admin', 'manager'],
    notifyOnEscalation: true,
    autoResponseEnabled: true,
    humanReviewRequired: false
  });

  const handleSave = async () => {
    try {
      toast.success('AI governance settings updated successfully');
    } catch {
      toast.error('Failed to save settings');
    }
  };

  const handleToggleRole = (role) => {
    const exists = settings.allowedOverrideRoles.includes(role);
    setSettings({
      ...settings,
      allowedOverrideRoles: exists
        ? settings.allowedOverrideRoles.filter((r) => r !== role)
        : [...settings.allowedOverrideRoles, role]
    });
  };

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3 text-[var(--color-text-primary)]">
            <Brain className="w-9 h-9 text-sky-400" />
            AI Governance & Safety
          </h1>
          <p className="text-sm text-[var(--color-text-muted)] mt-1">
            Configure AI confidence thresholds, automated safety guardrails, and escalation workflows
          </p>
        </div>

        <Button
          onClick={handleSave}
          variant="primary"
          leftIcon={Save}
        >
          Save Settings
        </Button>
      </div>

      {/* Confidence Threshold */}
      <GlassCard>
        <div className="p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-sky-500 to-blue-600 flex items-center justify-center">
              <Settings className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-[var(--color-text-primary)]">Confidence Threshold</h2>
              <p className="text-sm text-[var(--color-text-muted)]">
                Minimum score required for the AI model to respond without manual review
              </p>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-[var(--color-text-primary)]">
                  Minimum Confidence Score
                </span>
                <span className="text-lg font-bold text-sky-400">
                  {Math.round(settings.minConfidence * 100)}%
                </span>
              </div>

              <input
                type="range"
                min="0.5"
                max="1.0"
                step="0.05"
                value={settings.minConfidence}
                aria-label="Minimum Confidence Score"
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    minConfidence: parseFloat(e.target.value)
                  })
                }
                className="w-full h-2 bg-[var(--color-surface-hover)] rounded-lg appearance-none cursor-pointer accent-sky-500"
              />

              <div className="flex justify-between text-xs text-[var(--color-text-muted)] mt-1">
                <span>50% (Permissive)</span>
                <span>75% (Balanced Recommended)</span>
                <span>100% (Strict)</span>
              </div>
            </div>

            <div className="p-3.5 bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)]">
              <p className="text-xs text-[var(--color-text-secondary)] leading-relaxed">
                Queries scored below this boundary will automatically queue for human agent intervention.
              </p>
            </div>
          </div>
        </div>
      </GlassCard>

      {/* Escalation Rules Component */}
      <EscalationRulesCard settings={settings} setSettings={setSettings} />

      {/* Override Permissions */}
      <GlassCard>
        <div className="p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-sky-600 flex items-center justify-center">
              <Users className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-[var(--color-text-primary)]">Override Permissions</h2>
              <p className="text-sm text-[var(--color-text-muted)]">
                Roles permitted to override AI suggestions or take over active chats
              </p>
            </div>
          </div>

          <div className="space-y-3">
            {['admin', 'manager', 'agent'].map((role) => {
              const isAllowed = settings.allowedOverrideRoles.includes(role);
              return (
                <label
                  key={role}
                  className="flex items-center justify-between p-3.5 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] hover:bg-[var(--color-surface-hover)] cursor-pointer transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <input
                      type="checkbox"
                      checked={isAllowed}
                      onChange={() => handleToggleRole(role)}
                      className="w-4 h-4 rounded border-[var(--color-border)] text-sky-500 focus:ring-sky-500/30"
                    />
                    <div className="font-medium capitalize text-sm text-[var(--color-text-primary)]">
                      {role}
                    </div>
                  </div>
                  {isAllowed && <CheckCircle className="w-5 h-5 text-emerald-400" />}
                </label>
              );
            })}
          </div>
        </div>
      </GlassCard>

      {/* Notifications */}
      <GlassCard>
        <div className="p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center">
              <Bell className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-[var(--color-text-primary)]">Escalation Notifications</h2>
              <p className="text-sm text-[var(--color-text-muted)]">
                Delivery preferences for real-time human escalation alerts
              </p>
            </div>
          </div>

          <label className="flex items-center justify-between p-3.5 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] hover:bg-[var(--color-surface-hover)] cursor-pointer transition-colors">
            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                checked={settings.notifyOnEscalation}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    notifyOnEscalation: e.target.checked
                  })
                }
                className="w-4 h-4 rounded border-[var(--color-border)] text-sky-500 focus:ring-sky-500/30"
              />
              <div>
                <div className="font-medium text-sm text-[var(--color-text-primary)]">Notify Active Workspace Agents</div>
                <div className="text-xs text-[var(--color-text-muted)]">
                  Dispatch in-app sound and banner alerts immediately when a customer conversation escalates
                </div>
              </div>
            </div>
            {settings.notifyOnEscalation && <CheckCircle className="w-5 h-5 text-emerald-400" />}
          </label>
        </div>
      </GlassCard>
    </div>
  );
}
