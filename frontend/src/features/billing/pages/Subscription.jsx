import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Check,
  X,
  Crown,
  Zap,
  Users,
  TrendingUp,
  Shield,
  Star,
  Sparkles,
  ArrowRight,
  AlertCircle
} from 'lucide-react';
import GlassCard from '../../../components/ui/GlassCard';
import api from '../../../services/api';
import { toast } from 'sonner';
import useThemeStore from '../../../store/themeStore';
import { useTranslation } from '../../../lib/translations';

export default function Subscription() {
  const [billingCycle, setBillingCycle] = useState('monthly');
  const queryClient = useQueryClient();
  const { t } = useTranslation();

  // Fetch all plans
  const { data: plansData, isLoading: plansLoading, error: plansError } = useQuery({
    queryKey: ['subscription-plans'],
    queryFn: async () => {
      console.log('Fetching subscription plans...');
      const result = await api.subscriptions.getPlans();
      console.log('Plans data received:', result);
      return result;
    },
    retry: 3,
    onError: (error) => {
      console.error('Failed to fetch plans:', error);
      toast.error(t('subscription.states.error'));
    }
  });

  // Safe extraction of plans array
  const plans = Array.isArray(plansData) ? plansData : (Array.isArray(plansData?.plans) ? plansData.plans : []);

  // Fetch my subscription
  const { data: mySubscription, isLoading, error: subscriptionError } = useQuery({
    queryKey: ['my-subscription'],
    queryFn: () => api.subscriptions.getMySubscription(),
    retry: 3,
    onError: (error) => {
      console.error('Failed to fetch subscription:', error);
      toast.error(t('subscription.states.error'));
    }
  });

  // Fetch usage percentages
  const { data: percentagesData } = useQuery({
    queryKey: ['usage-percentages'],
    queryFn: () => api.subscriptions.getUsagePercentage(),
    enabled: !!mySubscription,
  });

  const percentages = percentagesData?.percentages || {};

  // Fetch usage alerts
  const { data: alerts } = useQuery({
    queryKey: ['usage-alerts'],
    queryFn: () => api.subscriptions.getUsageAlerts(),
    enabled: !!mySubscription,
  });

  // Upgrade mutation
  const upgradeMutation = useMutation({
    mutationFn: async ({ tier }) => {
      return api.subscriptions.upgrade({
        tier,
        billing_cycle: billingCycle,
      });
    },
    onSuccess: (data) => {
      toast.success(data.message || t('integrations.connect_success'));
      queryClient.invalidateQueries(['my-subscription']);
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || t('common.error'));
    },
  });

  const getTierIcon = (tier) => {
    const icons = {
      free: Star,
      starter: Zap,
      professional: Users,
      business: TrendingUp,
      enterprise: Crown,
    };
    return icons[tier] || Star;
  };

  const getTierColor = (tier) => {
    const colors = {
      free: 'from-gray-400 to-gray-600',
      starter: 'from-blue-400 to-blue-600',
      professional: 'from-sky-400 to-sky-600',
      business: 'from-orange-400 to-orange-600',
      enterprise: 'from-yellow-400 to-yellow-600',
    };
    return colors[tier] || 'from-gray-400 to-gray-600';
  };

  const getPrice = (plan) => {
    return billingCycle === 'monthly' ? plan.monthly_price : plan.annual_price;
  };

  const getSavings = (plan) => {
    if (billingCycle === 'annually' && plan.monthly_price > 0) {
      const monthlyCost = plan.monthly_price * 12;
      const annualCost = plan.annual_price;
      const savings = monthlyCost - annualCost;
      const percentage = Math.round((savings / monthlyCost) * 100);
      return { amount: savings, percentage };
    }
    return null;
  };

  const isCurrentTier = (tier) => {
    return mySubscription?.subscription?.tier === tier || mySubscription?.tier === tier;
  };

  // Show loading state
  if (plansLoading || isLoading) {
    return (
      <div className="min-h-screen bg-dark-950 flex items-center justify-center">
        <div className="text-white text-xl">{t('subscription.states.loading')}</div>
      </div>
    );
  }

  // Show error state
  if (plansError || subscriptionError) {
    return (
      <div className="min-h-screen bg-dark-950 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 text-red-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-white mb-2">{t('subscription.states.error')}</h2>
          <p className="text-gray-400 mb-4">
            {plansError?.response?.data?.detail || subscriptionError?.response?.data?.detail || t('subscription.states.error')}
          </p>
          <button
            onClick={() => window.location.reload()}
            className="px-6 py-3 bg-accent-500 hover:bg-accent-600 text-white font-semibold rounded-lg transition-colors"
          >
            {t('subscription.states.retry')}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-dark-950 p-6">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center space-y-4">
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="inline-flex items-center gap-2 px-4 py-2 bg-accent-500/20 rounded-full"
          >
            <Sparkles className="w-5 h-5 text-accent-400" />
            <span className="text-accent-400 font-semibold">{t('subscription.title')}</span>
          </motion.div>

          <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-accent-400 via-accent-500 to-accent-600 bg-clip-text text-transparent">
            {t('subscription.headline')}
          </h1>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            {t('subscription.subheadline')}
          </p>
        </div>

        {/* Current Subscription Info */}
        {!isLoading && mySubscription && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
          >
            <GlassCard className="p-6 border-2 border-accent-500/40">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className={`p-3 rounded-xl bg-gradient-to-br ${getTierColor(mySubscription.tier)}`}>
                    <Shield className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">{t('subscription.current.title')}</p>
                    <p className="text-2xl font-bold text-white capitalize">
                      {mySubscription.tier_info?.name}
                    </p>
                  </div>
                </div>

                <div className="text-right">
                  <p className="text-sm text-gray-400">{t('subscription.current.usage_monthly')}</p>
                  <div className="flex items-center gap-4 mt-1">
                    <div className="text-center">
                      <p className="text-lg font-bold text-white">
                        {mySubscription.usage?.messages || 0}
                      </p>
                      <p className="text-xs text-gray-400">{t('subscription.current.messages')}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-lg font-bold text-white">
                        {mySubscription.usage?.orders || 0}
                      </p>
                      <p className="text-xs text-gray-400">{t('subscription.current.orders')}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-lg font-bold text-white">
                        {mySubscription.usage?.ai_requests || 0}
                      </p>
                      <p className="text-xs text-gray-400">{t('subscription.current.ai_requests')}</p>
                    </div>
                  </div>
                </div>
              </div>
            </GlassCard>
          </motion.div>
        )}

        {/* Billing Toggle */}
        <div className="flex justify-center">
          <div className="inline-flex items-center gap-3 p-1 bg-dark-800 rounded-xl">
            <button
              onClick={() => setBillingCycle('monthly')}
              className={`px-6 py-3 rounded-lg font-semibold transition-all ${billingCycle === 'monthly'
                ? 'bg-accent-500 text-white'
                : 'text-gray-400 hover:text-white'
                }`}
            >
              {t('subscription.billing.monthly')}
            </button>
            <button
              onClick={() => setBillingCycle('annually')}
              className={`px-6 py-3 rounded-lg font-semibold transition-all relative ${billingCycle === 'annually'
                ? 'bg-accent-500 text-white'
                : 'text-gray-400 hover:text-white'
                }`}
            >
              {t('subscription.billing.annually')}
              <span className="absolute -top-2 -right-2 px-2 py-0.5 bg-green-500 text-white text-xs rounded-full">
                {t('subscription.billing.save')}
              </span>
            </button>
          </div>
        </div>

        {/* Pricing Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
          {plans.map((plan, index) => {
            try {
              const Icon = getTierIcon(plan.tier);
              const savings = getSavings(plan);
              const price = getPrice(plan);
              const isCurrent = isCurrentTier(plan.tier);
              const isPopular = plan.tier === 'professional';

              return (
                <motion.div
                  key={plan.tier}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="relative"
                >
                  {isPopular && (
                    <div className="absolute -top-4 left-0 right-0 flex justify-center z-10">
                      <span className="px-4 py-1 bg-gradient-to-r from-accent-500 to-accent-600 text-white text-sm font-bold rounded-full">
                        {t('subscription.cards.popular')}
                      </span>
                    </div>
                  )}

                  <GlassCard
                    className={`p-6 h-full flex flex-col ${isPopular ? 'border-2 border-accent-500' : ''
                      } ${isCurrent ? 'border-2 border-green-500' : ''}`}
                  >
                    {/* Header */}
                    <div className="text-center mb-6">
                      <div
                        className={`w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br ${getTierColor(
                          plan.tier
                        )} flex items-center justify-center`}
                      >
                        <Icon className="w-8 h-8 text-white" />
                      </div>
                      <h3 className="text-2xl font-bold text-white mb-2">{plan.name}</h3>
                      <p className="text-sm text-gray-400 min-h-[40px]">{plan.description}</p>
                    </div>

                    {/* Price */}
                    <div className="text-center mb-6">
                      <div className="flex items-baseline justify-center gap-1">
                        <span className="text-4xl font-bold text-white">${price}</span>
                        <span className="text-gray-400">{billingCycle === 'monthly' ? t('subscription.cards.mo') : t('subscription.cards.yr')}</span>
                      </div>
                      {savings && (
                        <p className="text-sm text-green-400 mt-1">
                          {t('subscription.cards.save_amount')
                            .replace('{amount}', savings.amount)
                            .replace('{percent}', savings.percentage)}
                        </p>
                      )}
                    </div>

                    {/* Features */}
                    <div className="flex-1 space-y-3 mb-6">
                      {plan.features.slice(0, 8).map((feature, idx) => (
                        <div key={idx} className="flex items-start gap-2">
                          <Check className="w-5 h-5 text-accent-400 flex-shrink-0 mt-0.5" />
                          <span className="text-sm text-gray-300">{feature}</span>
                        </div>
                      ))}
                      {plan.features.length > 8 && (
                        <p className="text-sm text-gray-400 text-center">
                          {t('subscription.cards.more_features').replace('{count}', plan.features.length - 8)}
                        </p>
                      )}
                    </div>

                    {/* CTA Button */}
                    <button
                      onClick={() => !isCurrent && upgradeMutation.mutate({ tier: plan.tier })}
                      disabled={isCurrent || upgradeMutation.isLoading}
                      className={`w-full py-3 rounded-lg font-semibold transition-all flex items-center justify-center gap-2 ${isCurrent
                        ? 'bg-green-500/20 text-green-400 cursor-not-allowed'
                        : isPopular
                          ? 'bg-gradient-to-r from-accent-500 to-accent-600 text-white hover:from-accent-600 hover:to-accent-700'
                          : 'bg-dark-700 text-white hover:bg-dark-600'
                        }`}
                    >
                      {isCurrent ? (
                        <>
                          <Check className="w-5 h-5" />
                          {t('subscription.cards.buttons.current')}
                        </>
                      ) : (
                        <>
                          {plan.tier === 'free' ? t('subscription.cards.buttons.start') : t('subscription.cards.buttons.upgrade')}
                          <ArrowRight className="w-5 h-5" />
                        </>
                      )}
                    </button>
                  </GlassCard>
                </motion.div>
              );
            } catch (err) {
              console.error('Error rendering plan card:', err, plan);
              return null;
            }
          })}
        </div>

        {/* Features Comparison */}
        <div className="mt-12">
          <h2 className="text-2xl font-bold text-white text-center mb-8">
            {t('subscription.comparison.title')}
          </h2>
          <GlassCard className="p-6 overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-accent-500/20">
                  <th className="text-left py-4 px-4 text-white font-semibold">{t('subscription.comparison.header_feature')}</th>
                  {plans.map((plan) => (
                    <th key={plan.tier} className="text-center py-4 px-4 text-white font-semibold capitalize">
                      {plan.name}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {[
                  { label: t('subscription.comparison.features.projects'), key: 'projects' },
                  { label: t('subscription.comparison.features.messages'), key: 'messages' },
                  { label: t('subscription.comparison.features.orders'), key: 'orders' },
                  { label: t('subscription.comparison.features.ai_requests'), key: 'ai_requests' },
                  { label: t('subscription.comparison.features.integrations'), key: 'integrations' },
                  { label: t('subscription.comparison.features.storage'), key: 'storage_gb' },
                  { label: t('subscription.comparison.features.team_members'), key: 'team_members' },
                ].map((feature) => (
                  <tr key={feature.key} className="border-b border-dark-700">
                    <td className="py-4 px-4 text-gray-300">{feature.label}</td>
                    {plans.map((plan) => {
                      const value = plan.limits[feature.key];
                      const isUnlimited = value >= 999999;
                      return (
                        <td key={plan.tier} className="text-center py-4 px-4 text-white font-semibold">
                          {isUnlimited ? (
                            <span className="text-accent-400">{t('subscription.comparison.unlimited')}</span>
                          ) : feature.key === 'storage_gb' ? (
                            `${value}GB`
                          ) : (
                            value.toLocaleString()
                          )}
                        </td>
                      );
                    })}
                  </tr>
                ))}

                {[
                  { label: t('subscription.comparison.features.ai_automation'), key: 'ai_automation' },
                  { label: t('subscription.comparison.features.advanced_reports'), key: 'advanced_reports' },
                  { label: t('subscription.comparison.features.social_media'), key: 'social_media_management' },
                  { label: t('subscription.comparison.features.memory'), key: 'conversation_memory' },
                  { label: t('subscription.comparison.features.order_auto'), key: 'order_automation' },
                  { label: t('subscription.comparison.features.api'), key: 'api_access' },
                  { label: t('subscription.comparison.features.white_label'), key: 'white_label' },
                  { label: t('subscription.comparison.features.custom_ai'), key: 'custom_ai' },
                ].map((feature) => (
                  <tr key={feature.key} className="border-b border-dark-700">
                    <td className="py-4 px-4 text-gray-300">{feature.label}</td>
                    {plans.map((plan) => (
                      <td key={plan.tier} className="text-center py-4 px-4">
                        {plan.limits[feature.key] ? (
                          <Check className="w-5 h-5 text-green-400 mx-auto" />
                        ) : (
                          <X className="w-5 h-5 text-gray-600 mx-auto" />
                        )}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </GlassCard>
        </div>

        {/* FAQ Section */}
        <div className="mt-12 text-center">
          <h2 className="text-2xl font-bold text-white mb-4">{t('subscription.faq.title')}</h2>
          <p className="text-gray-400 mb-6">
            {t('subscription.faq.desc')}
          </p>
          <div className="flex gap-4 justify-center">
            <button className="px-6 py-3 bg-accent-500 hover:bg-accent-600 text-white font-semibold rounded-lg transition-colors">
              {t('subscription.faq.contact')}
            </button>
            <button className="px-6 py-3 bg-dark-700 hover:bg-dark-600 text-white font-semibold rounded-lg transition-colors">
              {t('subscription.faq.docs')}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
