import { motion } from 'framer-motion';
import { Sparkles, BarChart3, Zap } from 'lucide-react';
import GlassCard from '@/components/ui/GlassCard';
import Badge from '@/components/ui/Badge';
import { useTranslation } from '@/lib/translations';

export default function AssistantSidebar({ businessContext, dailyUsage, subscription }) {
  const { t } = useTranslation();

  const capabilities = [
    t('assistant.capabilities.analyze') || 'Sales Pipeline Intelligence',
    t('assistant.capabilities.manage_orders') || 'Autonomous Order Management',
    t('assistant.capabilities.respond') || 'Omnichannel Message Routing',
    t('assistant.capabilities.reports') || 'Automated Performance Reporting',
    t('assistant.capabilities.follow_ups') || 'Proactive Lead Follow-ups',
  ];

  return (
    <div className="hidden lg:flex lg:w-[45%] flex-col space-y-4 overflow-y-auto pr-1">
      {/* Model Specifications */}
      <GlassCard className="p-5 border border-border rounded-2xl">
        <h3 className="text-sm font-bold uppercase tracking-wider text-text-primary mb-3 flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-brand-primary" />
          {t('assistant.model_info.title') || 'Active AI Model'}
        </h3>
        <div className="space-y-2.5 text-xs">
          <div className="flex items-center justify-between p-2 rounded-lg bg-surface-subtle">
            <span className="text-text-muted">Engine</span>
            <div className="flex items-center gap-1.5">
              <span className="font-semibold text-text-primary">Gemini 2.0 Flash</span>
              <Badge variant="success" size="sm">High-Speed</Badge>
            </div>
          </div>
          <div className="flex items-center justify-between p-2 rounded-lg bg-surface-subtle">
            <span className="text-text-muted">Context Window</span>
            <span className="font-mono font-medium text-text-primary">1,000,000 Tokens</span>
          </div>
          <div className="flex items-center justify-between p-2 rounded-lg bg-surface-subtle">
            <span className="text-text-muted">Function Calling</span>
            <span className="font-medium text-emerald-400">Enabled (Catalog & CRM)</span>
          </div>
        </div>
      </GlassCard>

      {/* Business Workspace Context */}
      {businessContext && (
        <GlassCard className="p-5 border border-border rounded-2xl">
          <h3 className="text-sm font-bold uppercase tracking-wider text-text-primary mb-3 flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-brand-primary" />
            {t('assistant.business_context.title') || 'Active Workspace Telemetry'}
          </h3>
          <div className="space-y-2 text-xs">
            <div className="flex items-center justify-between p-2 rounded-lg bg-surface-subtle">
              <span className="text-text-muted">Workspace</span>
              <span className="font-semibold text-text-primary">{businessContext.project_name}</span>
            </div>
            <div className="flex items-center justify-between p-2 rounded-lg bg-surface-subtle">
              <span className="text-text-muted">Total Customer Interactions</span>
              <span className="font-mono font-medium text-text-primary">{businessContext.total_messages}</span>
            </div>
            {businessContext.unread_messages > 0 && (
              <div className="flex items-center justify-between p-2 rounded-lg bg-amber-500/10 border border-amber-500/20">
                <span className="text-amber-400">Unread Inquiries</span>
                <span className="font-mono font-bold text-amber-400">{businessContext.unread_messages}</span>
              </div>
            )}
          </div>
        </GlassCard>
      )}

      {/* Capabilities */}
      <GlassCard className="p-5 border border-border rounded-2xl">
        <h3 className="text-sm font-bold uppercase tracking-wider text-text-primary mb-3">
          {t('assistant.capabilities.title') || 'Operational Capabilities'}
        </h3>
        <div className="space-y-1.5">
          {capabilities.map((action, index) => (
            <div
              key={index}
              className="flex items-center gap-2.5 p-2 rounded-lg bg-surface-subtle text-xs text-text-secondary"
            >
              <div className="w-1.5 h-1.5 rounded-full bg-brand-primary" />
              <span>{action}</span>
            </div>
          ))}
        </div>
      </GlassCard>

      {/* Daily Usage */}
      <GlassCard className="p-5 border border-border rounded-2xl">
        <h3 className="text-sm font-bold uppercase tracking-wider text-text-primary mb-3">
          {t('assistant.usage.title') || 'API Consumption'}
        </h3>
        <div className="space-y-3">
          <div>
            <div className="flex items-center justify-between text-xs mb-1.5">
              <span className="text-text-muted">Requests Today</span>
              <span className="font-mono text-text-primary font-semibold">
                {dailyUsage?.request_count || 0} / {subscription?.limits_status?.ai_requests?.limit || 'Unlimited'}
              </span>
            </div>
            <div className="h-2 bg-surface-subtle rounded-full overflow-hidden border border-border">
              <div
                className="h-full bg-brand-primary"
                style={{
                  width: `${Math.min(
                    ((dailyUsage?.request_count || 0) / (subscription?.limits_status?.ai_requests?.limit || 100)) * 100,
                    100
                  )}%`
                }}
              />
            </div>
          </div>

          <div className="flex items-center justify-between text-xs text-text-muted pt-1 border-t border-border/50">
            <span>Estimated Cost:</span>
            <span className="font-mono text-text-primary font-semibold">
              ${(dailyUsage?.total_cost || 0).toFixed(4)}
            </span>
          </div>
        </div>
      </GlassCard>
    </div>
  );
}
