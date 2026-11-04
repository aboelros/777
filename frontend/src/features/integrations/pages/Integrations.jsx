import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  ShoppingBag, MessageCircle, Send, Facebook, Instagram,
  MessageSquare, Video, RefreshCw, Settings as SettingsIcon, Sparkles,
  Plug
} from 'lucide-react';
import { toast } from 'sonner';
import api from '@/services/api';
import { useProjectStore } from '@/store/projectStore';
import { useTranslation } from '@/lib/translations';
import Button from '@/components/ui/Button';
import { NoProjectState } from '@/components/ui/EmptyState';
import ConnectedIntegrationsList from '../components/ConnectedIntegrationsList';
import IntegrationCard from '../components/IntegrationCard';
import IntegrationConnectModal from '../components/IntegrationConnectModal';
import IntegrationInstructionsDrawer from '../components/IntegrationInstructionsDrawer';
import WhatsAppQRModal from '@/components/WhatsAppQRModal';

export default function Integrations() {
  const { currentProject } = useProjectStore();
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { t } = useTranslation();

  const [selectedProvider, setSelectedProvider] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [showInstructions, setShowInstructions] = useState(false);
  const [selectedInstructions, setSelectedInstructions] = useState(null);
  const [qrModalOpen, setQrModalOpen] = useState(false);
  const [activeWhatsAppIntegrationId, setActiveWhatsAppIntegrationId] = useState(null);
  const [credentials, setCredentials] = useState({
    apiKey: '',
    shopDomain: '',
    whatsappPhoneNumber: '',
    whatsappBusinessAccountId: '',
    whatsapp_provider: 'business_api',
  });

  const availableIntegrations = [
    { id: 'shopify', name: 'Shopify Store', icon: ShoppingBag, description: 'Sync products, inventory, and order fulfillment status automatically.', color: 'from-emerald-500 to-green-600' },
    { id: 'whatsapp', name: 'WhatsApp Business', icon: MessageCircle, description: 'Autonomous sales assistant and conversational customer messaging.', color: 'from-green-500 to-emerald-600' },
    { id: 'telegram', name: 'Telegram Bot', icon: Send, description: 'Direct customer support, alerts, and automated community response.', color: 'from-sky-500 to-blue-600' },
    { id: 'instagram', name: 'Instagram Direct', icon: Instagram, description: 'Auto-reply to post comments and stories with product checkout links.', color: 'from-pink-500 to-rose-600' },
    { id: 'facebook', name: 'Facebook Messenger', icon: Facebook, description: 'Instant page messaging and lead capture pipeline.', color: 'from-blue-600 to-indigo-700' },
    { id: 'discord', name: 'Discord Community', icon: MessageSquare, description: 'Private VIP customer channels and automated support tickets.', color: 'from-indigo-500 to-purple-600' },
    { id: 'tiktok', name: 'TikTok Shop', icon: Video, description: 'Live shopping inquiries, creator messaging, and order tracking.', color: 'from-slate-800 to-cyan-700' },
  ];

  const { data: connectedIntegrations, isLoading } = useQuery({
    queryKey: ['integrations', currentProject?.id],
    queryFn: () => api.integrations.list(currentProject?.id),
    enabled: !!currentProject?.id,
  });

  const connectMutation = useMutation({
    mutationFn: (data) => api.integrations.create(currentProject?.id, data),
    onSuccess: (data) => {
      toast.success(t('integrations.connect_success') || 'Channel connected successfully');
      queryClient.invalidateQueries(['integrations', currentProject?.id]);
      setShowModal(false);
      const isBaileys = data?.provider === 'whatsapp' && (
        data?.config?.whatsapp_provider === 'baileys' ||
        data?.extra_data?.provider === 'baileys' ||
        credentials.whatsapp_provider === 'baileys'
      );
      if (isBaileys && data?.id) {
        setActiveWhatsAppIntegrationId(data.id);
        setQrModalOpen(true);
      }
      setCredentials({ apiKey: '', shopDomain: '', whatsappPhoneNumber: '', whatsappBusinessAccountId: '', whatsapp_provider: 'business_api' });
    },
    onError: (err) => toast.error(err.response?.data?.detail || 'Connection failed'),
  });

  const syncMutation = useMutation({
    mutationFn: (integrationId) => api.integrations.sync(currentProject?.id, integrationId),
    onSuccess: () => toast.success('Sync completed'),
  });

  const verifyMutation = useMutation({
    mutationFn: (integrationId) => api.integrations.verify(currentProject?.id, integrationId),
    onSuccess: () => {
      toast.success('Channel verified');
      queryClient.invalidateQueries(['integrations', currentProject?.id]);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (integrationId) => api.integrations.delete(currentProject?.id, integrationId),
    onSuccess: () => {
      toast.success('Integration disconnected');
      queryClient.invalidateQueries(['integrations', currentProject?.id]);
    },
  });

  if (!currentProject) {
    return <NoProjectState subtitle={t('integrations.description') || 'Select a project to configure third-party sales and messaging integrations'} />;
  }

  const rawList = Array.isArray(connectedIntegrations) ? connectedIntegrations : (connectedIntegrations?.data || []);
  const getStatus = (providerId) => {
    const item = rawList.find((i) => i.provider === providerId);
    return item?.status || 'disconnected';
  };
  const getIntegrationId = (providerId) => rawList.find((i) => i.provider === providerId)?.id;

  const handleMetaConnect = async () => {
    try {
      const redirectUri = `${window.location.origin}/integrations/meta/callback`;
      const res = await api.integrations.getMetaAuthUrl(currentProject.id, redirectUri);
      if (res.auth_url) window.location.href = res.auth_url;
    } catch {
      toast.error('Failed to initiate Meta authorization');
    }
  };

  const handleConnectSubmit = () => {
    if (!selectedProvider) return;
    const configData = { ...credentials, auto_sync: true };
    if (configData.whatsappPhoneNumber && !configData.phone_number) {
      configData.phone_number = configData.whatsappPhoneNumber;
    }
    connectMutation.mutate({ provider: selectedProvider.id, config: configData });
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3 text-text-primary tracking-tight">
            <span className="p-2.5 rounded-xl bg-brand-primary/10 border border-brand-primary/20 text-brand-primary">
              <Plug className="w-6 h-6" />
            </span>
            {t('integrations.title')}
          </h1>
          <p className="text-sm text-text-secondary mt-1">{t('integrations.description')}</p>
        </div>
        <div className="flex items-center gap-3">
          <Button onClick={handleMetaConnect} variant="primary" leftIcon={Sparkles}>
            Connect Meta
          </Button>
          <Button onClick={() => navigate('/integrations/manage')} variant="secondary" leftIcon={SettingsIcon}>
            Manage Integrations
          </Button>
        </div>
      </div>

      {/* Integration Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {availableIntegrations.map((integration) => {
          const status = getStatus(integration.id);
          const extId = getIntegrationId(integration.id);
          return (
            <IntegrationCard
              key={integration.id}
              integration={integration}
              status={status}
              hasIntegration={Boolean(extId)}
              existingIntegrationId={extId}
              onConnect={() => { setSelectedProvider(integration); setShowModal(true); }}
              onSync={() => extId && syncMutation.mutate(extId)}
              onVerify={() => {
                if (integration.id === 'whatsapp' && extId) {
                  const waItem = rawList.find((i) => i.id === extId);
                  const isBaileys = waItem?.config?.whatsapp_provider === 'baileys' || waItem?.extra_data?.provider === 'baileys';
                  if (isBaileys) {
                    setActiveWhatsAppIntegrationId(extId);
                    setQrModalOpen(true);
                    return;
                  }
                }
                if (extId) verifyMutation.mutate(extId);
              }}
              onDelete={() => extId && deleteMutation.mutate(extId)}
              onOpenInstructions={() => { setSelectedInstructions(integration); setShowInstructions(true); }}
              isConnecting={connectMutation.isPending && selectedProvider?.id === integration.id}
              isSyncing={syncMutation.isPending}
              isVerifying={verifyMutation.isPending}
              isDeleting={deleteMutation.isPending}
            />
          );
        })}
      </div>

      {/* Connected Integrations List */}
      <ConnectedIntegrationsList
        integrations={connectedIntegrations}
        onDelete={(id) => deleteMutation.mutate(id)}
        onSync={(id) => syncMutation.mutate(id)}
        isDeleting={deleteMutation.isPending}
        isSyncing={syncMutation.isPending}
        onManage={() => navigate('/integrations/manage')}
      />

      {/* Modals */}
      <IntegrationConnectModal
        show={showModal}
        selectedProvider={selectedProvider}
        credentials={credentials}
        setCredentials={setCredentials}
        onClose={() => { setShowModal(false); setSelectedProvider(null); }}
        onSubmit={handleConnectSubmit}
        onMetaConnect={handleMetaConnect}
        isConnecting={connectMutation.isPending}
      />

      <IntegrationInstructionsDrawer
        show={showInstructions}
        integration={selectedInstructions}
        onClose={() => { setShowInstructions(false); setSelectedInstructions(null); }}
      />

      <WhatsAppQRModal
        isOpen={qrModalOpen}
        onClose={() => setQrModalOpen(false)}
        projectId={currentProject?.id}
        integrationId={activeWhatsAppIntegrationId}
      />
    </div>
  );
}
