import { Instagram, Facebook, Video, MessageCircle, Send, Globe } from 'lucide-react';
import GlassCard from '@/components/ui/GlassCard';
import Badge from '@/components/ui/Badge';

const PROVIDER_ICONS = {
  instagram: Instagram,
  facebook: Facebook,
  tiktok: Video,
  whatsapp: MessageCircle,
  telegram: Send,
};

export default function IntegrationDetailCard({ integration, account }) {
  const Icon = PROVIDER_ICONS[integration.provider] || Globe;
  const isConnected = integration.status === 'connected';

  return (
    <GlassCard className="p-6 rounded-2xl border border-border flex flex-col justify-between hover:border-brand-primary/30 transition-all">
      <div>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-brand-primary/10 border border-brand-primary/20 text-brand-primary">
              <Icon className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-base text-text-primary capitalize">{integration.provider}</h3>
              <p className="text-xs text-text-muted">{integration.name || account?.name || 'Omnichannel Stream'}</p>
            </div>
          </div>
          <Badge variant={isConnected ? 'success' : 'default'} withDot>
            {integration.status || 'disconnected'}
          </Badge>
        </div>

        <div className="space-y-2 text-xs text-text-secondary py-3 border-y border-border/50">
          <div className="flex justify-between">
            <span className="text-text-muted">Account ID:</span>
            <span className="font-mono text-text-primary truncate max-w-[180px]">{integration.id}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-text-muted">AI Auto-Reply:</span>
            <span className="text-emerald-400 font-medium">Active (Gemini 2.0)</span>
          </div>
          {account?.followers_count !== undefined && (
            <div className="flex justify-between">
              <span className="text-text-muted">Followers:</span>
              <span className="font-mono text-text-primary font-bold">{account.followers_count.toLocaleString()}</span>
            </div>
          )}
        </div>
      </div>

      <div className="pt-4 flex justify-between items-center text-xs">
        <span className="text-text-muted">Last sync: Just now</span>
        <span className="text-brand-primary font-semibold hover:underline cursor-pointer">
          Manage Rules →
        </span>
      </div>
    </GlassCard>
  );
}
