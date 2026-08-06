import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
    LayoutDashboard, Plus, Search, Filter
} from 'lucide-react';
import { toast } from 'sonner';
import api from '../../../services/api';
import { useProjectStore } from '../../../store/projectStore';
import useThemeStore from '../../../store/themeStore';
import { useTranslation } from '../../../lib/translations';
import KanbanBoard from '../../../components/KanbanBoard';
import Button from '../../../components/ui/Button';
import ApiErrorState from '../../../components/ApiErrorState';
import SkeletonLoader from '../../../components/ui/SkeletonLoader';
import CreateDealModal from '../../../components/CreateDealModal';

export default function Deals() {
    const { currentProject } = useProjectStore();
    const queryClient = useQueryClient();
    const { t } = useTranslation();
    const [view, setView] = useState('kanban');

    const { data: stages = [], isLoading: stagesLoading, error: stagesError, refetch: refetchStages } = useQuery({
        queryKey: ['pipeline-stages', currentProject?.id],
        queryFn: () => api.deals.getStages(currentProject.id),
        enabled: !!currentProject,
        retry: 1,
    });

    const { data: deals = [], isLoading: dealsLoading, error: dealsError, refetch: refetchDeals } = useQuery({
        queryKey: ['deals', currentProject?.id],
        queryFn: () => api.deals.getDeals(currentProject.id),
        enabled: !!currentProject,
        retry: 1,
    });

    const moveDealMutation = useMutation({
        mutationFn: ({ dealId, stageId }) =>
            api.deals.updateDeal(currentProject.id, dealId, { stage_id: stageId }),
        onSuccess: () => {
            // Optimistic update could go here, but invalidate is safer for MVP
            queryClient.invalidateQueries(['deals']);
        },
        onError: () => toast.error(t('deals.move_error'))
    });

    const [showCreateModal, setShowCreateModal] = useState(false);
    const [selectedStageId, setSelectedStageId] = useState(null);

    const handleDealMove = (dealId, stageId) => {
        moveDealMutation.mutate({ dealId, stageId });
    };

    const addDealMutation = useMutation({
        mutationFn: (data) => api.deals.createDeal(currentProject.id, data),
        onSuccess: () => {
            queryClient.invalidateQueries(['deals']);
            setShowCreateModal(false);
            toast.success(t('common.save'));
        },
        onError: (error) => toast.error(error.response?.data?.detail || t('common.error'))
    });

    const handleAddDeal = (stageId) => {
        setSelectedStageId(stageId);
        setShowCreateModal(true);
    };

    const handleSubmitDeal = (data) => {
        addDealMutation.mutate(data);
    };

    if (!currentProject) return null;

    return (
        <div className="h-full flex flex-col p-6 overflow-hidden">
            {/* Header */}
            <div className="flex items-center justify-between mb-6 flex-shrink-0">
                <div>
                    <h1 className="text-3xl font-bold flex items-center gap-3 text-primary">
                        <LayoutDashboard className="w-8 h-8 text-accent-500" />
                        {t('deals.title')}
                    </h1>
                    <p className="text-secondary">{t('deals.description')}</p>
                </div>
                <div className="flex gap-3">
                    <Button
                        variant="secondary"
                        leftIcon={Filter}
                    >
                        {t('deals.filter')}
                    </Button>
                    <Button
                        variant="primary"
                        leftIcon={Plus}
                        onClick={() => handleAddDeal(stages[0]?.id)}
                    >
                        {t('deals.new_deal')}
                    </Button>
                </div>
            </div>

            {/* Content */}
            <div className="flex-1 min-h-0 bg-dark-900/50 rounded-2xl border border-white/5 overflow-hidden">
                {stagesLoading || dealsLoading ? (
                    <div className="h-full flex items-center justify-center p-8">
                        <SkeletonLoader type="card" count={3} className="w-full" />
                    </div>
                ) : stagesError || dealsError ? (
                    <div className="h-full flex items-center justify-center p-8">
                        <ApiErrorState
                            error={stagesError || dealsError}
                            onRetry={() => {
                                if (stagesError) refetchStages();
                                if (dealsError) refetchDeals();
                            }}
                            title="Failed to load pipeline"
                        />
                    </div>
                ) : stages.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-gray-500">
                        <p>{t('deals.no_stages')}</p>
                        <button className="mt-4 text-sky-400 hover:underline">{t('deals.configure_pipeline')}</button>
                    </div>
                ) : (
                    <KanbanBoard
                        stages={stages}
                        deals={deals}
                        onDealMove={handleDealMove}
                        onAddDeal={handleAddDeal}
                    />
                )}
            </div>

            <CreateDealModal
                isOpen={showCreateModal}
                onClose={() => setShowCreateModal(false)}
                onSubmit={handleSubmitDeal}
                initialStageId={selectedStageId}
                stages={stages}
            />
        </div>
    );
}
