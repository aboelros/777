import { useState, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Share2, Globe, Eye, MessageSquare, Wifi } from 'lucide-react';
import { toast } from 'sonner';
import api from '@/services/api';
import { useProjectStore } from '@/store/projectStore';
import { useTranslation } from '@/lib/translations';
import { NoProjectState } from '@/components/ui/EmptyState';
import Badge from '@/components/ui/Badge';
import SocialStatCards from '../components/SocialStatCards';
import IntegrationDetailCard from '../components/IntegrationDetailCard';
import SocialCommentsTab from '../components/SocialCommentsTab';
import SocialFeedTab from '../components/SocialFeedTab';
import PostDetailDrawer from '@/components/PostDetailDrawer';

export default function SocialMedia() {
  const queryClient = useQueryClient();
  const { currentProject } = useProjectStore();
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState('integrations');
  const [selectedPost, setSelectedPost] = useState(null);
  const [generatingFor, setGeneratingFor] = useState(null);

  const { data: integrationsData, isLoading: isLoadingIntegrations } = useQuery({
    queryKey: ['integrations', currentProject?.id],
    queryFn: () => api.integrations.list(currentProject.id),
    enabled: !!currentProject?.id,
  });

  const socialIntegrations = useMemo(() => {
    const all = integrationsData || [];
    const list = Array.isArray(all) ? all : (all.integrations || all.data || []);
    return list.filter((i) =>
      ['facebook', 'instagram', 'whatsapp', 'tiktok', 'telegram', 'discord'].includes(i.provider)
    );
  }, [integrationsData]);

  const connectedIntegrations = socialIntegrations.filter((i) => i.status === 'connected');

  const { data: commentsData, isLoading: isLoadingComments } = useQuery({
    queryKey: ['social-comments', currentProject?.id],
    queryFn: () => api.socialMedia.listComments(currentProject.id, {}),
    enabled: !!currentProject?.id && activeTab === 'comments',
  });

  const { data: feedData, isLoading: isLoadingFeed } = useQuery({
    queryKey: ['social-feed', currentProject?.id],
    queryFn: () => api.socialMedia.getFeed(currentProject.id),
    enabled: !!currentProject?.id && activeTab === 'feed',
  });

  const { data: statsData } = useQuery({
    queryKey: ['social-stats', currentProject?.id],
    queryFn: () => api.socialMedia.getStats(currentProject.id),
    enabled: !!currentProject?.id,
  });

  const generateMutation = useMutation({
    mutationFn: async (commentId) => {
      setGeneratingFor(commentId);
      return api.socialMedia.generateResponse(currentProject.id, commentId);
    },
    onSuccess: (data) => {
      toast.success(t('social.comments.sent') || 'Response generated');
      setGeneratingFor(null);
      queryClient.invalidateQueries(['social-comments']);
    },
    onError: (error) => {
      setGeneratingFor(null);
      toast.error(error.response?.data?.detail || 'Failed to generate response');
    },
  });

  if (!currentProject) {
    return <NoProjectState subtitle={t('social.subtitle') || 'Select a project to orchestrate social messaging channels and feeds'} />;
  }

  const tabs = [
    { key: 'integrations', label: 'Connected Channels', icon: Globe },
    { key: 'feed', label: t('social.tabs.feed') || 'Post Feeds', icon: Eye },
    { key: 'comments', label: t('social.tabs.comments') || 'Comments & Triage', icon: MessageSquare },
  ];

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3 text-text-primary tracking-tight">
            <span className="p-2.5 rounded-xl bg-brand-primary/10 border border-brand-primary/20 text-brand-primary">
              <Share2 className="w-6 h-6" />
            </span>
            {t('social.title') || 'Omnichannel Social Operations'}
          </h1>
          <p className="text-sm text-text-secondary mt-1">{t('social.subtitle')}</p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant={connectedIntegrations.length > 0 ? 'success' : 'default'} withDot>
            {connectedIntegrations.length} Active Feeds
          </Badge>
        </div>
      </div>

      {/* KPI Stats */}
      <SocialStatCards stats={statsData || {}} />

      {/* Tab Navigation */}
      <div className="flex gap-2 border-b border-border pb-3 overflow-x-auto">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.key;
          return (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition-all ${
                isActive
                  ? 'bg-brand-primary text-white shadow-sm'
                  : 'bg-surface-subtle text-text-muted hover:text-text-primary hover:bg-surface-hover'
              }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Active Tab View */}
      {activeTab === 'integrations' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {socialIntegrations.map((integration) => (
            <IntegrationDetailCard key={integration.id} integration={integration} />
          ))}
        </div>
      )}

      {activeTab === 'feed' && (
        <SocialFeedTab
          feed={feedData?.data || []}
          isLoading={isLoadingFeed}
          onSelectPost={(post) => setSelectedPost(post)}
        />
      )}

      {activeTab === 'comments' && (
        <SocialCommentsTab
          comments={commentsData?.comments || []}
          isLoading={isLoadingComments}
          onGenerateResponse={(id) => generateMutation.mutate(id)}
          generatingFor={generatingFor}
        />
      )}

      {selectedPost && (
        <PostDetailDrawer
          post={selectedPost}
          onClose={() => setSelectedPost(null)}
        />
      )}
    </div>
  );
}
