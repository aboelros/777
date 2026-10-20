import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { GitBranch, Plus, Play, Clock } from 'lucide-react';
import api from '@/services/api';
import { useProjectStore } from '@/store/projectStore';
import DripBuilder from '@/components/DripBuilder';
import { useTranslation } from '@/lib/translations';
import Button from '@/components/ui/Button';
import Badge from '@/components/ui/Badge';
import { NoProjectState, EmptyState } from '@/components/ui/EmptyState';
import SkeletonLoader from '@/components/ui/SkeletonLoader';

export default function DripCampaigns() {
  const { currentProject } = useProjectStore();
  const { t } = useTranslation();
  const [isBuilderOpen, setIsBuilderOpen] = useState(false);
  const [selectedCampaign, setSelectedCampaign] = useState(null);

  const { data: campaigns = [], isLoading } = useQuery({
    queryKey: ['drip-campaigns', currentProject?.id],
    queryFn: () => api.dripCampaigns.getCampaigns(currentProject.id),
    enabled: !!currentProject?.id,
  });

  if (!currentProject) {
    return <NoProjectState subtitle={t('campaigns.subtitle') || 'Select a project to manage automated communication sequences'} />;
  }

  return (
    <div className="h-full flex flex-col p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3 text-text-primary tracking-tight">
            <span className="p-2.5 rounded-xl bg-brand-primary/10 border border-brand-primary/20 text-brand-primary">
              <GitBranch className="w-6 h-6" />
            </span>
            {t('campaigns.title')}
          </h1>
          <p className="text-sm text-text-secondary mt-1">{t('campaigns.subtitle')}</p>
        </div>
        <Button
          onClick={() => { setSelectedCampaign(null); setIsBuilderOpen(true); }}
          variant="primary"
          leftIcon={Plus}
        >
          {t('campaigns.new')}
        </Button>
      </div>

      {/* Campaign List / Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {Array.from({ length: 3 }).map((_, i) => (
            <SkeletonLoader key={i} type="card" />
          ))}
        </div>
      ) : campaigns.length === 0 ? (
        <EmptyState
          icon={GitBranch}
          title={t('campaigns.empty_title') || 'No Drip Sequences Created'}
          description={t('campaigns.empty_desc') || 'Automate follow-ups and nurture leads with multi-step trigger sequences.'}
          actionLabel={t('campaigns.new')}
          onAction={() => { setSelectedCampaign(null); setIsBuilderOpen(true); }}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {campaigns.map((campaign) => (
            <div
              key={campaign.id}
              className="glass-card p-6 rounded-2xl border border-border hover:border-brand-primary/30 transition-all cursor-pointer group hover:-translate-y-0.5"
              onClick={() => { setSelectedCampaign(campaign); setIsBuilderOpen(true); }}
            >
              <div className="flex justify-between items-start mb-4 gap-3">
                <h3 className="font-semibold text-lg text-text-primary group-hover:text-brand-primary transition-colors line-clamp-1">
                  {campaign.name}
                </h3>
                <Badge variant={campaign.is_active ? 'success' : 'default'} withDot>
                  {campaign.is_active ? t('campaigns.status.active') : t('campaigns.status.paused')}
                </Badge>
              </div>

              <div className="space-y-2.5 text-sm text-text-secondary pt-2 border-t border-border/50">
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4 text-text-muted" />
                  <span>{campaign.steps?.length || 0} {t('campaigns.status.steps')}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Play className="w-4 h-4 text-text-muted" />
                  <span className="font-mono text-xs">{campaign.trigger_type || 'manual_trigger'}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Builder Modal */}
      {isBuilderOpen && (
        <DripBuilder
          campaign={selectedCampaign}
          onClose={() => setIsBuilderOpen(false)}
        />
      )}
    </div>
  );
}
