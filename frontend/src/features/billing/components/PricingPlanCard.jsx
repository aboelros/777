import React from 'react';
import PropTypes from 'prop-types';
import { motion } from 'framer-motion';
import { Check, ArrowRight } from 'lucide-react';
import GlassCard from '@/components/ui/GlassCard';
import Button from '@/components/ui/Button';

/**
 * PricingPlanCard - Renders an individual subscription tier card
 */
export default function PricingPlanCard({
  plan,
  index,
  billingCycle,
  isCurrent,
  isPopular,
  onUpgrade,
  isLoading,
  getTierIcon,
  getTierColor,
  getSavings,
  getPrice,
  t
}) {
  const Icon = getTierIcon(plan.tier);
  const savings = getSavings(plan);
  const price = getPrice(plan);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.08 }}
      className="relative flex flex-col h-full"
    >
      {isPopular && (
        <div className="absolute -top-3.5 left-0 right-0 flex justify-center z-10">
          <span className="px-3.5 py-1 bg-gradient-to-r from-sky-500 to-blue-600 text-white text-xs font-bold rounded-full shadow-md">
            {t('subscription.cards.popular') || 'MOST POPULAR'}
          </span>
        </div>
      )}

      <GlassCard
        className={`p-6 flex-1 flex flex-col justify-between ${
          isPopular ? 'border-2 border-sky-500 shadow-neon' : ''
        } ${isCurrent ? 'border-2 border-emerald-500/80' : ''}`}
      >
        <div>
          {/* Header */}
          <div className="text-center mb-6">
            <div
              className={`w-14 h-14 mx-auto mb-3.5 rounded-2xl bg-gradient-to-br ${getTierColor(
                plan.tier
              )} flex items-center justify-center shadow-lg`}
            >
              <Icon className="w-7 h-7 text-white" />
            </div>
            <h3 className="text-xl font-bold text-[var(--color-text-primary)] mb-1">
              {plan.name}
            </h3>
            <p className="text-xs text-[var(--color-text-muted)] min-h-[36px]">
              {plan.description}
            </p>
          </div>

          {/* Price */}
          <div className="text-center mb-6">
            <div className="flex items-baseline justify-center gap-1">
              <span className="text-3xl font-extrabold text-[var(--color-text-primary)] font-numeric">
                ${price}
              </span>
              <span className="text-xs text-[var(--color-text-muted)]">
                {billingCycle === 'monthly' ? '/month' : '/year'}
              </span>
            </div>
            {savings && (
              <p className="text-xs text-emerald-400 mt-1 font-medium">
                Save ${savings.amount} ({savings.percentage}%) annually
              </p>
            )}
          </div>

          {/* Feature list */}
          <div className="space-y-2.5 mb-6">
            {(plan.features || []).slice(0, 8).map((feature, idx) => (
              <div key={idx} className="flex items-start gap-2.5">
                <Check className="w-4 h-4 text-sky-400 flex-shrink-0 mt-0.5" />
                <span className="text-xs text-[var(--color-text-secondary)] leading-relaxed">
                  {feature}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* CTA Button */}
        <Button
          onClick={() => !isCurrent && onUpgrade(plan.tier)}
          disabled={isCurrent || isLoading}
          variant={isCurrent ? 'secondary' : isPopular ? 'primary' : 'outline'}
          fullWidth
          className="mt-4"
        >
          {isCurrent ? (
            <span className="flex items-center gap-2 text-emerald-400">
              <Check className="w-4 h-4" /> Current Active Plan
            </span>
          ) : (
            <span className="flex items-center justify-center gap-2">
              {plan.tier === 'free' ? 'Select Free Tier' : 'Upgrade Workspace'}
              <ArrowRight className="w-4 h-4" />
            </span>
          )}
        </Button>
      </GlassCard>
    </motion.div>
  );
}

PricingPlanCard.propTypes = {
  plan: PropTypes.object.isRequired,
  index: PropTypes.number.isRequired,
  billingCycle: PropTypes.string.isRequired,
  isCurrent: PropTypes.bool.isRequired,
  isPopular: PropTypes.bool.isRequired,
  onUpgrade: PropTypes.func.isRequired,
  isLoading: PropTypes.bool,
  getTierIcon: PropTypes.func.isRequired,
  getTierColor: PropTypes.func.isRequired,
  getSavings: PropTypes.func.isRequired,
  getPrice: PropTypes.func.isRequired,
  t: PropTypes.func.isRequired
};
