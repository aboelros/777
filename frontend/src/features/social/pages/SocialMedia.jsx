import { useState, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Hash, MessageSquare, Send, Sparkles, Filter,
  Instagram, Facebook, AlertCircle, ThumbsUp, ThumbsDown,
  Clock, CheckCircle, XCircle, Globe, Calendar, Link2, Eye,
  Users, ExternalLink, Shield, Wifi, WifiOff, MessageCircle
} from 'lucide-react';
import { toast } from 'sonner';
import api from '../../../services/api';
import { useProjectStore } from '../../../store/projectStore';
import PostDetailDrawer from '../../../components/PostDetailDrawer';
import useThemeStore from '../../../store/themeStore';
import { useTranslation } from '../../../lib/translations';

export default function SocialMedia() {
  const queryClient = useQueryClient();
  const { currentProject } = useProjectStore();
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState('integrations'); // 'integrations', 'feed', or 'comments'
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [selectedPost, setSelectedPost] = useState(null);
  const [platformFilter, setPlatformFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [generatingFor, setGeneratingFor] = useState(null);

  // Fetch connected integrations (the real data source)
  const { data: integrationsData, isLoading: isLoadingIntegrations } = useQuery({
    queryKey: ['integrations', currentProject?.id],
    queryFn: () => api.integrations.list(currentProject.id),
    enabled: !!currentProject,
  });

  // Filter to only social integrations
  const socialIntegrations = useMemo(() => {
    const all = integrationsData || [];
    const list = Array.isArray(all) ? all : (all.integrations || all.data || []);
    return list.filter(i =>
      ['facebook', 'instagram', 'whatsapp', 'tiktok', 'telegram', 'discord'].includes(i.provider)
    );
  }, [integrationsData]);

  const connectedIntegrations = socialIntegrations.filter(i => i.status === 'connected');

  // Fetch Accounts (social media specific data)
  const { data: accountsData } = useQuery({
    queryKey: ['social-accounts', currentProject?.id],
    queryFn: () => api.socialMedia.getAccounts(currentProject.id),
    enabled: !!currentProject,
  });

  const accounts = accountsData?.accounts || [];

  // Fetch comments
  const { data: commentsData, isLoading: isLoadingComments } = useQuery({
    queryKey: ['social-comments', currentProject?.id, platformFilter, statusFilter, selectedAccount?.id],
    queryFn: async () => {
      const params = {};
      if (typeof platformFilter === 'string' && platformFilter !== 'all') params.platform = platformFilter;
      if (selectedAccount) params.platform = selectedAccount.platform;
      if (statusFilter !== 'all') params.responded = statusFilter === 'responded';
      return api.socialMedia.listComments(currentProject.id, params);
    },
    enabled: !!currentProject && activeTab === 'comments',
  });

  // Fetch feed
  const { data: feedData, isLoading: isLoadingFeed } = useQuery({
    queryKey: ['social-feed', currentProject?.id],
    queryFn: () => api.socialMedia.getFeed(currentProject.id),
    enabled: !!currentProject && activeTab === 'feed',
  });

  // Fetch stats
  const { data: statsData } = useQuery({
    queryKey: ['social-stats', currentProject?.id],
    queryFn: () => api.socialMedia.getStats(currentProject.id),
    enabled: !!currentProject,
  });

  const comments = commentsData?.comments || [];
  const stats = statsData || {};

  const filteredFeed = useMemo(() => {
    if (!feedData?.data) return [];
    if (!selectedAccount) return feedData.data;
    return feedData.data.filter(item =>
      item.platform === selectedAccount.platform &&
      (!item.account_name || !selectedAccount.name || item.account_name === selectedAccount.name)
    );
  }, [feedData, selectedAccount]);

  // Generate response mutation
  const generateMutation = useMutation({
    mutationFn: async (commentId) => {
      setGeneratingFor(commentId);
      return api.socialMedia.generateResponse(currentProject.id, commentId);
    },
    onSuccess: (data) => {
      toast.success(t('social.comments.sent') + '!');
      setGeneratingFor(null);
      const response = data.generated_response;
      if (confirm(t('social.comments.reply_modal').replace('{response}', response))) {
        sendMutation.mutate({ commentId: data.comment_id, text: response });
      }
    },
    onError: (error) => {
      setGeneratingFor(null);
      toast.error(error.response?.data?.detail || t('common.error'));
    },
  });

  // Send response mutation
  const sendMutation = useMutation({
    mutationFn: ({ commentId, text }) =>
      api.socialMedia.sendResponse(currentProject.id, commentId, text),
    onSuccess: () => {
      queryClient.invalidateQueries(['social-comments']);
      queryClient.invalidateQueries(['social-stats']);
      toast.success(t('social.comments.sent'));
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || t('common.error'));
    },
  });

  if (!currentProject) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 text-yellow-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold mb-2">{t('projects.no_projects')}</h2>
          <p className="text-gray-400">{t('projects.modal.subtitle')}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold mb-2">{t('social.title')}</h1>
          <p className="text-gray-400">{t('social.subtitle')}</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white/5 border border-white/10">
            <Wifi className="w-4 h-4 text-green-400" />
            <span className="text-sm text-gray-300">{connectedIntegrations.length} Connected</span>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-white/10 pb-4">
        {[
          { key: 'integrations', label: 'Connected Accounts', icon: Globe },
          { key: 'feed', label: t('social.tabs.feed'), icon: Eye },
          { key: 'comments', label: t('social.tabs.comments'), icon: MessageSquare },
        ].map(tab => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`flex items-center gap-2 px-5 py-2.5 rounded-xl transition-all text-sm font-medium ${activeTab === tab.key
              ? 'bg-gradient-to-r from-sky-600 to-sky-600 text-white shadow-lg shadow-sky-500/20'
              : 'bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white'
              }`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard
          title={t('social.stats.comments')}
          value={stats.total_comments || 0}
          icon={MessageSquare}
          color="from-blue-500 to-cyan-600"
        />
        <StatCard
          title={t('social.stats.pending')}
          value={stats.pending_responses || 0}
          icon={Clock}
          color="from-yellow-500 to-orange-600"
        />
        <StatCard
          title={t('social.stats.responded')}
          value={stats.responded || 0}
          icon={CheckCircle}
          color="from-green-500 to-emerald-600"
        />
        <StatCard
          title={t('social.stats.rate')}
          value={`${stats.response_rate || 0}%`}
          icon={Sparkles}
          color="from-sky-500 to-sky-600"
        />
      </div>

      {/* Content */}
      <AnimatePresence mode='wait'>
        {activeTab === 'integrations' && (
          <motion.div
            key="integrations"
            initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
            className="w-full space-y-6"
          >
            {isLoadingIntegrations ? (
              <div className="text-center py-20">
                <div className="loading-spinner mx-auto mb-4"></div>
                <p className="text-gray-400">Loading integrations...</p>
              </div>
            ) : socialIntegrations.length === 0 ? (
              <div className="text-center py-20">
                <Globe className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                <h3 className="text-xl font-semibold mb-2">No Social Integrations</h3>
                <p className="text-gray-400">
                  Go to Settings → Integrations to connect Instagram, Facebook, WhatsApp, or other platforms.
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {socialIntegrations.map((integration) => (
                  <IntegrationDetailCard
                    key={integration.id}
                    integration={integration}
                    account={accounts.find(a => a.id === integration.id)}
                  />
                ))}
              </div>
            )}
          </motion.div>
        )}

        {activeTab === 'feed' && (
          <motion.div
            key="feed"
            initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
            className="w-full"
          >
            {/* Account filter chips */}
            {accounts.length > 0 && (
              <div className="flex gap-3 mb-6 overflow-x-auto pb-2">
                <button
                  onClick={() => setSelectedAccount(null)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm whitespace-nowrap transition-all ${!selectedAccount
                      ? 'bg-gradient-to-r from-sky-600 to-sky-600 text-white'
                      : 'bg-white/5 text-gray-400 hover:bg-white/10'
                    }`}
                >
                  <Globe className="w-4 h-4" /> All Accounts
                </button>
                {accounts.map(acc => {
                  const Icon = getPlatformIcon(acc.platform);
                  return (
                    <button
                      key={acc.id}
                      onClick={() => setSelectedAccount(acc)}
                      className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm whitespace-nowrap transition-all ${selectedAccount?.id === acc.id
                          ? 'bg-gradient-to-r from-sky-600 to-sky-600 text-white'
                          : 'bg-white/5 text-gray-400 hover:bg-white/10'
                        }`}
                    >
                      {acc.profile_picture ? (
                        <img src={acc.profile_picture} alt="" className="w-5 h-5 rounded-full object-cover" />
                      ) : (
                        <Icon className="w-4 h-4" />
                      )}
                      {acc.name}
                    </button>
                  );
                })}
              </div>
            )}

            {isLoadingFeed ? (
              <div className="text-center py-20">
                <div className="loading-spinner mx-auto mb-4"></div>
                <p className="text-gray-400">{t('social.feed.loading')}</p>
              </div>
            ) : !filteredFeed || filteredFeed.length === 0 ? (
              <div className="text-center py-20">
                <Filter className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                <h3 className="text-xl font-semibold mb-2">{t('social.feed.no_items')}</h3>
                <p className="text-gray-400">{t('social.feed.connect_hint')}</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredFeed.map((item) => (
                  <FeedCard
                    key={item.id}
                    item={item}
                    onViewDetails={() => setSelectedPost(item)}
                    t={t}
                  />
                ))}
              </div>
            )}
          </motion.div>
        )}

        {activeTab === 'comments' && (
          <motion.div
            key="comments"
            initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
            className="w-full space-y-4"
          >
            {/* Filters */}
            <div className="glass-card p-4 rounded-xl">
              <div className="flex gap-4">
                <div className="flex-1">
                  <label className="block text-sm font-medium mb-2">{t('social.filters.platform')}</label>
                  <select
                    value={platformFilter}
                    onChange={(e) => setPlatformFilter(e.target.value)}
                    className="w-full bg-dark-800/50 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-sky-500"
                  >
                    <option value="all">{t('social.filters.all_platforms')}</option>
                    <option value="instagram">Instagram</option>
                    <option value="facebook">Facebook</option>
                    <option value="tiktok">TikTok</option>
                  </select>
                </div>
                <div className="flex-1">
                  <label className="block text-sm font-medium mb-2">{t('social.filters.status')}</label>
                  <select
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                    className="w-full bg-dark-800/50 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-sky-500"
                  >
                    <option value="all">{t('social.filters.all_status')}</option>
                    <option value="pending">{t('social.filters.pending')}</option>
                    <option value="responded">{t('social.filters.responded')}</option>
                  </select>
                </div>
              </div>
            </div>

            {isLoadingComments ? (
              <div className="text-center py-20">
                <div className="loading-spinner mx-auto mb-4"></div>
                <p className="text-gray-400">{t('social.comments.loading')}</p>
              </div>
            ) : comments.length === 0 ? (
              <div className="text-center py-20">
                <MessageSquare className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                <h3 className="text-xl font-semibold mb-2">{t('social.comments.no_comments')}</h3>
                <p className="text-gray-400">{t('social.comments.hint')}</p>
              </div>
            ) : (
              <div className="space-y-4">
                {comments.map((comment) => (
                  <CommentCard
                    key={comment.id}
                    comment={comment}
                    onGenerateResponse={() => generateMutation.mutate(comment.id)}
                    isGenerating={generatingFor === comment.id}
                    t={t}
                  />
                ))}
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Post Detail Drawer */}
      <PostDetailDrawer
        isOpen={!!selectedPost}
        onClose={() => setSelectedPost(null)}
        post={selectedPost}
        projectId={currentProject?.id}
      />
    </div>
  );
}

// ─── Helpers ───────────────────────────────────────────────────

function getPlatformIcon(platform) {
  switch (platform) {
    case 'facebook': return Facebook;
    case 'instagram': return Instagram;
    case 'whatsapp': return MessageCircle;
    case 'tiktok': return Hash;
    case 'telegram': return Send;
    case 'discord': return Hash;
    default: return Globe;
  }
}

function getPlatformGradient(platform) {
  switch (platform) {
    case 'facebook': return 'from-blue-600 to-blue-700';
    case 'instagram': return 'from-sky-500 via-sky-500 to-orange-400';
    case 'whatsapp': return 'from-green-500 to-emerald-600';
    case 'tiktok': return 'from-slate-800 to-black';
    case 'telegram': return 'from-sky-400 to-blue-500';
    case 'discord': return 'from-indigo-500 to-sky-600';
    default: return 'from-gray-600 to-gray-700';
  }
}

function getPlatformLabel(provider) {
  switch (provider) {
    case 'facebook': return 'Facebook Page';
    case 'instagram': return 'Instagram Business';
    case 'whatsapp': return 'WhatsApp';
    case 'tiktok': return 'TikTok Shop';
    case 'telegram': return 'Telegram Bot';
    case 'discord': return 'Discord Bot';
    default: return provider;
  }
}

// ─── Connected Integration Detail Card ─────────────────────────

function IntegrationDetailCard({ integration, account }) {
  const Icon = getPlatformIcon(integration.provider);
  const gradient = getPlatformGradient(integration.provider);
  const isConnected = integration.status === 'connected';
  const config = integration.config || {};
  const extra = integration.extra_data || {};

  // Extract display info
  const pageName = config.page_name || config.instagram_username || config.phone_number || config.shop_name || config.bot_username || account?.name || getPlatformLabel(integration.provider);
  const pageId = config.page_id || config.instagram_business_account_id || config.phone_number_id || config.shop_id || config.bot_id || null;
  const username = config.instagram_username || config.bot_username || null;
  const profilePic = account?.profile_picture || config.profile_picture_url || (config.page_id ? `https://graph.facebook.com/${config.page_id}/picture?type=large` : null);
  const connectedAt = integration.created_at ? new Date(integration.created_at) : null;
  const lastSync = integration.last_sync ? new Date(integration.last_sync) : null;
  const errorMsg = integration.error_message;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="relative overflow-hidden rounded-2xl border border-white/10 bg-white/[0.03] backdrop-blur-sm hover:border-white/20 transition-all group"
    >
      {/* Gradient header bar */}
      <div className={`h-24 bg-gradient-to-r ${gradient} relative overflow-hidden`}>
        <div className="absolute inset-0 bg-black/20" />
        <Icon className="absolute -right-6 -top-6 w-32 h-32 text-white/10 rotate-12" />

        {/* Status badge */}
        <div className="absolute top-4 right-4">
          <div className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold backdrop-blur-sm ${isConnected
              ? 'bg-green-500/20 text-green-300 border border-green-400/30'
              : 'bg-red-500/20 text-red-300 border border-red-400/30'
            }`}>
            {isConnected ? <Wifi className="w-3 h-3" /> : <WifiOff className="w-3 h-3" />}
            {isConnected ? 'Connected' : 'Disconnected'}
          </div>
        </div>
      </div>

      {/* Profile section */}
      <div className="px-6 -mt-10 relative z-10">
        <div className="flex items-end gap-4">
          {/* Profile picture */}
          <div className="w-20 h-20 rounded-2xl overflow-hidden border-4 border-dark-950 bg-dark-800 shadow-xl flex-shrink-0">
            {profilePic ? (
              <img
                src={profilePic}
                alt={pageName}
                className="w-full h-full object-cover"
                onError={(e) => {
                  e.target.style.display = 'none';
                  e.target.parentElement.querySelector('.fallback-icon')?.classList.remove('hidden');
                }}
              />
            ) : null}
            <div className={`fallback-icon w-full h-full bg-gradient-to-br ${gradient} flex items-center justify-center ${profilePic ? 'hidden' : ''}`}>
              <Icon className="w-8 h-8 text-white" />
            </div>
          </div>

          {/* Name + platform */}
          <div className="pb-1 min-w-0 flex-1">
            <h3 className="text-lg font-bold text-white truncate">{pageName}</h3>
            <p className="text-sm text-gray-400 flex items-center gap-1.5">
              <Icon className="w-3.5 h-3.5" />
              {getPlatformLabel(integration.provider)}
            </p>
          </div>
        </div>
      </div>

      {/* Details */}
      <div className="px-6 py-5 space-y-3">
        {/* Info grid */}
        <div className="grid grid-cols-2 gap-3">
          {username && (
            <InfoItem icon={Users} label="Username" value={`@${username}`} />
          )}
          {pageId && (
            <InfoItem icon={Shield} label="ID" value={pageId} truncate />
          )}
          {connectedAt && (
            <InfoItem icon={Calendar} label="Connected" value={connectedAt.toLocaleDateString()} />
          )}
          {lastSync && (
            <InfoItem icon={Clock} label="Last Sync" value={formatTimeAgo(lastSync)} />
          )}
        </div>

        {/* Error message */}
        {errorMsg && (
          <div className="flex items-start gap-2 p-3 rounded-xl bg-red-500/10 border border-red-500/20">
            <AlertCircle className="w-4 h-4 text-red-400 mt-0.5 flex-shrink-0" />
            <p className="text-xs text-red-300 break-all">{errorMsg}</p>
          </div>
        )}

        {/* Config details (non-sensitive) */}
        {integration.provider === 'facebook' && config.page_name && (
          <div className="flex items-center gap-2 p-3 rounded-xl bg-blue-500/5 border border-blue-500/10">
            <Facebook className="w-4 h-4 text-blue-400" />
            <span className="text-sm text-gray-300">Page: <span className="text-white font-medium">{config.page_name}</span></span>
          </div>
        )}

        {integration.provider === 'instagram' && config.instagram_username && (
          <div className="flex items-center gap-2 p-3 rounded-xl bg-sky-500/5 border border-sky-500/10">
            <Instagram className="w-4 h-4 text-sky-400" />
            <span className="text-sm text-gray-300">@{config.instagram_username}</span>
          </div>
        )}

        {integration.provider === 'whatsapp' && config.phone_number && (
          <div className="flex items-center gap-2 p-3 rounded-xl bg-green-500/5 border border-green-500/10">
            <MessageCircle className="w-4 h-4 text-green-400" />
            <span className="text-sm text-gray-300">{config.phone_number}</span>
          </div>
        )}
      </div>
    </motion.div>
  );
}

function InfoItem({ icon: Icon, label, value, truncate }) {
  return (
    <div className="flex items-center gap-2 min-w-0">
      <Icon className="w-3.5 h-3.5 text-gray-500 flex-shrink-0" />
      <div className="min-w-0">
        <p className="text-[10px] uppercase tracking-wider text-gray-500">{label}</p>
        <p className={`text-sm text-gray-300 ${truncate ? 'truncate' : ''}`} title={value}>{value}</p>
      </div>
    </div>
  );
}

function formatTimeAgo(date) {
  const seconds = Math.floor((new Date() - date) / 1000);
  if (seconds < 60) return 'Just now';
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
  return date.toLocaleDateString();
}

// ─── Existing Components ───────────────────────────────────────

function FeedCard({ item, onViewDetails, t }) {
  const PlatformIcon = item.platform === 'facebook' ? Facebook : Instagram;
  const platformColor = item.platform === 'facebook' ? 'from-blue-600 to-blue-700' : 'from-sky-600 to-sky-600';

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="glass-card overflow-hidden rounded-2xl border border-white/10 hover:border-sky-500/30 transition-all group flex flex-col h-full"
    >
      <div className="relative aspect-square overflow-hidden bg-dark-900 group-cursor-pointer" onClick={onViewDetails}>
        {item.full_picture ? (
          <img
            src={item.full_picture}
            alt="Feed content"
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500 cursor-pointer"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-600">{t('social.drawer.no_media')}</div>
        )}
        <div className={`absolute top-4 left-4 w-10 h-10 rounded-lg bg-gradient-to-br ${platformColor} flex items-center justify-center shadow-lg`}>
          <PlatformIcon className="w-5 h-5 text-white" />
        </div>
      </div>

      <div className="p-5 flex flex-col flex-1">
        <div className="flex items-center gap-2 mb-3">
          <p className="text-sm font-semibold text-white">{item.account_name}</p>
          <span className="text-xs text-gray-500 opacity-50">•</span>
          <p className="text-xs text-gray-500">
            {item.created_time ? new Date(item.created_time).toLocaleDateString() : 'Recent'}
          </p>
        </div>

        <p className="text-gray-300 text-sm line-clamp-3 mb-4 flex-1">
          {item.message || item.caption || 'No caption'}
        </p>

        <div className="flex items-center justify-between mt-auto pt-4 border-t border-white/5">
          <div className="flex gap-4 text-xs text-gray-400">
            <span className="flex items-center gap-1"><ThumbsUp className="w-3 h-3" /> {item.likes_count || 0}</span>
            <span className="flex items-center gap-1"><MessageSquare className="w-3 h-3" /> {item.comments_count || 0}</span>
          </div>

          <button
            onClick={onViewDetails}
            className="text-xs px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 transition-colors"
          >
            {t('social.feed.view_details')}
          </button>
        </div>
      </div>
    </motion.div>
  );
}

function StatCard({ title, value, icon: Icon, color }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card p-5 rounded-xl"
    >
      <div className="flex items-center justify-between mb-3">
        <div className={`w-11 h-11 rounded-xl bg-gradient-to-br ${color} flex items-center justify-center`}>
          <Icon className="w-5 h-5 text-white" />
        </div>
      </div>
      <div>
        <p className="text-2xl font-bold mb-0.5">{value}</p>
        <p className="text-sm text-gray-400">{title}</p>
      </div>
    </motion.div>
  );
}

function CommentCard({ comment, onGenerateResponse, isGenerating, t }) {
  const platformIcons = {
    instagram: Instagram,
    facebook: Facebook,
    tiktok: Hash,
  };

  const platformColors = {
    instagram: 'from-sky-500 to-sky-600',
    facebook: 'from-blue-500 to-blue-600',
    tiktok: 'from-cyan-500 to-blue-600',
  };

  const sentimentIcons = {
    positive: ThumbsUp,
    negative: ThumbsDown,
    neutral: MessageSquare,
  };

  const PlatformIcon = platformIcons[comment.platform] || Hash;
  const SentimentIcon = sentimentIcons[comment.sentiment] || MessageSquare;
  const platformColor = platformColors[comment.platform] || 'from-gray-500 to-gray-600';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card p-6 rounded-xl"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${platformColor} flex items-center justify-center`}>
            <PlatformIcon className="w-6 h-6 text-white" />
          </div>
          <div>
            <p className="font-semibold">{comment.author_username || t('social.accounts.unnamed')}</p>
            <p className="text-sm text-gray-400">{comment.platform}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {comment.sentiment && (
            <div className={`px-3 py-1 rounded-full text-xs font-medium ${comment.sentiment === 'positive' ? 'bg-green-500/20 text-green-400' :
              comment.sentiment === 'negative' ? 'bg-red-500/20 text-red-400' :
                'bg-gray-500/20 text-gray-400'
              }`}>
              <SentimentIcon className="w-3 h-3 inline mr-1" />
              {comment.sentiment}
            </div>
          )}
          {comment.responded ? (
            <div className="px-3 py-1 rounded-full text-xs font-medium bg-green-500/20 text-green-400">
              <CheckCircle className="w-3 h-3 inline mr-1" />
              {t('social.filters.responded')}
            </div>
          ) : (
            <div className="px-3 py-1 rounded-full text-xs font-medium bg-yellow-500/20 text-yellow-400">
              <Clock className="w-3 h-3 inline mr-1" />
              {t('social.filters.pending')}
            </div>
          )}
        </div>
      </div>

      <div className="mb-4">
        <p className="text-gray-300">{comment.content}</p>
        {comment.intent && (
          <p className="text-sm text-gray-500 mt-2">{t('social.comments.intent')}: {comment.intent}</p>
        )}
      </div>

      {comment.responded && comment.response_content && (
        <div className="glass-card p-4 rounded-lg mb-4 border border-green-500/30">
          <p className="text-sm text-gray-400 mb-2">{t('social.comments.response')}:</p>
          <p className="text-green-400">{comment.response_content}</p>
          {comment.response_sent_at && (
            <p className="text-xs text-gray-500 mt-2">
              {t('social.comments.sent')}: {new Date(comment.response_sent_at).toLocaleString()}
            </p>
          )}
        </div>
      )}

      {!comment.responded && (
        <div className="flex gap-2">
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={onGenerateResponse}
            disabled={isGenerating}
            className="flex-1 btn-neon flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {isGenerating ? (
              <>
                <div className="loading-spinner w-4 h-4"></div>
                {t('social.comments.generating')}
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                {t('social.comments.generate')}
              </>
            )}
          </motion.button>
        </div>
      )}
    </motion.div>
  );
}
