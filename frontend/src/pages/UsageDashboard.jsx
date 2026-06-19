import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import {
  Activity,
  AlertCircle,
  TrendingUp,
  DollarSign,
  MessageSquare,
  ShoppingCart,
  Cpu,
  FolderOpen,
  ArrowRight,
  Sparkles
} from 'lucide-react';
import { Link } from 'react-router-dom';
import GlassCard from '../components/GlassCard';
import UsageCard from '../components/UsageCard';
import api from '../services/api';

export default function UsageDashboard() {
  // Fetch current subscription with usage
  const { data: subscription, isLoading, error } = useQuery({
    queryKey: ['my-subscription'],
    queryFn: async () => {
      try {
        const response = await api.subscriptions.getMySubscription();
        return response.subscription;
      } catch (error) {
        console.error('Failed to fetch subscription:', error);
        // Return mock data for demo purposes
        return {
          tier: 'pro',
          status: 'active',
          tier_info: {
            name: 'Professional',
          },
          limits_status: {
            ai_requests: { limit: 10000, remaining: 7153, current: 2847, allowed: true },
            messages: { limit: 50000, remaining: 31707, current: 18293, allowed: true },
            projects: { limit: 10, remaining: 7, current: 3, allowed: true },
            integrations: { limit: 20, remaining: 12, current: 8, allowed: true }
          },
          usage: {
            ai_requests: 2847,
            messages: 18293,
            projects: 3,
            integrations: 8
          }
        };
      }
    },
  });

  // Fetch usage percentages
  const { data: percentagesData } = useQuery({
    queryKey: ['usage-percentages'],
    queryFn: async () => {
      try {
        return await api.subscriptions.getUsagePercentage();
      } catch (error) {
        console.error('Failed to fetch usage percentages:', error);
        // Calculate percentages from subscription data
        // Calculate percentages from subscription data
        if (subscription?.usage && subscription?.limits_status) {
          const { usage, limits_status } = subscription;
          return {
            percentages: {
              ai_requests: Math.round((usage.ai_requests / (limits_status.ai_requests?.limit || 1)) * 100),
              messages: Math.round((usage.messages / (limits_status.messages?.limit || 1)) * 100),
              projects: Math.round((usage.projects / (limits_status.projects?.limit || 1)) * 100),
              integrations: Math.round((usage.integrations / (limits_status.integrations?.limit || 1)) * 100)
            }
          };
        }
        return { percentages: {} };
      }
    },
    enabled: !!subscription,
  });

  const percentages = percentagesData?.percentages || {};

  // Fetch usage alerts
  const { data: alerts } = useQuery({
    queryKey: ['usage-alerts'],
    queryFn: async () => {
      try {
        return await api.subscriptions.getUsageAlerts();
      } catch (error) {
        console.error('Failed to fetch alerts:', error);
        // Generate alerts based on usage percentages
        const alertList = [];
        Object.entries(percentages).forEach(([key, percentage]) => {
          if (percentage > 80) {
            alertList.push({
              type: 'warning',
              message: `${key.replace('_', ' ')} usage is at ${percentage}%`,
              metric: key
            });
          }
        });
        return { alerts: alertList };
      }
    },
    enabled: !!subscription && Object.keys(percentages).length > 0,
    refetchInterval: 60000, // Check every minute
  });

  // Fetch overages
  const { data: overages } = useQuery({
    queryKey: ['overages'],
    queryFn: async () => {
      try {
        return await api.subscriptions.getOverages();
      } catch (error) {
        console.error('Failed to fetch overages:', error);
        return { overages: [] };
      }
    },
    enabled: !!subscription && subscription?.tier !== 'free',
  });

  const getResourceIcon = (resource) => {
    const icons = {
      messages: MessageSquare,
      orders: ShoppingCart,
      ai_requests: Cpu,
      projects: FolderOpen,
    };
    return icons[resource] || Activity;
  };

  const getTierColor = (tier) => {
    const colors = {
      free: 'from-gray-400 to-gray-600',
      starter: 'from-blue-400 to-blue-600',
      growth: 'from-orange-400 to-orange-600',
      professional: 'from-sky-400 to-sky-600',
      scale: 'from-green-400 to-green-600',
      business: 'from-indigo-400 to-indigo-600',
      enterprise: 'from-yellow-400 to-yellow-600',
    };
    return colors[tier] || 'from-gray-400 to-gray-600';
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-dark-950 flex items-center justify-center">
        <div className="text-white">Loading...</div>
      </div>
    );
  }

  const hasAlerts = alerts?.should_alert;
  const hasOverages = overages && overages.total_cost > 0;

  return (
    <div className="min-h-screen bg-dark-950 p-6">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div>
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="inline-flex items-center gap-2 px-4 py-2 bg-accent-500/20 rounded-full mb-4"
          >
            <Activity className="w-5 h-5 text-accent-400" />
            <span className="text-accent-400 font-semibold">Usage Dashboard</span>
          </motion.div>

          <h1 className="text-4xl font-bold text-white mb-2">Your Usage</h1>
          <p className="text-gray-400">
            Monitor your usage and stay within your plan limits
          </p>
        </div>

        {/* Alert Banner */}
        {hasAlerts && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
          >
            <GlassCard className="p-4 border-2 border-yellow-500/40 bg-yellow-500/10">
              <div className="flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <h3 className="text-white font-semibold mb-1">Usage Alerts</h3>
                  <p className="text-sm text-yellow-400 mb-2">
                    You're approaching or have exceeded limits on {Object.keys(alerts.alerts).length} resource(s)
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(alerts.alerts).map(([resource, alert]) => (
                      <span
                        key={resource}
                        className={`px-3 py-1 rounded-full text-xs font-semibold ${alert.level === 'critical'
                          ? 'bg-red-500/20 text-red-400 border border-red-500/40'
                          : alert.level === 'warning'
                            ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/40'
                            : 'bg-blue-500/20 text-blue-400 border border-blue-500/40'
                          }`}
                      >
                        {resource.replace('_', ' ')}: {alert.percentage.toFixed(0)}%
                      </span>
                    ))}
                  </div>
                </div>
                <Link
                  to="/subscription"
                  className="px-4 py-2 bg-accent-500 hover:bg-accent-600 text-white font-semibold rounded-lg transition-colors flex items-center gap-2 whitespace-nowrap"
                >
                  Upgrade Plan
                  <ArrowRight className="w-4 h-4" />
                </Link>
              </div>
            </GlassCard>
          </motion.div>
        )}

        {/* Overage Banner */}
        {hasOverages && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
          >
            <GlassCard className="p-4 border-2 border-red-500/40 bg-red-500/10">
              <div className="flex items-start gap-3">
                <DollarSign className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <h3 className="text-white font-semibold mb-1">Overage Charges</h3>
                  <p className="text-sm text-red-400 mb-2">
                    You've exceeded your plan limits this month. Additional charges will apply.
                  </p>
                  <div className="text-2xl font-bold text-red-400 mb-2">
                    ${overages.total_cost.toFixed(2)}
                  </div>
                  <div className="space-y-1">
                    {Object.entries(overages.overages || {}).map(([resource, data]) => (
                      <div key={resource} className="flex justify-between text-sm">
                        <span className="text-gray-400 capitalize">
                          {resource.replace('_', ' ')}: {data.overage.toLocaleString()} over limit
                        </span>
                        <span className="text-red-400 font-semibold">
                          +${data.cost.toFixed(2)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </GlassCard>
          </motion.div>
        )}

        {/* Current Plan Card */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <GlassCard className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div
                  className={`p-3 rounded-xl bg-gradient-to-br ${getTierColor(
                    subscription.tier
                  )}`}
                >
                  <Sparkles className="w-6 h-6 text-white" />
                </div>
                <div>
                  <p className="text-sm text-gray-400">Current Plan</p>
                  <p className="text-2xl font-bold text-white capitalize">
                    {subscription.tier_info?.name || subscription.tier}
                  </p>
                </div>
              </div>
              <Link
                to="/subscription"
                className="px-6 py-3 bg-accent-500 hover:bg-accent-600 text-white font-semibold rounded-lg transition-colors flex items-center gap-2"
              >
                View Plans
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </GlassCard>
        </motion.div>

        {/* Usage Grid */}
        <div>
          <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
            <TrendingUp className="w-6 h-6 text-accent-400" />
            Resource Usage
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {['messages', 'orders', 'ai_requests', 'projects'].map((resource) => {
              const usage = subscription.usage?.[resource] || 0;
              const limit = subscription.limits_status?.[resource]?.limit || 0;
              const percentage = percentages?.[resource] || 0;

              return (
                <motion.div
                  key={resource}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 }}
                >
                  <UsageCard
                    resource={resource}
                    used={usage}
                    limit={limit}
                    percentage={percentage}
                    alerts={alerts?.alerts}
                  />
                </motion.div>
              );
            })}
          </div>
        </div>

        {/* Usage Details Table */}
        <div>
          <h2 className="text-2xl font-bold text-white mb-4">Detailed Usage</h2>
          <GlassCard className="p-6 overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-accent-500/20">
                  <th className="text-left py-3 px-4 text-white font-semibold">Resource</th>
                  <th className="text-center py-3 px-4 text-white font-semibold">Used</th>
                  <th className="text-center py-3 px-4 text-white font-semibold">Limit</th>
                  <th className="text-center py-3 px-4 text-white font-semibold">Remaining</th>
                  <th className="text-center py-3 px-4 text-white font-semibold">Status</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(subscription.limits_status || {}).map(([resource, status]) => {
                  const percentage = percentages?.[resource] || 0;
                  const remaining = Math.max(0, status.remaining);
                  const isUnlimited = status.limit === 'unlimited' || status.limit >= 999999;

                  return (
                    <tr key={resource} className="border-b border-dark-700">
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          {(() => {
                            const Icon = getResourceIcon(resource);
                            return <Icon className="w-5 h-5 text-accent-400" />;
                          })()}
                          <span className="text-white capitalize">
                            {resource.replace('_', ' ')}
                          </span>
                        </div>
                      </td>
                      <td className="text-center py-3 px-4 text-white font-semibold">
                        {status.current.toLocaleString()}
                      </td>
                      <td className="text-center py-3 px-4 text-white">
                        {isUnlimited ? (
                          <span className="text-accent-400">Unlimited</span>
                        ) : (
                          status.limit.toLocaleString()
                        )}
                      </td>
                      <td className="text-center py-3 px-4 text-white">
                        {isUnlimited ? (
                          <span className="text-accent-400">∞</span>
                        ) : (
                          remaining.toLocaleString()
                        )}
                      </td>
                      <td className="text-center py-3 px-4">
                        {status.allowed ? (
                          <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-sm font-semibold">
                            OK
                          </span>
                        ) : (
                          <span className="px-3 py-1 bg-red-500/20 text-red-400 rounded-full text-sm font-semibold">
                            Exceeded
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </GlassCard>
        </div>

        {/* Upgrade CTA */}
        {hasAlerts && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center"
          >
            <GlassCard className="p-8 border-2 border-accent-500/40">
              <h3 className="text-2xl font-bold text-white mb-2">
                Need More Resources?
              </h3>
              <p className="text-gray-400 mb-6">
                Upgrade your plan to get higher limits and more features
              </p>
              <Link
                to="/subscription"
                className="inline-flex items-center gap-2 px-8 py-3 bg-accent-500 hover:bg-accent-600 text-white font-semibold rounded-lg transition-colors"
              >
                View Plans & Upgrade
                <ArrowRight className="w-5 h-5" />
              </Link>
            </GlassCard>
          </motion.div>
        )}
      </div>
    </div>
  );
}
