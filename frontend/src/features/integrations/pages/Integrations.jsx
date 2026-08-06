import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ShoppingBag,
  MessageCircle,
  Send,
  Facebook,
  Instagram,
  MessageSquare,
  Video,
  Plus,
  Settings as SettingsIcon,
  RefreshCw,
  AlertCircle,
  CheckCircle,
  Check,
  ListTree,
  X,
  BookOpen,
  Trash2,
  ExternalLink,
  Info,
  Sparkles,
} from 'lucide-react';
import { toast } from 'sonner';
import GlassCard from '../../../components/ui/GlassCard';
import Button from '../../../components/ui/Button';
import WebhookTerminal from '../../../components/WebhookTerminal';
import WhatsAppQRModal from '../../../components/WhatsAppQRModal';
import api from '../../../services/api';
import { useProjectStore } from '../../../store/projectStore';
import { useTranslation } from '../../../lib/translations';

// Move availableIntegrations inside the component if needed or use a separate function
// For simplicity, I'll pass t to a mapping function

export default function Integrations() {
  const { currentProject } = useProjectStore();
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { t } = useTranslation();
  const integrations = api.integrations;

  const availableIntegrations = [
    {
      id: 'shopify',
      name: t('integrations.providers.shopify.name'),
      icon: ShoppingBag,
      description: t('integrations.providers.shopify.description'),
      color: 'from-green-500 to-emerald-600',
      instructions: t('integrations.providers.shopify.instructions'),
    },
    {
      id: 'whatsapp',
      name: t('integrations.providers.whatsapp.name'),
      icon: MessageCircle,
      description: t('integrations.providers.whatsapp.description'),
      color: 'from-green-400 to-green-600',
      instructions: t('integrations.providers.whatsapp.instructions'),
    },
    {
      id: 'telegram',
      name: t('integrations.providers.telegram.name'),
      icon: Send,
      description: t('integrations.providers.telegram.description'),
      color: 'from-blue-400 to-blue-600',
      instructions: t('integrations.providers.telegram.instructions'),
    },
    {
      id: 'instagram',
      name: t('integrations.providers.instagram.name'),
      icon: Instagram,
      description: t('integrations.providers.instagram.description'),
      color: 'from-sky-500 to-sky-600',
      instructions: t('integrations.providers.instagram.instructions'),
    },
    {
      id: 'facebook',
      name: t('integrations.providers.facebook.name'),
      icon: Facebook,
      description: t('integrations.providers.facebook.description'),
      color: 'from-blue-500 to-indigo-600',
      instructions: t('integrations.providers.facebook.instructions'),
    },
    {
      id: 'discord',
      name: t('integrations.providers.discord.name'),
      icon: MessageSquare,
      description: t('integrations.providers.discord.description'),
      color: 'from-indigo-500 to-sky-600',
      instructions: t('integrations.providers.discord.instructions'),
    },
    {
      id: 'tiktok',
      name: t('integrations.providers.tiktok.name'),
      icon: Video,
      description: t('integrations.providers.tiktok.description'),
      color: 'from-black via-sky-500 to-cyan-400',
      instructions: t('integrations.providers.tiktok.instructions'),
    },
  ];
  const [showTerminal, setShowTerminal] = useState(false);
  const [connectingProvider, setConnectingProvider] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState(null);
  const initialCredentials = {
    apiKey: '',
    apiSecret: '',
    webhookUrl: '',
    shopDomain: '',
    whatsappBusinessAccountId: '',
    whatsappPhoneNumber: '',
    whatsappProvider: 'business_api', // 'business_api' or 'wa_gateway'
    sessionId: 'default', // For wa-gateway
    baseUrl: '', // For wa-gateway
    instagramBusinessAccountId: '',
    facebookPageId: '',
    facebookAppId: '',
    tiktokShopId: '',
    tiktokAppKey: '',
    tiktokAppSecret: '',
    tiktokAccessToken: '',
    discordGuildId: '',
  };

  const [credentials, setCredentials] = useState(initialCredentials);
  const [showInstructions, setShowInstructions] = useState(false);
  const [selectedInstructions, setSelectedInstructions] = useState(null);
  const [showWhatsAppQR, setShowWhatsAppQR] = useState(false);
  const [qrCodeData, setQrCodeData] = useState(null);

  // Fetch integrations
  const { data: connectedIntegrations, isLoading, refetch } = useQuery({
    queryKey: ['integrations', currentProject?.id],
    queryFn: () => integrations.list(currentProject?.id),
    enabled: !!currentProject,
    onSuccess: (data) => {
      console.log('Integrations fetched:', data);
    }
  });

  // Connect mutation
  const connectMutation = useMutation({
    mutationFn: (data) => integrations.create(currentProject?.id, data),
    onSuccess: async (data) => {
      console.log('Integration connected successfully:', data);

      // Show success message based on status
      if (data.status === 'connected') {
        toast.success(`🎉 ${t('integrations.connect_success')}`);
      } else if (data.status === 'pending') {
        toast.success(`✅ ${t('integrations.qr_success')}`);

        // If WA-Gateway or WPPConnect, automatically start session and show QR code
        // Check config_values.whatsapp_provider (API returns config_keys and config_values separately)
        const isWaGateway = data.provider === 'whatsapp' &&
          (data.config_values?.whatsapp_provider === 'go_whatsapp' ||
            data.config?.whatsapp_provider === 'go_whatsapp');

        if (isWaGateway) {
          try {
            console.log('Starting WA-Gateway session for integration:', data.id);
            const sessionResponse = await integrations.waGateway.startSession(
              currentProject?.id,
              data.id
            );

            console.log('Session Response:', sessionResponse);

            if (sessionResponse.session_url) {
              console.log('✅ Session URL found:', sessionResponse.session_url);

              // Show session URL in modal (iframe)
              setQrCodeData(sessionResponse.session_url);
              setShowWhatsAppQR(true);

              toast.success('📱 Scan QR code to connect WhatsApp!', {
                duration: 5000,
                description: 'QR code will appear in the modal'
              });
            } else {
              console.error('❌ No session URL in response:', sessionResponse);
              toast.error('Session URL not found in response');
            }
          } catch (error) {
            console.error('Failed to start WA-Gateway session:', error);
            toast.error(`Failed to start session: ${error.message}`);
          }
        }
      } else {
        toast.success('Integration connected successfully!');
      }

      // Refresh data
      queryClient.invalidateQueries(['integrations', currentProject?.id]);
      refetch();

      // Reset form
      setShowModal(false);
      setCredentials(initialCredentials);
      setConnectingProvider(null);
    },
    onError: (error) => {
      console.error('Connection failed:', error);

      // Show specific error message
      const errorMessage = error.response?.data?.detail || error.message || 'Connection failed';
      toast.error(`❌ ${errorMessage}`);

      setConnectingProvider(null);
    },
  });

  // Sync mutation
  const syncMutation = useMutation({
    mutationFn: ({ projectId, integrationId }) =>
      integrations.sync(projectId, integrationId),
    onSuccess: () => {
      toast.success(t('integrations.sync_success'));
      // Fix: Use the correct query key that matches the useQuery
      queryClient.invalidateQueries(['integrations', currentProject?.id]);
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || t('common.error'));
    },
  });

  // Verify mutation
  const verifyMutation = useMutation({
    mutationFn: ({ projectId, integrationId }) =>
      integrations.verify(projectId, integrationId),
    onSuccess: async (data, variables) => {
      if (data.status === 'success') {
        toast.success(t('integrations.verify_success'));

        // Check if this is a WA-Gateway integration and show QR code
        const integration = (connectedIntegrations?.data || connectedIntegrations || []).find(
          i => i.id === variables.integrationId
        );

        console.log('Verify success - checking for WA-Gateway:', {
          integration,
          provider: integration?.provider,
          config_values: integration?.config_values,
          whatsapp_provider: integration?.config_values?.whatsapp_provider,
          isWaGateway: integration?.provider === 'whatsapp' && integration?.config_values?.whatsapp_provider === 'wa_gateway'
        });

        if (integration?.provider === 'whatsapp' &&
          (integration?.config_values?.whatsapp_provider === 'go_whatsapp')) {
          try {
            console.log('Fetching QR code for WA-Gateway integration');
            const qrResponse = await integrations.waGateway.startSession(
              variables.projectId,
              variables.integrationId
            );

            console.log('QR Response received:', qrResponse);

            if (qrResponse.qr_url) {
              console.log('Setting QR code data:', qrResponse.qr_url);
              setQrCodeData(qrResponse.qr_url);
              setShowWhatsAppQR(true);
              toast.success('📱 Scan QR code with WhatsApp to connect!');
            } else {
              console.error('No qr_url in response:', qrResponse);
              toast.error('QR code URL not found in response');
            }
          } catch (error) {
            console.error('Failed to get QR code:', error);
            toast.error(`Failed to generate QR code: ${error.message}`);
          }
        } else {
          console.log('Not a WA-Gateway integration, skipping QR display');
        }
      } else {
        toast.error(data.message || 'Verification failed');
      }
      // Refresh integrations list
      queryClient.invalidateQueries(['integrations', currentProject?.id]);
      refetch();
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Verification failed');
    },
  });

  // Refresh Identities mutation
  const refreshIdentitiesMutation = useMutation({
    mutationFn: () => integrations.refreshIdentities(currentProject?.id),
    onSuccess: (data) => {
      if (data.updated_count > 0) {
        toast.success(`✅ ${t('integrations.identities_success')} (${data.updated_count})`);
      } else {
        toast.info(t('integrations.identities_up_to_date'));
      }
      queryClient.invalidateQueries(['integrations', currentProject?.id]);
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || t('common.error'));
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: ({ projectId, integrationId }) =>
      integrations.delete(projectId, integrationId),
    onSuccess: () => {
      toast.success('Integration deleted successfully');
      queryClient.invalidateQueries(['integrations', currentProject?.id]);
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Delete failed');
    },
  });

  const handleDelete = (integrationId) => {
    if (!currentProject || !integrationId) return;

    // If integrationId is a provider name (not a UUID), try to resolve it
    if (!integrationId.match(/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i)) {
      const resolvedId = getIntegrationId(integrationId);
      if (resolvedId) {
        integrationId = resolvedId;
      } else {
        // If we still don't have a UUID, it might be that the integration isn't connected/found
        // But let's verify if it's a valid UUID before proceeding
        console.error('Invalid integration ID:', integrationId);
        return;
      }
    }

    if (window.confirm(t('integrations.delete_confirm'))) {
      deleteMutation.mutate({
        projectId: currentProject.id,
        integrationId: integrationId,
      });
    }
  };

  const getIntegrationStatus = (provider) => {
    // Handle both direct array and nested data structure
    const integrations = connectedIntegrations?.data || connectedIntegrations || [];
    const integration = integrations.find(
      (i) => i.provider === provider
    );
    return integration?.status || 'disconnected';
  };

  const getIntegrationId = (provider) => {
    // Handle both direct array and nested data structure
    const integrations = connectedIntegrations?.data || connectedIntegrations || [];
    const integration = integrations.find(
      (i) => i.provider === provider
    );
    return integration?.id;
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'connected':
        return 'bg-green-500/20 text-green-400 border border-green-500/30';
      case 'pending':
        return 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30';
      case 'error':
        return 'bg-red-500/20 text-red-400 border border-red-500/30';
      case 'syncing':
        return 'bg-blue-500/20 text-blue-400 border border-blue-500/30';
      default:
        return 'bg-gray-500/20 text-gray-400 border border-gray-500/30';
    }
  };

  const handleConnect = (provider) => {
    const integration = availableIntegrations.find(i => i.id === provider);
    setSelectedProvider(integration);
    setCredentials(initialCredentials);
    setShowModal(true);
  };

  const handleSubmitConnection = () => {
    const providerId = selectedProvider.id;

    setConnectingProvider(providerId);

    // Build config data, only include non-empty values
    const configData = {};

    // Add API Key if provided (allow for whatsapp if it's wa_gateway or wppconnect)
    if (credentials.apiKey && credentials.apiKey.trim()) {
      if (providerId !== 'whatsapp' || credentials.whatsappProvider === 'go_whatsapp') {
        configData.api_key = credentials.apiKey.trim();
      }
    }

    if (credentials.apiSecret && credentials.apiSecret.trim() && providerId === 'shopify') {
      configData.api_secret = credentials.apiSecret.trim();
    }

    if (credentials.webhookUrl && credentials.webhookUrl.trim()) {
      configData.webhook_url = credentials.webhookUrl.trim();
    }

    if (providerId === 'shopify') {
      if (credentials.shopDomain && credentials.shopDomain.trim()) {
        configData.shop_domain = credentials.shopDomain.trim();
      } else {
        toast.error('Shop domain is required for Shopify');
        setConnectingProvider(null);
        return;
      }

      if (!credentials.apiSecret || !credentials.apiSecret.trim()) {
        toast.error('Admin API secret is required for Shopify');
        setConnectingProvider(null);
        return;
      }
    }

    if (providerId === 'whatsapp') {
      // Add provider type to config
      configData.whatsapp_provider = credentials.whatsappProvider || 'business_api';

      if (credentials.whatsappProvider === 'go_whatsapp') {
        // Go WhatsApp validation
        if (!credentials.baseUrl || !credentials.baseUrl.trim()) {
          toast.error('Go WhatsApp Base URL is required');
          setConnectingProvider(null);
          return;
        }

        configData.base_url = credentials.baseUrl.trim();
        // Session ID is optional/default for Go WhatsApp but we send it if provided
        if (credentials.sessionId && credentials.sessionId.trim()) {
          configData.session_id = credentials.sessionId.trim();
        } else {
          configData.session_id = 'default';
        }
        // API Key is already added at the top if present

      } else {
        // Business API validation
        if (!credentials.whatsappPhoneNumber || !credentials.whatsappPhoneNumber.trim()) {
          toast.error('Phone number is required for WhatsApp Business API');
          setConnectingProvider(null);
          return;
        }
        configData.phone_number = credentials.whatsappPhoneNumber.trim();
        if (credentials.whatsappBusinessAccountId && credentials.whatsappBusinessAccountId.trim()) {
          configData.business_account_id = credentials.whatsappBusinessAccountId.trim();
        }
      }
    }

    if (providerId === 'instagram') {
      if (!credentials.instagramBusinessAccountId || !credentials.instagramBusinessAccountId.trim()) {
        toast.error('Instagram Business Account ID is required');
        setConnectingProvider(null);
        return;
      }
      configData.business_account_id = credentials.instagramBusinessAccountId.trim();
    }

    if (providerId === 'facebook') {
      if (!credentials.facebookPageId || !credentials.facebookPageId.trim()) {
        toast.error('Facebook Page ID is required');
        setConnectingProvider(null);
        return;
      }
      configData.page_id = credentials.facebookPageId.trim();
      if (credentials.facebookAppId && credentials.facebookAppId.trim()) {
        configData.app_id = credentials.facebookAppId.trim();
      }
    }

    if (providerId === 'tiktok') {
      if (!credentials.tiktokShopId || !credentials.tiktokShopId.trim()) {
        toast.error('TikTok Shop ID is required');
        setConnectingProvider(null);
        return;
      }
      if (!credentials.tiktokAppKey || !credentials.tiktokAppKey.trim()) {
        toast.error('TikTok App Key is required');
        setConnectingProvider(null);
        return;
      }

      configData.shop_id = credentials.tiktokShopId.trim();
      configData.api_key = credentials.tiktokAppKey.trim(); // Map App Key to api_key

      if (credentials.tiktokAppSecret && credentials.tiktokAppSecret.trim()) {
        configData.api_secret = credentials.tiktokAppSecret.trim();
      }
      if (credentials.tiktokAccessToken && credentials.tiktokAccessToken.trim()) {
        configData.access_token = credentials.tiktokAccessToken.trim();
      }
    }

    if (providerId === 'discord') {
      if (!credentials.discordGuildId || !credentials.discordGuildId.trim()) {
        toast.error('Discord Server ID (Guild ID) is required');
        setConnectingProvider(null);
        return;
      }
      configData.guild_id = credentials.discordGuildId.trim();
    }

    // Validate API key for providers that still require it
    if (providerId !== 'whatsapp' && providerId !== 'tiktok' && !configData.api_key) {
      toast.error('API Key cannot be empty');
      setConnectingProvider(null);
      return;
    }

    const requestData = {
      provider: providerId,
      config: {
        ...configData,
        auto_sync: true,
      }
    };

    console.log('Connecting integration with data:', requestData);
    console.log('API Key length:', configData.api_key ? configData.api_key.length : 0);

    connectMutation.mutate(requestData);
  };

  const handleSync = (provider) => {
    const integrationId = getIntegrationId(provider);
    if (!integrationId || !currentProject) return;

    syncMutation.mutate({
      projectId: currentProject.id,
      integrationId: integrationId,
    });
  };

  const handleVerify = (provider) => {
    const integrationId = getIntegrationId(provider);
    if (!integrationId || !currentProject) return;

    verifyMutation.mutate({
      projectId: currentProject.id,
      integrationId: integrationId,
    });
  };

  const handleDebug = async (provider) => {
    const integrationId = getIntegrationId(provider);
    if (!integrationId || !currentProject) return;

    try {
      const debugData = await integrations.debug(currentProject.id, integrationId);
      console.log('Integration debug data:', debugData);
      toast.info('Debug data logged to console');
    } catch (error) {
      console.error('Debug failed:', error);
      toast.error('Debug failed');
    }
  };


  const handleMetaConnect = async () => {
    try {
      const redirectUri = window.location.origin + '/integrations/meta/callback';
      const response = await integrations.getMetaAuthUrl(currentProject.id, redirectUri);

      if (response.auth_url) {
        window.location.href = response.auth_url;
      } else {
        toast.error('Failed to get authentication URL');
      }
    } catch (error) {
      console.error('Meta auth error:', error);
      toast.error('Failed to start Meta connection');
    }
  };

  if (isLoading) {
    return (
      <div className="p-6 flex items-center justify-center h-96">
        <div className="animate-spin w-12 h-12 border-4 border-accent-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3 text-primary">
            <RefreshCw className="w-8 h-8 text-accent-500" />
            {t('integrations.title')}
          </h1>
          <p className="text-secondary">{t('integrations.description')}</p>
        </div>
        <div className="flex gap-3">
          <Button
            onClick={handleMetaConnect}
            variant="primary"
            size="lg"
            className="shadow-neon"
            leftIcon={Sparkles}
          >
            {t('integrations.meta')}
          </Button>

          <div className="w-[1px] h-10 bg-white/10 mx-2" />

          <Button
            onClick={() => refreshIdentitiesMutation.mutate()}
            disabled={refreshIdentitiesMutation.isPending}
            variant="ghost"
            className="text-sky-400 hover:bg-sky-500/10 border-sky-500/20"
            isLoading={refreshIdentitiesMutation.isPending}
            leftIcon={RefreshCw}
          >
            {t('integrations.refresh_identities')}
          </Button>

          <Button
            onClick={() => setShowTerminal(!showTerminal)}
            variant={showTerminal ? "primary" : "secondary"}
            leftIcon={ListTree}
          >
            {t('integrations.terminal')}
          </Button>
        </div>
      </motion.div>


      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <GlassCard className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm mb-1">{t('integrations.connected')}</p>
              <p className="text-3xl font-bold">
                {connectedIntegrations?.data?.filter(i => i.status === 'connected').length || 0}
              </p>
            </div>
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center">
              <Check className="w-6 h-6 text-white" />
            </div>
          </div>
        </GlassCard>

        <GlassCard className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm mb-1">{t('common.active')}</p>
              <p className="text-3xl font-bold">{availableIntegrations.length}</p>
            </div>
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-600 flex items-center justify-center">
              <Plus className="w-6 h-6 text-white" />
            </div>
          </div>
        </GlassCard>

        <GlassCard className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm mb-1">{t('integrations.error')}</p>
              <p className="text-3xl font-bold">
                {connectedIntegrations?.data?.filter(i => i.status === 'error').length || 0}
              </p>
            </div>
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-red-500 to-sky-600 flex items-center justify-center">
              <X className="w-6 h-6 text-white" />
            </div>
          </div>
        </GlassCard>
      </div>

      {/* Integration Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {availableIntegrations.map((integration, index) => {
          const status = getIntegrationStatus(integration.id);
          const isConnected = status === 'connected';
          const isPending = status === 'pending';
          const isError = status === 'error';
          const isConnecting = connectingProvider === integration.id;

          return (
            <motion.div
              key={integration.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <GlassCard className="p-6 hover:scale-105 transition-all duration-300">
                {/* Icon & Status */}
                <div className="flex items-start justify-between mb-4">
                  <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${integration.color} flex items-center justify-center`}>
                    <integration.icon className="w-7 h-7 text-white" />
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(status)}`}>
                    {status}
                  </span>
                </div>

                {/* Info */}
                <h3 className="text-xl font-semibold mb-2">{integration.name}</h3>
                <p className="text-sm text-gray-400 mb-6">{integration.description}</p>

                {/* Actions */}
                <div className="flex gap-2">
                  {isConnected ? (
                    <>
                      <Button
                        onClick={() => handleSync(integration.id)}
                        disabled={syncMutation.isPending}
                        variant="secondary"
                        size="sm"
                        className="flex-1"
                        isLoading={syncMutation.isPending || integration.status === 'syncing'}
                        loadingText="Syncing..."
                        leftIcon={RefreshCw}
                      >
                        Sync
                      </Button>

                      <Button
                        variant="secondary"
                        size="sm"
                        className="px-3"
                      >
                        <SettingsIcon className="w-4 h-4" />
                      </Button>

                      <Button
                        onClick={() => handleDelete(getIntegrationId(integration.id))}
                        disabled={deleteMutation.isPending}
                        variant="danger"
                        size="sm"
                        className="px-3"
                        isLoading={deleteMutation.isPending}
                      >
                        {!deleteMutation.isPending && <Trash2 className="w-4 h-4" />}
                      </Button>
                    </>
                  ) : isPending ? (
                    <div className="space-y-2 w-full">
                      <Button
                        onClick={() => handleVerify(integration.id)}
                        disabled={verifyMutation.isPending}
                        variant="primary"
                        className="w-full"
                        isLoading={verifyMutation.isPending}
                        leftIcon={CheckCircle}
                      >
                        {t('integrations.verify')}
                      </Button>

                      <div className="flex gap-2">
                        <Button
                          onClick={() => handleDebug(integration.id)}
                          variant="secondary"
                          size="xs"
                          className="flex-1"
                        >
                          🐛 Debug
                        </Button>

                        <Button
                          onClick={() => handleConnect(integration.id)}
                          variant="secondary"
                          size="xs"
                          className="flex-1 text-yellow-400 hover:text-yellow-300"
                          leftIcon={SettingsIcon}
                        >
                          {t('common.edit')}
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <Button
                      onClick={() => handleConnect(integration.id)}
                      disabled={isConnecting || !currentProject}
                      variant="primary"
                      className="w-full"
                      isLoading={isConnecting}
                    >
                      {t('integrations.connect')}
                    </Button>
                  )}
                </div>

                {/* Instructions Button */}
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => {
                    setSelectedInstructions(integration);
                    setShowInstructions(true);
                  }}
                  className="w-full mt-3 glass-card px-4 py-2 rounded-xl hover:bg-white/10 transition-colors text-xs font-medium flex items-center justify-center gap-2"
                >
                  <BookOpen className="w-3 h-3" />
                  {t('integrations.setup_instructions')}
                </motion.button>

                {/* Error Message */}
                {
                  isError && (
                    <p className="mt-3 text-xs text-red-400 bg-red-400/10 p-2 rounded-lg">
                      {t('integrations.error')}
                    </p>
                  )
                }

                {/* Last Sync */}
                {
                  isConnected && (
                    <p className="mt-3 text-xs text-gray-500">
                      {t('integrations.status')}: {t(`integrations.${integration.status}`)}
                    </p>
                  )
                }
              </GlassCard>
            </motion.div>
          );
        })}
      </div >



      {/* Connection Modal */}
      {
        showModal && selectedProvider && (
          <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="glass-card p-6 max-w-md w-full rounded-2xl"
            >
              <div className="flex items-center gap-3 mb-6">
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${selectedProvider.color} flex items-center justify-center`}>
                  <selectedProvider.icon className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h2 className="text-xl font-semibold">Connect {selectedProvider.name}</h2>
                  <p className="text-sm text-gray-400">{selectedProvider.description}</p>
                </div>
              </div>

              {/* Provider-specific instructions */}
              {selectedProvider.id === 'telegram' && (
                <div className="mb-4 p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg">
                  <p className="text-blue-400 text-xs font-semibold mb-1">🤖 Quick Setup:</p>
                  <p className="text-xs text-gray-400">
                    1. Message @BotFather on Telegram<br />
                    2. Send /newbot command<br />
                    3. Copy the bot token below
                  </p>
                </div>
              )}

              {selectedProvider.id === 'shopify' && (
                <div className="mb-4 p-3 bg-green-500/10 border border-green-500/30 rounded-lg">
                  <p className="text-green-400 text-xs font-semibold mb-1">🛍️ Shopify Setup:</p>
                  <p className="text-xs text-gray-400">
                    Get API credentials from Shopify Admin → Apps → Develop apps
                  </p>
                </div>
              )}

              {selectedProvider.id === 'whatsapp' && (
                <div className="mb-4 p-3 bg-green-500/10 border border-green-500/30 rounded-lg">
                  <p className="text-green-400 text-xs font-semibold mb-1">📱 WhatsApp Setup:</p>
                  <p className="text-xs text-gray-400">
                    Enter your WhatsApp phone number in international format (e.g., +1234567890).
                    After connecting, your WhatsApp account will be linked to this platform.
                  </p>
                </div>
              )}

              {/* Meta OAuth Button Removed - Manual Connection Only */}

              <form onSubmit={(e) => { e.preventDefault(); handleSubmitConnection(); }} className="space-y-4">
                {selectedProvider.id !== 'whatsapp' && (
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      {(() => {
                        switch (selectedProvider.id) {
                          case 'telegram':
                            return 'Bot Token *';
                          case 'discord':
                            return 'Bot Token *';
                          case 'shopify':
                            return 'Admin API Key *';
                          case 'instagram':
                            return 'User Access Token *';
                          case 'facebook':
                            return 'Page Access Token *';
                          case 'tiktok':
                            return 'App Key *';
                          default:
                            return 'API Key *';
                        }
                      })()}
                    </label>
                    <input
                      type="text"
                      placeholder={
                        selectedProvider.id === 'telegram'
                          ? '1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ'
                          : selectedProvider.id === 'discord'
                            ? 'MTAw...'
                            : selectedProvider.id === 'shopify'
                              ? 'shpat_...'
                              : selectedProvider.id === 'facebook'
                                ? 'EAAG...'
                                : selectedProvider.id === 'tiktok'
                                  ? 'Enter App Key'
                                  : 'Enter your API key'
                      }
                      className="input-glass w-full"
                      autoComplete="off"
                      required
                      value={selectedProvider.id === 'tiktok' ? credentials.tiktokAppKey : credentials.apiKey}
                      onChange={(e) => {
                        if (selectedProvider.id === 'tiktok') {
                          setCredentials({ ...credentials, tiktokAppKey: e.target.value });
                        } else {
                          setCredentials({ ...credentials, apiKey: e.target.value });
                        }
                      }}
                    />
                    {selectedProvider.id === 'telegram' && (
                      <p className="text-xs text-gray-500 mt-1">
                        Get this from @BotFather after creating your bot
                      </p>
                    )}
                    {selectedProvider.id === 'discord' && (
                      <p className="text-xs text-gray-500 mt-1">
                        Get this from the Discord Developer Portal
                      </p>
                    )}
                  </div>
                )}

                {selectedProvider.id === 'discord' && (
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Server ID (Guild ID) *
                    </label>
                    <input
                      type="text"
                      value={credentials.discordGuildId || ''}
                      onChange={(e) => setCredentials({ ...credentials, discordGuildId: e.target.value })}
                      placeholder="123456789012345678"
                      className="input-glass w-full"
                      required
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Enable Developer Mode in Discord settings to copy this ID
                    </p>
                  </div>
                )}

                {selectedProvider.id === 'shopify' && (
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Shop Domain *
                    </label>
                    <input
                      type="text"
                      value={credentials.shopDomain || ''}
                      onChange={(e) => setCredentials({ ...credentials, shopDomain: e.target.value })}
                      placeholder="your-shop-name (without .myshopify.com)"
                      className="input-glass w-full"
                      required={selectedProvider.id === 'shopify'}
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Just the shop name, not the full URL
                    </p>
                  </div>
                )}

                {selectedProvider.id === 'shopify' && (
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Admin API Secret Key *
                    </label>
                    <input
                      type="password"
                      value={credentials.apiSecret}
                      onChange={(e) => setCredentials({ ...credentials, apiSecret: e.target.value })}
                      placeholder="Required for Shopify"
                      className="input-glass w-full"
                      autoComplete="current-password"
                      required
                    />
                  </div>
                )}

                {selectedProvider.id === 'whatsapp' && (
                  <div className="grid grid-cols-1 gap-4">
                    {/* Provider Selection */}
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        WhatsApp Provider *
                      </label>
                      <select
                        value={credentials.whatsappProvider}
                        onChange={(e) => setCredentials({ ...credentials, whatsappProvider: e.target.value })}
                        className="input-glass w-full"
                      >
                        <option value="business_api">WhatsApp Business API (Official)</option>
                        <option value="go_whatsapp">Go WhatsApp (Multi-Device)</option>
                      </select>
                      <p className="text-xs text-gray-500 mt-1">
                        {credentials.whatsappProvider === 'business_api'
                          ? 'Connect your WhatsApp Business Account'
                          : 'Scan QR code in next step'}
                      </p>
                    </div>

                    {/* Business API Fields */}
                    {credentials.whatsappProvider === 'business_api' && (
                      <>
                        <div>
                          <label className="block text-sm font-medium text-gray-300 mb-2">
                            WhatsApp Phone Number *
                          </label>
                          <input
                            type="text"
                            value={credentials.whatsappPhoneNumber}
                            onChange={(e) => setCredentials({ ...credentials, whatsappPhoneNumber: e.target.value })}
                            placeholder="+15551234567"
                            className="input-glass w-full"
                            required
                          />
                          <p className="text-xs text-gray-500 mt-1">
                            Business phone number registered with WhatsApp Business API
                          </p>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-300 mb-2">
                            Business Account ID (optional)
                          </label>
                          <input
                            type="text"
                            value={credentials.whatsappBusinessAccountId}
                            onChange={(e) => setCredentials({ ...credentials, whatsappBusinessAccountId: e.target.value })}
                            placeholder="Optional"
                            className="input-glass w-full"
                          />
                        </div>
                      </>
                    )}



                    {/* Go WhatsApp Fields */}
                    {credentials.whatsappProvider === 'go_whatsapp' && (
                      <div className="space-y-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-300 mb-2">
                            Go WhatsApp Base URL *
                          </label>
                          <input
                            type="text"
                            value={credentials.baseUrl}
                            onChange={(e) => setCredentials({ ...credentials, baseUrl: e.target.value })}
                            placeholder="https://go-whatsapp.railway.app"
                            className="input-glass w-full"
                            required
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-300 mb-2">
                            Basic Auth Password (Optional)
                          </label>
                          <input
                            type="password"
                            value={credentials.apiKey}
                            onChange={(e) => setCredentials({ ...credentials, apiKey: e.target.value })}
                            placeholder="Password if Basic Auth is enabled"
                            className="input-glass w-full"
                            autoComplete="off"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-300 mb-2">
                            Session Name (Optional)
                          </label>
                          <input
                            type="text"
                            value={credentials.sessionId}
                            onChange={(e) => setCredentials({ ...credentials, sessionId: e.target.value })}
                            placeholder="default"
                            className="input-glass w-full"
                          />
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {selectedProvider.id === 'instagram' && (
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Instagram Business Account ID *
                    </label>
                    <input
                      type="text"
                      value={credentials.instagramBusinessAccountId}
                      onChange={(e) => setCredentials({ ...credentials, instagramBusinessAccountId: e.target.value })}
                      placeholder="17841405793187218"
                      className="input-glass w-full"
                      required
                    />
                  </div>
                )}

                {selectedProvider.id === 'facebook' && (
                  <div className="grid grid-cols-1 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Page ID *
                      </label>
                      <input
                        type="text"
                        value={credentials.facebookPageId}
                        onChange={(e) => setCredentials({ ...credentials, facebookPageId: e.target.value })}
                        placeholder="112233445566778"
                        className="input-glass w-full"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        App ID (optional)
                      </label>
                      <input
                        type="text"
                        value={credentials.facebookAppId}
                        onChange={(e) => setCredentials({ ...credentials, facebookAppId: e.target.value })}
                        placeholder="987654321098765"
                        className="input-glass w-full"
                      />
                    </div>
                  </div>
                )}

                {selectedProvider.id === 'tiktok' && (
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Shop ID *
                      </label>
                      <input
                        type="text"
                        value={credentials.tiktokShopId}
                        onChange={(e) => setCredentials({ ...credentials, tiktokShopId: e.target.value })}
                        placeholder="Enter TikTok Shop ID"
                        className="input-glass w-full"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        App Secret (Optional)
                      </label>
                      <input
                        type="password"
                        value={credentials.tiktokAppSecret}
                        onChange={(e) => setCredentials({ ...credentials, tiktokAppSecret: e.target.value })}
                        placeholder="Enter App Secret"
                        className="input-glass w-full"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Access Token (Optional)
                      </label>
                      <input
                        type="password"
                        value={credentials.tiktokAccessToken}
                        onChange={(e) => setCredentials({ ...credentials, tiktokAccessToken: e.target.value })}
                        placeholder="Enter Access Token"
                        className="input-glass w-full"
                      />
                    </div>
                  </div>
                )}
                {selectedProvider.id !== 'shopify' && (
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Webhook URL (optional)
                    </label>
                    <input
                      type="url"
                      value={credentials.webhookUrl}
                      onChange={(e) => setCredentials({ ...credentials, webhookUrl: e.target.value })}
                      placeholder="https://your-domain.com/webhook"
                      className="input-glass w-full"
                      autoComplete="url"
                    />
                  </div>
                )}
              </form>

              <div className="flex gap-3 mt-6">
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => {
                    setShowModal(false);
                    setCredentials(initialCredentials);
                  }}
                  disabled={connectMutation.isPending}
                  className="flex-1 glass-card px-4 py-2 rounded-xl hover:bg-white/10 transition-colors"
                >
                  {t('integrations.cancel')}
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleSubmitConnection}
                  disabled={
                    connectMutation.isPending ||
                    (selectedProvider.id !== 'whatsapp' && selectedProvider.id !== 'tiktok' && !credentials.apiKey) ||
                    (selectedProvider.id === 'tiktok' && (!credentials.tiktokAppKey || !credentials.tiktokShopId))
                  }
                  className="flex-1 btn-neon disabled:opacity-50"
                >
                  {connectMutation.isPending ? t('common.loading') : t('integrations.connect')}
                </motion.button>
              </div>
            </motion.div>
          </div>
        )
      }

      {/* Instructions Modal */}
      {
        showInstructions && selectedInstructions && (
          <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="glass-card p-8 max-w-2xl w-full rounded-2xl max-h-[80vh] overflow-y-auto"
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-6 sticky top-0 bg-dark-900/90 backdrop-blur-lg pb-4 border-b border-white/10">
                <div className="flex items-center gap-3">
                  <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${selectedInstructions.color} flex items-center justify-center`}>
                    <selectedInstructions.icon className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h2 className="text-2xl font-semibold">{selectedInstructions.name} Setup</h2>
                    <p className="text-sm text-gray-400">Complete step-by-step instructions</p>
                  </div>
                </div>
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={() => {
                    setShowInstructions(false);
                    setSelectedInstructions(null);
                  }}
                  className="glass-card p-2 rounded-lg hover:bg-white/10 transition-colors"
                >
                  <X className="w-5 h-5" />
                </motion.button>
              </div>

              {/* Instructions Content */}
              <div className="prose prose-invert max-w-none">
                <div className="text-sm leading-relaxed space-y-4 whitespace-pre-wrap">
                  {selectedInstructions.instructions}
                </div>
              </div>

              {/* Footer */}
              <div className="flex gap-3 mt-8 pt-6 border-t border-white/10">
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => {
                    setShowInstructions(false);
                    setSelectedInstructions(null);
                  }}
                  className="flex-1 glass-card px-4 py-3 rounded-xl hover:bg-white/10 transition-colors font-medium"
                >
                  Close
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => {
                    setShowInstructions(false);
                    setSelectedInstructions(null);
                    handleConnect(selectedInstructions.id);
                  }}
                  disabled={!currentProject}
                  className="flex-1 btn-neon disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Plus className="w-4 h-4 inline mr-2" />
                  Connect Now
                </motion.button>
              </div>
            </motion.div>
          </div>
        )
      }
      {/* WhatsApp QR Modal */}
      {
        showWhatsAppQR && (
          <WhatsAppQRModal
            isOpen={showWhatsAppQR}
            onClose={() => setShowWhatsAppQR(false)}
            projectId={currentProject?.id}
            integrationId={getIntegrationId('whatsapp')}
            initialQRCode={qrCodeData}
          />
        )
      }

      {/* Webhook Terminal Overlay */}
      <AnimatePresence>
        {showTerminal && (
          <WebhookTerminal onClose={() => setShowTerminal(false)} />
        )}
      </AnimatePresence>
    </div >
  );
}
