import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Plus,
  Edit,
  Trash2,
  Save,
  X,
  RefreshCw,
  Check,
  AlertCircle,
  Settings as SettingsIcon,
  Key,
  Link as LinkIcon,
  Power
} from 'lucide-react';
import { toast } from 'sonner';
import GlassCard from '../components/GlassCard';
import api from '../services/api';
import { useProjectStore } from '../store/projectStore';

export default function IntegrationsManagement() {
  const { currentProject } = useProjectStore();
  const queryClient = useQueryClient();

  const [showAddModal, setShowAddModal] = useState(false);
  const [editingIntegration, setEditingIntegration] = useState(null);
  const [formData, setFormData] = useState({
    provider: '',
    name: '',
    apiKey: '',
    apiSecret: '',
    webhookUrl: '',
    config: {}
  });

  // Fetch integrations
  const { data: integrationsData, isLoading } = useQuery({
    queryKey: ['integrations', currentProject?.id],
    queryFn: () => api.integrations.list(currentProject?.id),
    enabled: !!currentProject,
  });

  const integrations = integrationsData?.data || [];

  // Create mutation
  const createMutation = useMutation({
    mutationFn: (data) => api.integrations.create(currentProject?.id, data),
    onSuccess: () => {
      toast.success('Integration created successfully!');
      queryClient.invalidateQueries(['integrations']);
      resetForm();
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Failed to create integration');
    },
  });

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => api.integrations.update(currentProject?.id, id, data),
    onSuccess: () => {
      toast.success('Integration updated successfully!');
      queryClient.invalidateQueries(['integrations']);
      setEditingIntegration(null);
      resetForm();
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Failed to update integration');
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id) => api.integrations.delete(currentProject?.id, id),
    onSuccess: () => {
      toast.success('Integration deleted successfully!');
      queryClient.invalidateQueries(['integrations']);
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Failed to delete integration');
    },
  });

  // Test mutation
  const testMutation = useMutation({
    mutationFn: (id) => api.integrations.test(currentProject?.id, id),
    onSuccess: () => {
      toast.success('Integration test successful!');
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Integration test failed');
    },
  });

  // Sync mutation
  const syncMutation = useMutation({
    mutationFn: (id) => api.integrations.sync(currentProject?.id, id),
    onSuccess: () => {
      toast.success('Sync started successfully!');
      queryClient.invalidateQueries(['integrations']);
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Sync failed');
    },
  });

  const resetForm = () => {
    setFormData({
      provider: '',
      name: '',
      apiKey: '',
      apiSecret: '',
      webhookUrl: '',
      config: {}
    });
    setShowAddModal(false);
    setEditingIntegration(null);
  };

  const handleEdit = (integration) => {
    setEditingIntegration(integration);
    setFormData({
      provider: integration.provider,
      name: integration.name || '',
      apiKey: '••••••••', // Masked for security
      apiSecret: '••••••••',
      webhookUrl: integration.webhook_url || '',
      config: integration.config || {}
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!formData.provider || !formData.apiKey) {
      toast.error('Provider and API Key are required');
      return;
    }

    const data = {
      provider: formData.provider,
      name: formData.name || formData.provider,
      credentials: {
        api_key: formData.apiKey,
        api_secret: formData.apiSecret,
        webhook_url: formData.webhookUrl,
      },
      config: { ...formData.config }, // Base config
    };

    // Correctly structure nested settings for specific providers
    if (formData.provider === 'discord' && formData.config && formData.config.guild_id) {
      data.config.discord_settings = {
        guild_id: formData.config.guild_id
      };
    }

    if (formData.provider === 'tiktok') {
      data.config.tiktok_settings = {};
      if (formData.config?.shop_id) data.config.tiktok_settings.shop_id = formData.config.shop_id;
      if (formData.config?.access_token) data.config.tiktok_settings.access_token = formData.config.access_token;
      if (formData.apiKey) data.config.tiktok_settings.app_key = formData.apiKey; // Map API Key to App Key
    }

    if (editingIntegration) {
      updateMutation.mutate({ id: editingIntegration.id, data });
    } else {
      createMutation.mutate(data);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'connected':
        return 'text-green-400 bg-green-400/10';
      case 'error':
        return 'text-red-400 bg-red-400/10';
      case 'syncing':
        return 'text-blue-400 bg-blue-400/10';
      default:
        return 'text-gray-400 bg-gray-400/10';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8 flex items-center justify-between"
        >
          <div>
            <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-sky-400 to-sky-400 mb-2">
              Integrations Manager
            </h1>
            <p className="text-slate-400">Manage your platform integrations and API connections</p>
          </div>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setShowAddModal(true)}
            disabled={!currentProject}
            className="px-6 py-3 bg-gradient-to-r from-blue-500 to-sky-500 text-white rounded-lg font-medium flex items-center gap-2 hover:shadow-lg hover:shadow-blue-500/50 transition-all disabled:opacity-50"
          >
            <Plus className="w-5 h-5" />
            Add Integration
          </motion.button>
        </motion.div>

        {/* Integrations List */}
        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin w-12 h-12 border-4 border-sky-500 border-t-transparent rounded-full" />
          </div>
        ) : integrations.length === 0 ? (
          <GlassCard className="p-12 text-center">
            <LinkIcon className="w-16 h-16 text-slate-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-slate-300 mb-2">No integrations yet</h3>
            <p className="text-slate-400 mb-6">Get started by adding your first integration</p>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setShowAddModal(true)}
              className="px-6 py-3 bg-gradient-to-r from-blue-500 to-sky-500 text-white rounded-lg font-medium"
            >
              <Plus className="w-5 h-5 inline mr-2" />
              Add Integration
            </motion.button>
          </GlassCard>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <AnimatePresence>
              {integrations.map((integration, index) => (
                <motion.div
                  key={integration.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <GlassCard className="p-6 hover:shadow-lg hover:shadow-sky-500/20 transition-all">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-sky-600 flex items-center justify-center">
                          <LinkIcon className="w-6 h-6 text-white" />
                        </div>
                        <div>
                          <h3 className="text-lg font-semibold text-white">{integration.name || integration.provider}</h3>
                          <p className="text-sm text-slate-400 capitalize">{integration.provider}</p>
                        </div>
                      </div>
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(integration.status)}`}>
                        {integration.status}
                      </span>
                    </div>

                    {/* Details */}
                    <div className="space-y-2 mb-4 text-sm">
                      {integration.webhook_url && (
                        <div className="flex items-center gap-2 text-slate-400">
                          <Key className="w-4 h-4" />
                          <span className="truncate">{integration.webhook_url}</span>
                        </div>
                      )}
                      {integration.last_sync && (
                        <div className="flex items-center gap-2 text-slate-400">
                          <RefreshCw className="w-4 h-4" />
                          <span>Last sync: {new Date(integration.last_sync).toLocaleString()}</span>
                        </div>
                      )}
                    </div>

                    {/* Actions */}
                    <div className="flex gap-2">
                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => syncMutation.mutate(integration.id)}
                        disabled={syncMutation.isPending}
                        className="flex-1 px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white hover:bg-white/10 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                      >
                        <RefreshCw className={`w-4 h-4 ${syncMutation.isPending ? 'animate-spin' : ''}`} />
                        Sync
                      </motion.button>
                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => testMutation.mutate(integration.id)}
                        disabled={testMutation.isPending}
                        className="flex-1 px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white hover:bg-white/10 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                      >
                        <Power className="w-4 h-4" />
                        Test
                      </motion.button>
                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => handleEdit(integration)}
                        className="px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white hover:bg-white/10 transition-all"
                      >
                        <Edit className="w-4 h-4" />
                      </motion.button>
                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => {
                          if (confirm('Are you sure you want to delete this integration?')) {
                            deleteMutation.mutate(integration.id);
                          }
                        }}
                        className="px-3 py-2 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 hover:bg-red-500/20 transition-all"
                      >
                        <Trash2 className="w-4 h-4" />
                      </motion.button>
                    </div>
                  </GlassCard>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}

        {/* Add/Edit Modal */}
        {(showAddModal || editingIntegration) && (
          <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="glass-card p-6 max-w-2xl w-full rounded-2xl max-h-[90vh] overflow-y-auto"
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-semibold text-white">
                  {editingIntegration ? 'Edit Integration' : 'Add New Integration'}
                </h2>
                <button
                  onClick={resetForm}
                  className="text-slate-400 hover:text-white transition-colors"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Provider *
                    </label>
                    <select
                      value={formData.provider}
                      onChange={(e) => setFormData({ ...formData, provider: e.target.value })}
                      className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-sky-500/50"
                      required
                    >
                      <option value="">Select provider</option>
                      <option value="shopify">Shopify</option>
                      <option value="whatsapp">WhatsApp</option>
                      <option value="telegram">Telegram</option>
                      <option value="facebook">Facebook</option>
                      <option value="instagram">Instagram</option>
                      <option value="discord">Discord</option>
                      <option value="tiktok">TikTok</option>
                      <option value="custom">Custom</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Display Name
                    </label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      placeholder="My Integration"
                      className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-sky-500/50"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    API Key *
                  </label>
                  <input
                    type="text"
                    value={formData.apiKey}
                    onChange={(e) => setFormData({ ...formData, apiKey: e.target.value })}
                    placeholder="Enter your API key"
                    className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-sky-500/50"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    API Secret (optional)
                  </label>
                  <input
                    type="password"
                    value={formData.apiSecret}
                    onChange={(e) => setFormData({ ...formData, apiSecret: e.target.value })}
                    placeholder="Enter your API secret"
                    className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-sky-500/50"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Webhook URL (optional)
                  </label>
                  <input
                    type="url"
                    value={formData.webhookUrl}
                    onChange={(e) => setFormData({ ...formData, webhookUrl: e.target.value })}
                    placeholder="https://your-domain.com/webhook"
                    className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-sky-500/50"
                  />
                </div>

                {/* Provider Specific Config */}
                {formData.provider === 'discord' && (
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Guild ID (Server ID) *
                    </label>
                    <input
                      type="text"
                      value={formData.config?.guild_id || ''}
                      onChange={(e) => setFormData({
                        ...formData,
                        config: { ...formData.config, guild_id: e.target.value }
                      })}
                      placeholder="Enter Discord Server ID"
                      className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-sky-500/50"
                      required
                    />
                  </div>
                )}

                {formData.provider === 'tiktok' && (
                  <>
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">
                        TikTok Shop ID *
                      </label>
                      <input
                        type="text"
                        value={formData.config?.shop_id || ''}
                        onChange={(e) => setFormData({
                          ...formData,
                          config: { ...formData.config, shop_id: e.target.value }
                        })}
                        placeholder="Enter TikTok Shop ID"
                        className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-sky-500/50"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">
                        Access Token (Optional)
                      </label>
                      <input
                        type="password"
                        value={formData.config?.access_token || ''}
                        onChange={(e) => setFormData({
                          ...formData,
                          config: { ...formData.config, access_token: e.target.value }
                        })}
                        placeholder="Enter Access Token"
                        className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-sky-500/50"
                      />
                    </div>
                  </>
                )}

                <div className="flex gap-3 mt-6">
                  <motion.button
                    type="button"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={resetForm}
                    className="flex-1 px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white hover:bg-white/10 transition-all"
                  >
                    Cancel
                  </motion.button>
                  <motion.button
                    type="submit"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    disabled={createMutation.isPending || updateMutation.isPending}
                    className="flex-1 px-4 py-2.5 bg-gradient-to-r from-blue-500 to-sky-500 text-white rounded-lg font-medium hover:shadow-lg hover:shadow-sky-500/50 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                  >
                    {(createMutation.isPending || updateMutation.isPending) ? (
                      <>
                        <div className="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full" />
                        Saving...
                      </>
                    ) : (
                      <>
                        <Save className="w-5 h-5" />
                        {editingIntegration ? 'Update' : 'Create'} Integration
                      </>
                    )}
                  </motion.button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </div>
    </div>
  );
}
