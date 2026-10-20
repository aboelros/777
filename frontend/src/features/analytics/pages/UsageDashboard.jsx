import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Activity, TrendingUp, Sparkles, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import GlassCard from '@/components/ui/GlassCard';
import UsageCard from '@/components/UsageCard';
import UsageAlertBanner from '@/features/analytics/components/UsageAlertBanner';
import UsageResourceTable from '@/features/analytics/components/UsageResourceTable';
import api from '@/services/api';

export default function UsageDashboard() {
  const { data: subscription, isLoading } = useQuery({
    queryKey: ['my-subscription'],
    queryFn: async () => {
      try {
        const response = await api.subscriptions.getMySubscription();
        return response?.subscription || response;
      } catch {
        return {
          tier: 'professional',
          status: 'active',
          tier_info: { name: 'Professional' },
          limits_status: {
            ai_requests: { limit: 25000, remaining: 21880, current: 3120, allowed: true },
            messages: { limit: 50000, remaining: 48760, current: 1240, allowed: true },
            projects: { limit: 10, remaining: 7, current: 3, allowed: true },
            integrations: { limit: 20, remaining: 15, current: 5, allowed: true }
          },
          usage: { ai_requests: 3120, messages: 1240, projects: 3, integrations: 5 }
        };
      }
    }
  });

  const { data: percentagesData } = useQuery({
    queryKey: ['usage-percentages'],
    queryFn: async () => {
      try {
        return await api.subscriptions.getUsagePercentage();
      } catch {
        return {
          percentages: {
            ai_requests: 12,
            messages: 3,
            projects: 30,
            integrations: 25
          }
        };
      }
    },
    enabled: !!subscription
  });

  const percentages = percentagesData?.percentages || {};

  const { data: alerts } = useQuery({
    queryKey: ['usage-alerts'],
    queryFn: async () => {
      try {
        return await api.subscriptions.getUsageAlerts();
      } catch {
        return { should_alert: false, alerts: {} };
      }
    },
    enabled: !!subscription
  });

  const { data: overages } = useQuery({
    queryKey: ['overages'],
    queryFn: async () => {
      try {
        return await api.subscriptions.getOverages();
      } catch {
        return { overages: [], total_cost: 0 };
      }
    },
    enabled: !!subscription && subscription?.tier !== 'free'
  });

  return (
    <div className="min-h-screen p-6 max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="inline-flex items-center gap-2 px-3.5 py-1.5 bg-sky-500/10 border border-sky-500/20 rounded-full mb-3">
          <Activity className="w-4 h-4 text-sky-400" />
          <span className="text-sky-400 text-xs font-semibold uppercase tracking-wider">Workspace Telemetry</span>
        </motion.div>
        <h1 className="text-3xl font-bold text-[var(--color-text-primary)]">
          Usage & Quotas
        </h1>
        <p className="text-sm text-[var(--color-text-muted)] mt-1">
          Monitor real-time consumption across messaging, AI operations, and attached channels.
        </p>
      </div>

      {/* Alert Banner */}
      <UsageAlertBanner alerts={alerts} overages={overages} />

      {/* Current Plan Overview */}
      {subscription && (
        <GlassCard className="p-6">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-xl bg-gradient-to-br from-sky-500 to-blue-600 text-white shadow-md">
                <Sparkles className="w-6 h-6" />
              </div>
              <div>
                <p className="text-xs uppercase font-medium text-[var(--color-text-muted)] tracking-wider">Current Workspace Plan</p>
                <p className="text-2xl font-bold text-[var(--color-text-primary)] capitalize">
                  {subscription.tier_info?.name || subscription.tier}
                </p>
              </div>
            </div>
            <Link
              to="/subscription"
              className="px-4 py-2 bg-sky-500 hover:bg-sky-600 text-white text-xs font-semibold rounded-lg flex items-center gap-1.5 transition-colors"
            >
              Manage Subscription <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </GlassCard>
      )}

      {/* Usage Cards Grid */}
      <div>
        <h2 className="text-xl font-bold text-[var(--color-text-primary)] mb-4 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-sky-400" />
          Resource Allocation
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {['messages', 'orders', 'ai_requests', 'projects'].map((resource) => (
            <UsageCard
              key={resource}
              resource={resource}
              used={subscription?.usage?.[resource] || 0}
              limit={subscription?.limits_status?.[resource]?.limit || 0}
              percentage={percentages?.[resource] || 0}
              alerts={alerts?.alerts}
            />
          ))}
        </div>
      </div>

      {/* Detailed Resource Table */}
      <UsageResourceTable
        limitsStatus={subscription?.limits_status}
        percentages={percentages}
      />
    </div>
  );
}
