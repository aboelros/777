import { MessageSquare, Clock, CheckCircle, Sparkles } from 'lucide-react';
import GlassCard from '@/components/ui/GlassCard';
import { useTranslation } from '@/lib/translations';

export default function SocialStatCards({ stats }) {
  const { t } = useTranslation();

  const cards = [
    {
      title: t('social.stats.comments') || 'Total Inquiries',
      value: stats.total_comments || 0,
      icon: MessageSquare,
      color: 'text-sky-400',
    },
    {
      title: t('social.stats.pending') || 'Awaiting Response',
      value: stats.pending_responses || 0,
      icon: Clock,
      color: 'text-amber-400',
    },
    {
      title: t('social.stats.responded') || 'Auto-Replied',
      value: stats.responded || 0,
      icon: CheckCircle,
      color: 'text-emerald-400',
    },
    {
      title: t('social.stats.rate') || 'Resolution Rate',
      value: `${stats.response_rate || 0}%`,
      icon: Sparkles,
      color: 'text-brand-primary',
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card, idx) => (
        <GlassCard key={idx} className="p-5 border border-border rounded-2xl flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-text-muted mb-1">{card.title}</p>
            <p className="text-2xl font-bold font-mono text-text-primary">{card.value}</p>
          </div>
          <div className="p-2.5 rounded-xl bg-surface-subtle border border-border">
            <card.icon className={`w-5 h-5 ${card.color}`} />
          </div>
        </GlassCard>
      ))}
    </div>
  );
}
