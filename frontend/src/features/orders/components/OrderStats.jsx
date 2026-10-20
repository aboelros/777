import { motion } from 'framer-motion';
import { ShoppingCart, DollarSign, Clock, TrendingUp } from 'lucide-react';
import GlassCard from '@/components/ui/GlassCard';
import { formatCurrency } from '@/utils/helpers';
import { useTranslation } from '@/lib/translations';

export default function OrderStats({ stats }) {
  const { t } = useTranslation();

  const cards = [
    {
      title: t('orders.stats.total_orders') || 'Total Orders',
      value: stats?.total_orders || 0,
      change: '+12.5%',
      icon: ShoppingCart,
      color: 'text-sky-400',
      bg: 'bg-sky-500/10',
    },
    {
      title: t('orders.stats.total_revenue') || 'Total Revenue',
      value: formatCurrency(stats?.total_revenue || 0),
      change: '+18.2%',
      icon: DollarSign,
      color: 'text-emerald-400',
      bg: 'bg-emerald-500/10',
    },
    {
      title: t('orders.stats.pending_orders') || 'Pending Orders',
      value: stats?.pending_orders || 0,
      change: '-5.4%',
      icon: Clock,
      color: 'text-amber-400',
      bg: 'bg-amber-500/10',
    },
    {
      title: t('orders.stats.fulfillment_rate') || 'Fulfillment Rate',
      value: `${stats?.fulfillment_rate || 0}%`,
      change: '+3.1%',
      icon: TrendingUp,
      color: 'text-brand-primary',
      bg: 'bg-brand-primary/10',
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {cards.map((stat, index) => (
        <motion.div
          key={stat.title}
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.05 }}
        >
          <GlassCard className="p-5 border border-border rounded-2xl hover:border-brand-primary/30 transition-all">
            <div className="flex items-center justify-between mb-3">
              <div className={`p-2.5 rounded-xl ${stat.bg} ${stat.color}`}>
                <stat.icon className="w-5 h-5" />
              </div>
              <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
                stat.change.startsWith('+')
                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                  : 'bg-red-500/10 text-red-400 border border-red-500/20'
              }`}>
                {stat.change}
              </span>
            </div>
            <p className="text-xs font-medium uppercase tracking-wider text-text-muted mb-1">{stat.title}</p>
            <p className="text-2xl font-bold font-mono text-text-primary">{stat.value}</p>
          </GlassCard>
        </motion.div>
      ))}
    </div>
  );
}
