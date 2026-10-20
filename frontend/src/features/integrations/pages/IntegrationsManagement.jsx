import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Edit, Trash2, RefreshCw, Power, Link as LinkIcon, Settings as SettingsIcon } from 'lucide-react';
import { toast } from 'sonner';
import GlassCard from '@/components/ui/GlassCard';
import Button from '@/components/ui/Button';
import Badge from '@/components/ui/Badge';
import { NoProjectState, EmptyState } from '@/components/ui/EmptyState';
import SkeletonLoader from '@/components/ui/SkeletonLoader';
import api from '@/services/api';
import { useProjectStore } from '@/store/projectStore';
import IntegrationManageModal from '../components/IntegrationManageModal';

export default function IntegrationsManagement() {
  const { currentProject } = useProjectStore();
  const queryClient = useQueryClient();

  const [showModal, setShowModal] = useState(false);
  const [editingIntegration, setEditingIntegration] = useState(null);
  const [formData, setFormData] = useState({
    provider: '',
    name: '',
    apiKey: '',
    apiSecret: '',
    webhookUrl: '',
    config: {},
  });

  const { data: integrationsData, isLoading } = useQuery({
    queryKey: ['integrations', currentProject?.id],
    queryFn: () => api.integrations.list(currentProject?.id),
    enabled: !!currentProject?.id,
  });

  const rawList = integrationsData?.data || (Array.isArray(integrationsData) ? integrationsData : []);

  const createMutation = useMutation({
    mutationFn: (data) => api.integrations.create(currentProject?.id, data),
    onSuccess: () => {
      toast.success('Integration created');
      queryClient.invalidateQueries(['integrations']);
      resetForm();
    },
    onError: (err) => toast.error(err.response?.data?.detail || 'Failed to create'),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => api.integrations.update(currentProject?.id, id, data),
    onSuccess: () => {
      toast.success('Integration updated');
      queryClient.invalidateQueries(['integrations']);
      resetForm();
    },
    onError: (err) => toast.error(err.response?.data?.detail || 'Failed to update'),
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => api.integrations.delete(currentProject?.id, id),
    onSuccess: () => {
      toast.success('Integration deleted');
      queryClient.invalidateQueries(['integrations']);
    },
  });

  const syncMutation = useMutation({
    mutationFn: (id) => api.integrations.sync(currentProject?.id, id),
    onSuccess: () => toast.success('Sync started'),
  });

  const testMutation = useMutation({
    mutationFn: (id) => api.integrations.test(currentProject?.id, id),
    onSuccess: () => toast.success('Connection verified successfully'),
    onError: () => toast.error('Connection test failed'),
  });

  const resetForm = () => {
    setFormData({ provider: '', name: '', apiKey: '', apiSecret: '', webhookUrl: '', config: {} });
    setShowModal(false);
    setEditingIntegration(null);
  };

  const handleEdit = (integration) => {
    setEditingIntegration(integration);
    setFormData({
      provider: integration.provider,
      name: integration.name || '',
      apiKey: '••••••••',
      apiSecret: '••••••••',
      webhookUrl: integration.webhook_url || '',
      config: integration.config || {},
    });
    setShowModal(true);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const payload = {
      provider: formData.provider,
      name: formData.name || formData.provider,
      credentials: {
        api_key: formData.apiKey,
        api_secret: formData.apiSecret,
        webhook_url: formData.webhookUrl,
      },
      config: { ...formData.config },
    };

    if (editingIntegration) {
      updateMutation.mutate({ id: editingIntegration.id, data: payload });
    } else {
      createMutation.mutate(payload);
    }
  };

  if (!currentProject) {
    return <NoProjectState subtitle="Select a project to manage platform API credentials and webhook endpoints" />;
  }

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3 text-text-primary tracking-tight">
            <span className="p-2.5 rounded-xl bg-brand-primary/10 border border-brand-primary/20 text-brand-primary">
              <SettingsIcon className="w-6 h-6" />
            </span>
            Integrations Manager
          </h1>
          <p className="text-sm text-text-secondary mt-1">Direct credential tokens and webhook configuration</p>
        </div>
        <Button onClick={() => setShowModal(true)} variant="primary" leftIcon={Plus}>
          Add Integration
        </Button>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <SkeletonLoader key={i} type="card" />
          ))}
        </div>
      ) : rawList.length === 0 ? (
        <EmptyState
          icon={LinkIcon}
          title="No Integrations Configured"
          description="Create a custom webhook or platform connection to link third-party services."
          actionLabel="Add Integration"
          onAction={() => setShowModal(true)}
        />
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {rawList.map((item) => (
            <GlassCard key={item.id} className="p-5 border border-border rounded-2xl flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <h3 className="font-bold text-text-primary text-base">{item.name || item.provider}</h3>
                    <span className="text-xs font-mono uppercase text-text-muted">{item.provider}</span>
                  </div>
                  <Badge variant={item.status === 'connected' ? 'success' : 'default'} withDot>
                    {item.status}
                  </Badge>
                </div>

                {item.webhook_url && (
                  <p className="text-xs font-mono text-text-muted truncate mb-3 p-2 rounded-lg bg-surface-subtle">
                    {item.webhook_url}
                  </p>
                )}
              </div>

              <div className="flex items-center gap-2 pt-3 border-t border-border">
                <Button onClick={() => syncMutation.mutate(item.id)} variant="secondary" size="sm" className="flex-1" leftIcon={RefreshCw}>
                  Sync
                </Button>
                <Button onClick={() => testMutation.mutate(item.id)} variant="secondary" size="sm" className="flex-1" leftIcon={Power}>
                  Test
                </Button>
                <Button onClick={() => handleEdit(item)} variant="outline" size="sm" className="px-3" title="Edit">
                  <Edit className="w-4 h-4" />
                </Button>
                <Button
                  onClick={() => {
                    if (window.confirm('Delete this integration?')) deleteMutation.mutate(item.id);
                  }}
                  variant="danger"
                  size="sm"
                  className="px-3"
                  title="Delete"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </GlassCard>
          ))}
        </div>
      )}

      <IntegrationManageModal
        show={showModal}
        isEditing={Boolean(editingIntegration)}
        formData={formData}
        setFormData={setFormData}
        onClose={resetForm}
        onSubmit={handleSubmit}
      />
    </div>
  );
}
