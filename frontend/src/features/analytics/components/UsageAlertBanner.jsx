import React from 'react';
import PropTypes from 'prop-types';
import { motion } from 'framer-motion';
import { AlertCircle, DollarSign, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import GlassCard from '@/components/ui/GlassCard';

/**
 * UsageAlertBanner - Renders active limit thresholds and overage alerts
 */
export default function UsageAlertBanner({ alerts, overages }) {
  const hasAlerts = alerts?.should_alert;
  const hasOverages = overages && overages.total_cost > 0;

  if (!hasAlerts && !hasOverages) return null;

  return (
    <div className="space-y-4">
      {hasAlerts && (
        <motion.div initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }}>
          <GlassCard className="p-4 border-2 border-amber-500/40 bg-amber-500/5">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              <div className="flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="text-sm font-semibold text-[var(--color-text-primary)]">Usage Limit Approaching</h3>
                  <p className="text-xs text-[var(--color-text-muted)] mt-0.5">
                    Your workspace is nearing capacity for active monthly quotas.
                  </p>
                </div>
              </div>
              <Link
                to="/subscription"
                className="px-4 py-1.5 bg-sky-500 hover:bg-sky-600 text-white text-xs font-semibold rounded-lg flex items-center gap-1.5 transition-colors self-end sm:self-auto"
              >
                Upgrade Tier <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </GlassCard>
        </motion.div>
      )}

      {hasOverages && (
        <motion.div initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }}>
          <GlassCard className="p-4 border-2 border-rose-500/40 bg-rose-500/5">
            <div className="flex items-start gap-3">
              <DollarSign className="w-5 h-5 text-rose-400 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <h3 className="text-sm font-semibold text-rose-400">Overage Charges Incurred</h3>
                <p className="text-xs text-[var(--color-text-muted)] mt-0.5">
                  Quotas have been exceeded. Total additional accrued cost: ${overages.total_cost?.toFixed(2)}
                </p>
              </div>
            </div>
          </GlassCard>
        </motion.div>
      )}
    </div>
  );
}

UsageAlertBanner.propTypes = {
  alerts: PropTypes.object,
  overages: PropTypes.object
};
