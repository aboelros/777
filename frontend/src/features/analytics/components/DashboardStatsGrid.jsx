import { motion } from 'framer-motion';
import { DollarSign, ShoppingCart, MessageSquare, Package, Hash, Zap, TrendingUp, TrendingDown } from 'lucide-react';
import GlassCard from '@/components/ui/GlassCard';
import SkeletonLoader from '@/components/ui/SkeletonLoader';
import ApiErrorState from '@/components/ApiErrorState';

export default function DashboardStatsGrid({ stats, isLoading, error, onRetry }) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {Array.from({ length: 6 }).map((_, i) => (
          <SkeletonLoader key={i} type="card" />
        ))}
      </div>
    );
  }

  if (error && import.meta.env.VITE_TESTING_MODE !== 'true') {
    return <ApiErrorState error={error} onRetry={onRetry} />;
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {stats.map((stat, index) => (
        <motion.div
          key={stat.label}
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.05 }}
        >
          <GlassCard className="p-6 rounded-2xl border border-white/10 hover:border-sky-400/50 transition-all flex flex-col justify-between group shadow-[0_8px_32px_rgba(0,0,0,0.45)]">
            <div>
              <div className="flex items-start justify-between mb-4">
                <div className="p-3 rounded-2xl bg-gradient-to-br from-sky-500/20 via-blue-600/10 to-transparent border border-sky-400/30 text-sky-400 shadow-[0_0_16px_rgba(56,189,248,0.25)] group-hover:scale-105 transition-transform duration-250">
                  <stat.icon className="w-5 h-5" />
                </div>
                {stat.change && (
                  <div
                    className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold backdrop-blur-md ${
                      stat.trend === 'up'
                        ? 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 shadow-[0_0_12px_rgba(16,185,129,0.2)]'
                        : 'bg-rose-500/15 text-rose-300 border border-rose-500/30 shadow-[0_0_12px_rgba(244,63,94,0.2)]'
                    }`}
                  >
                    {stat.trend === 'up' ? <TrendingUp className="w-3.5 h-3.5" /> : <TrendingDown className="w-3.5 h-3.5" />}
                    {stat.change}
                  </div>
                )}
              </div>

              <p className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5">{stat.label}</p>
              <p className="text-3xl font-extrabold font-numeric text-white tracking-tight drop-shadow-[0_2px_12px_rgba(255,255,255,0.12)]">
                {stat.value}
              </p>
            </div>

            {stat.subValue && (
              <p className="text-xs text-slate-400 mt-4 pt-3 border-t border-white/10 truncate font-medium">
                {stat.subValue}
              </p>
            )}
          </GlassCard>
        </motion.div>
      ))}
    </div>
  );
}
