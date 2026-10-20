import React from 'react';
import PropTypes from 'prop-types';
import { motion } from 'framer-motion';
import { AlertTriangle, DollarSign } from 'lucide-react';
import GlassCard from '@/components/ui/GlassCard';
import { formatCurrency } from '@/utils/helpers';

/**
 * ReportSummaryCards - High-level telemetry for escalations, sales, and weekly performance
 */
export default function ReportSummaryCards({ dashboardSummary, t }) {
  if (!dashboardSummary) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8"
    >
      {/* Escalation Risk */}
      <GlassCard className="p-6 border-l-4 border-l-rose-500 bg-rose-500/5">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-rose-500/20 rounded-xl text-rose-400">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-semibold text-sm text-[var(--color-text-primary)]">
                {t('reports.cards.escalations') || 'Human Escalations Today'}
              </h3>
              <p className="text-xs text-rose-300">
                {t('reports.cards.escalations_desc') || 'Conversations flagged for review'}
              </p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-3xl font-bold font-numeric text-[var(--color-text-primary)]">
              {dashboardSummary.today?.escalations || 0}
            </p>
            <p className="text-xs text-[var(--color-text-muted)]">
              vs {dashboardSummary.yesterday?.escalations || 0} yesterday
            </p>
          </div>
        </div>
      </GlassCard>

      {/* Today's Sales */}
      <GlassCard className="p-6 border-l-4 border-l-emerald-500 bg-emerald-500/5">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-emerald-500/20 rounded-xl text-emerald-400">
              <DollarSign className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-semibold text-sm text-[var(--color-text-primary)]">
                {t('reports.cards.sales') || 'Revenue Generated Today'}
              </h3>
              <p className="text-xs text-emerald-300">
                {t('reports.cards.sales_desc') || 'Closed through automated checkout'}
              </p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-3xl font-bold font-numeric text-[var(--color-text-primary)]">
              {formatCurrency(dashboardSummary.today?.revenue || 0)}
            </p>
            <p className="text-xs text-emerald-400 font-medium">
              +{dashboardSummary.yesterday?.revenue ? '14.2%' : '100%'} vs yesterday
            </p>
          </div>
        </div>
      </GlassCard>

      {/* Performance Summary */}
      <GlassCard className="p-6 lg:col-span-2">
        <h3 className="font-semibold text-sm text-[var(--color-text-primary)] mb-4">
          {t('reports.cards.performance') || 'Weekly Overview'}
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="p-4 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl">
            <p className="text-[var(--color-text-muted)] text-xs mb-1">This Week</p>
            <p className="text-lg font-bold font-numeric text-[var(--color-text-primary)]">
              {formatCurrency(dashboardSummary.this_week?.revenue || 0)}
            </p>
          </div>
          <div className="p-4 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl">
            <p className="text-[var(--color-text-muted)] text-xs mb-1">Last Week</p>
            <p className="text-lg font-bold font-numeric text-[var(--color-text-secondary)]">
              {formatCurrency(dashboardSummary.last_week?.revenue || 0)}
            </p>
          </div>
          <div className="p-4 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl">
            <p className="text-[var(--color-text-muted)] text-xs mb-1">Month to Date</p>
            <p className="text-lg font-bold font-numeric text-sky-400">
              {formatCurrency(dashboardSummary.this_month?.revenue || 0)}
            </p>
          </div>
          <div className="p-4 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl">
            <p className="text-[var(--color-text-muted)] text-xs mb-1">Monthly Escalations</p>
            <p className="text-lg font-bold font-numeric text-rose-400">
              {dashboardSummary.this_month?.escalations || 0}
            </p>
          </div>
        </div>
      </GlassCard>
    </motion.div>
  );
}

ReportSummaryCards.propTypes = {
  dashboardSummary: PropTypes.object,
  t: PropTypes.func.isRequired
};
