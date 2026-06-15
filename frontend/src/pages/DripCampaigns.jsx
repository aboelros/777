import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
    GitBranch, Plus, Play, Pause, Clock
} from 'lucide-react';
import { toast } from 'sonner';
import api from '../services/api';
import { useProjectStore } from '../store/projectStore';
import DripBuilder from '../components/DripBuilder';
import useThemeStore from '../store/themeStore';
import { useTranslation } from '../lib/translations';

export default function DripCampaigns() {
    const { currentProject } = useProjectStore();
    const { t } = useTranslation();
    const [isBuilderOpen, setIsBuilderOpen] = useState(false);
    const [selectedCampaign, setSelectedCampaign] = useState(null);

    const { data: campaigns = [], isLoading } = useQuery({
        queryKey: ['drip-campaigns', currentProject?.id],
        queryFn: () => api.dripCampaigns.getCampaigns(currentProject.id),
        enabled: !!currentProject
    });

    if (!currentProject) return null;

    return (
        <div className="h-full flex flex-col p-6 max-w-7xl mx-auto space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold flex items-center gap-3">
                        <GitBranch className="w-8 h-8 text-accent-500" />
                        {t('campaigns.title')}
                    </h1>
                    <p className="text-gray-400">{t('campaigns.subtitle')}</p>
                </div>
                <button
                    onClick={() => { setSelectedCampaign(null); setIsBuilderOpen(true); }}
                    className="btn-primary flex items-center gap-2"
                >
                    <Plus className="w-4 h-4" /> {t('campaigns.new')}
                </button>
            </div>

            {/* Campaign Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {campaigns.map(campaign => (
                    <div
                        key={campaign.id}
                        className="glass-card p-6 rounded-xl hover:border-accent-500/30 transition-all cursor-pointer group"
                        onClick={() => { setSelectedCampaign(campaign); setIsBuilderOpen(true); }}
                    >
                        <div className="flex justify-between items-start mb-4">
                            <h3 className="font-semibold text-lg">{campaign.name}</h3>
                            <span className={`px-2 py-0.5 text-xs rounded-full ${campaign.is_active ? 'bg-green-500/10 text-green-400' : 'bg-gray-500/10 text-gray-400'}`}>
                                {campaign.is_active ? t('campaigns.status.active') : t('campaigns.status.paused')}
                            </span>
                        </div>

                        <div className="space-y-2 text-sm text-gray-400">
                            <div className="flex items-center gap-2">
                                <Clock className="w-4 h-4" />
                                <span>{campaign.steps?.length || 0} {t('campaigns.status.steps')}</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <Play className="w-4 h-4" />
                                <span>{campaign.trigger_type}</span>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Builder Modal (Drawer) */}
            {isBuilderOpen && (
                <DripBuilder
                    campaign={selectedCampaign}
                    onClose={() => setIsBuilderOpen(false)}
                />
            )}
        </div>
    );
}
