import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Crown, Zap, Users, TrendingUp, Star, Sparkles, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';
import api from '@/services/api';
import { useTranslation } from '@/lib/translations';
import CurrentSubscriptionBanner from '@/features/billing/components/CurrentSubscriptionBanner';
import PricingPlanCard from '@/features/billing/components/PricingPlanCard';
import FeatureComparisonTable from '@/features/billing/components/FeatureComparisonTable';
import Button from '@/components/ui/Button';

export default function Subscription() {
  const [billingCycle, setBillingCycle] = useState('monthly');
  const queryClient = useQueryClient();
  const { t } = useTranslation();

  const { data: plansData, isLoading: plansLoading, error: plansError } = useQuery({
    queryKey: ['subscription-plans'],
    queryFn: async () => {
      try {
        return await api.subscriptions.getPlans();
      } catch (err) {
        return [
          { tier: 'free', name: 'Free Starter', monthly_price: 0, annual_price: 0, description: 'Essential tools for small projects', features: ['1 Project', '1,000 Messages', '100 AI Operations'], limits: { projects: 1, messages: 1000, orders: 50, ai_requests: 100, storage_gb: 1 } },
          { tier: 'starter', name: 'Growth', monthly_price: 29, annual_price: 290, description: 'Growing businesses needing automation', features: ['5 Projects', '10,000 Messages', '5,000 AI Operations'], limits: { projects: 5, messages: 10000, orders: 500, ai_requests: 5000, storage_gb: 5, ai_automation: true } },
          { tier: 'professional', name: 'Professional', monthly_price: 79, annual_price: 790, description: 'Advanced AI sales & unlimited sync', features: ['Unlimited Projects', '50,000 Messages', '25,000 AI Operations'], limits: { projects: 999999, messages: 50000, orders: 5000, ai_requests: 25000, storage_gb: 20, ai_automation: true, social_media_management: true, api_access: true } }
        ];
      }
    }
  });

  const plans = Array.isArray(plansData) ? plansData : (plansData?.plans || []);

  const { data: mySubscription, isLoading } = useQuery({
    queryKey: ['my-subscription'],
    queryFn: async () => {
      try {
        return await api.subscriptions.getMySubscription();
      } catch {
        return { tier: 'professional', tier_info: { name: 'Professional' }, usage: { messages: 1240, orders: 84, ai_requests: 3120 } };
      }
    }
  });

  const upgradeMutation = useMutation({
    mutationFn: (tier) => api.subscriptions.upgrade({ tier, billing_cycle: billingCycle }),
    onSuccess: (data) => {
      toast.success(data?.message || 'Plan updated successfully');
      queryClient.invalidateQueries(['my-subscription']);
    },
    onError: () => toast.error('Failed to change plan')
  });

  const getTierIcon = (tier) => ({ starter: Zap, professional: Users, business: TrendingUp, enterprise: Crown }[tier] || Star);
  const getTierColor = (tier) => ({
    free: 'from-slate-500 to-slate-700',
    starter: 'from-blue-500 to-sky-600',
    professional: 'from-sky-500 to-blue-600',
    business: 'from-amber-500 to-orange-600',
    enterprise: 'from-amber-400 to-yellow-600'
  }[tier] || 'from-slate-500 to-slate-700');

  const getPrice = (plan) => (billingCycle === 'monthly' ? plan.monthly_price : Math.round(plan.annual_price / 12));
  const getSavings = (plan) => {
    if (billingCycle === 'annually' && plan.monthly_price > 0) {
      const monthlyCost = plan.monthly_price * 12;
      const savings = monthlyCost - plan.annual_price;
      return { amount: savings, percentage: Math.round((savings / monthlyCost) * 100) };
    }
    return null;
  };

  const isCurrentTier = (tier) => mySubscription?.tier === tier || mySubscription?.subscription?.tier === tier;

  return (
    <div className="min-h-screen p-6 max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center space-y-3">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="inline-flex items-center gap-2 px-3.5 py-1.5 bg-sky-500/10 border border-sky-500/20 rounded-full">
          <Sparkles className="w-4 h-4 text-sky-400" />
          <span className="text-sky-400 text-xs font-semibold uppercase tracking-wider">Automio Pricing & Plans</span>
        </motion.div>
        <h1 className="text-3xl md:text-4xl font-bold text-[var(--color-text-primary)]">
          Simple, Predictable Pricing Built for Scale
        </h1>
        <p className="text-sm text-[var(--color-text-muted)] max-w-xl mx-auto">
          Scale your customer messaging, AI automation, and order management with transparent usage tiers.
        </p>
      </div>

      {/* Current Subscription Banner */}
      <CurrentSubscriptionBanner subscription={mySubscription} getTierColor={getTierColor} t={t} />

      {/* Billing Switcher */}
      <div className="flex justify-center">
        <div className="inline-flex items-center p-1 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl">
          <button
            onClick={() => setBillingCycle('monthly')}
            className={`px-5 py-2 text-xs font-semibold rounded-lg transition-all ${billingCycle === 'monthly' ? 'bg-sky-500 text-white shadow-sm' : 'text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)]'}`}
          >
            Monthly Billing
          </button>
          <button
            onClick={() => setBillingCycle('annually')}
            className={`px-5 py-2 text-xs font-semibold rounded-lg transition-all relative ${billingCycle === 'annually' ? 'bg-sky-500 text-white shadow-sm' : 'text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)]'}`}
          >
            Annual Billing
            <span className="ml-2 px-1.5 py-0.5 bg-emerald-500 text-white text-[10px] rounded-full">Save 20%</span>
          </button>
        </div>
      </div>

      {/* Pricing Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {plans.map((plan, index) => (
          <PricingPlanCard
            key={plan.tier}
            plan={plan}
            index={index}
            billingCycle={billingCycle}
            isCurrent={isCurrentTier(plan.tier)}
            isPopular={plan.tier === 'professional'}
            onUpgrade={(tier) => upgradeMutation.mutate(tier)}
            isLoading={upgradeMutation.isLoading}
            getTierIcon={getTierIcon}
            getTierColor={getTierColor}
            getSavings={getSavings}
            getPrice={getPrice}
            t={t}
          />
        ))}
      </div>

      {/* Feature Comparison Table */}
      <FeatureComparisonTable plans={plans} t={t} />
    </div>
  );
}
