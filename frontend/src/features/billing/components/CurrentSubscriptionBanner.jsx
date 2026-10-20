import React from 'react';
import PropTypes from 'prop-types';
import { Shield } from 'lucide-react';
import GlassCard from '@/components/ui/GlassCard';

/**
 * CurrentSubscriptionBanner - Displays active plan tier and monthly resource consumption
 */
export default function CurrentSubscriptionBanner({ subscription, getTierColor, t }) {
  if (!subscription) return null;

  return (
    <GlassCard className="p-6 border-2 border-[var(--color-brand)]/40">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className={`p-3 rounded-xl bg-gradient-to-br ${getTierColor(subscription.tier)}`}>
            <Shield className="w-6 h-6 text-white" />
          </div>
          <div>
            <p className="text-xs uppercase font-medium text-[var(--color-text-muted)] tracking-wider">
              {t('subscription.current.title') || 'Active Workspace Subscription'}
            </p>
            <p className="text-2xl font-bold text-[var(--color-text-primary)] capitalize">
              {subscription.tier_info?.name || subscription.tier}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-6 self-end sm:self-center">
          <div className="text-center">
            <p className="text-xl font-bold text-[var(--color-text-primary)]">
              {subscription.usage?.messages || 0}
            </p>
            <p className="text-xs text-[var(--color-text-muted)]">
              {t('subscription.current.messages') || 'Messages'}
            </p>
          </div>
          <div className="w-px h-8 bg-[var(--color-border)]" />
          <div className="text-center">
            <p className="text-xl font-bold text-[var(--color-text-primary)]">
              {subscription.usage?.orders || 0}
            </p>
            <p className="text-xs text-[var(--color-text-muted)]">
              {t('subscription.current.orders') || 'Orders'}
            </p>
          </div>
          <div className="w-px h-8 bg-[var(--color-border)]" />
          <div className="text-center">
            <p className="text-xl font-bold text-[var(--color-text-primary)]">
              {subscription.usage?.ai_requests || 0}
            </p>
            <p className="text-xs text-[var(--color-text-muted)]">
              {t('subscription.current.ai_requests') || 'AI Ops'}
            </p>
          </div>
        </div>
      </div>
    </GlassCard>
  );
}

CurrentSubscriptionBanner.propTypes = {
  subscription: PropTypes.object,
  getTierColor: PropTypes.func.isRequired,
  t: PropTypes.func.isRequired
};
