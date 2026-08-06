import { motion } from 'framer-motion';
import { AlertTriangle, TrendingUp, CheckCircle, XCircle } from 'lucide-react';
import GlassCard from './ui/GlassCard';
import { useTranslation } from '../lib/translations';

export default function UsageCard({ resource, used, limit, percentage, alerts }) {
  const { t } = useTranslation();
  const isUnlimited = limit === 'unlimited' || limit >= 999999;
  const alertLevel = alerts?.[resource]?.level;

  const getAlertColor = () => {
    if (alertLevel === 'critical') return 'text-red-400';
    if (alertLevel === 'warning') return 'text-yellow-400';
    if (alertLevel === 'info') return 'text-blue-400';
    return 'text-green-400';
  };

  const getAlertIcon = () => {
    if (alertLevel === 'critical') return XCircle;
    if (alertLevel === 'warning') return AlertTriangle;
    if (alertLevel === 'info') return TrendingUp;
    return CheckCircle;
  };

  const getProgressColor = () => {
    if (percentage >= 100) return 'bg-red-500';
    if (percentage >= 90) return 'bg-yellow-500';
    if (percentage >= 80) return 'bg-blue-500';
    return 'bg-green-500';
  };

  const AlertIcon = getAlertIcon();
  const remaining = Math.max(0, limit - used);

  return (
    <GlassCard className="p-4">
      <div className="flex items-center justify-between mb-3">
        <div>
          <h3 className="text-lg font-semibold text-white capitalize">
            {t(`reports.summary.${resource}`) || resource.replace('_', ' ')}
          </h3>
          <p className="text-sm text-gray-400">
            {isUnlimited ? t('reports.controls.all') : `${remaining.toLocaleString()} ${t('common.save')}`}
          </p>
        </div>

        {alertLevel && (
          <AlertIcon className={`w-5 h-5 ${getAlertColor()}`} />
        )}
      </div>

      <div className="space-y-2">
        {/* Usage Numbers */}
        <div className="flex justify-between text-sm">
          <span className="text-gray-400">{t('reports.summary.used')}</span>
          <span className="text-white font-semibold">
            {used.toLocaleString()} {isUnlimited ? '' : `/ ${limit.toLocaleString()}`}
          </span>
        </div>

        {/* Progress Bar */}
        {!isUnlimited && (
          <div className="relative h-2 bg-dark-700 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${Math.min(percentage, 100)}%` }}
              transition={{ duration: 0.5, ease: 'easeOut' }}
              className={`absolute top-0 left-0 h-full ${getProgressColor()} rounded-full`}
            />
          </div>
        )}

        {/* Percentage */}
        {!isUnlimited && (
          <div className="flex justify-between text-xs">
            <span className={getAlertColor()}>
              {percentage.toFixed(1)}% {t('reports.summary.used')}
            </span>
            {percentage >= 80 && (
              <span className={getAlertColor()}>
                {percentage >= 100 ? t('common.error') : t('common.active')}
              </span>
            )}
          </div>
        )}

        {/* Alert Message */}
        {alertLevel === 'critical' && (
          <motion.div
            initial={{ opacity: 0, y: -5 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-2 p-2 bg-red-500/20 border border-red-500/40 rounded-lg"
          >
            <p className="text-xs text-red-400 font-semibold">
              ⚠️ {t('common.error')}
            </p>
          </motion.div>
        )}

        {alertLevel === 'warning' && (
          <motion.div
            initial={{ opacity: 0, y: -5 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-2 p-2 bg-yellow-500/20 border border-yellow-500/40 rounded-lg"
          >
            <p className="text-xs text-yellow-400">
              {t('common.active')}
            </p>
          </motion.div>
        )}
      </div>
    </GlassCard>
  );
}
