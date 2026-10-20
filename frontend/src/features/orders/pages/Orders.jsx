import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ShoppingCart, Search, Filter } from 'lucide-react';
import { toast } from 'sonner';
import api from '@/services/api';
import { useProjectStore } from '@/store/projectStore';
import { useTranslation } from '@/lib/translations';
import GlassCard from '@/components/ui/GlassCard';
import Input from '@/components/ui/Input';
import { NoProjectState, EmptyState } from '@/components/ui/EmptyState';
import SkeletonLoader from '@/components/ui/SkeletonLoader';
import OrderStats from '../components/OrderStats';
import OrdersTable from '../components/OrdersTable';
import OrderDetailsModal from '../components/OrderDetailsModal';

const FILTER_TABS = ['all', 'pending', 'processing', 'fulfilled', 'shipped', 'cancelled'];

export default function Orders() {
  const { currentProject } = useProjectStore();
  const { t } = useTranslation();
  const queryClient = useQueryClient();

  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [showDetails, setShowDetails] = useState(false);

  const { data: ordersData, isLoading } = useQuery({
    queryKey: ['orders', currentProject?.id, statusFilter],
    queryFn: () => api.orders.list(currentProject?.id, { status: statusFilter }),
    enabled: !!currentProject?.id,
  });

  const { data: stats } = useQuery({
    queryKey: ['orderStats', currentProject?.id],
    queryFn: () => api.orders.stats(currentProject?.id),
    enabled: !!currentProject?.id,
  });

  const updateStatusMutation = useMutation({
    mutationFn: ({ orderId, status }) => api.orders.updateStatus(orderId, status),
    onSuccess: () => {
      queryClient.invalidateQueries(['orders']);
      queryClient.invalidateQueries(['orderStats']);
      toast.success(t('orders.status_updated') || 'Order status updated');
    },
  });

  const aiProcessMutation = useMutation({
    mutationFn: (orderId) => api.orders.aiProcess(currentProject?.id, orderId),
    onSuccess: () => {
      queryClient.invalidateQueries(['orders']);
      toast.success('AI processing initiated');
    },
    onError: () => toast.error('AI processing failed'),
  });

  const deleteOrderMutation = useMutation({
    mutationFn: (orderId) => api.orders.delete(currentProject?.id, orderId),
    onSuccess: () => {
      queryClient.invalidateQueries(['orders']);
      queryClient.invalidateQueries(['orderStats']);
      toast.success(t('orders.deleted') || 'Order deleted');
      setShowDetails(false);
    },
  });

  if (!currentProject) {
    return <NoProjectState subtitle={t('orders.subtitle') || 'Select a project to review and manage customer orders'} />;
  }

  const rawOrders = ordersData?.orders || [];
  const filteredOrders = rawOrders.filter((order) =>
    searchQuery === '' ||
    order.customer_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    order.customer_email?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    order.external_id?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-3 text-text-primary tracking-tight">
          <span className="p-2.5 rounded-xl bg-brand-primary/10 border border-brand-primary/20 text-brand-primary">
            <ShoppingCart className="w-6 h-6" />
          </span>
          {t('orders.title')}
        </h1>
        <p className="text-sm text-text-secondary mt-1">{t('orders.subtitle')}</p>
      </div>

      {/* Analytics KPI Cards */}
      <OrderStats stats={stats} />

      {/* Search & Filter Bar */}
      <div className="glass-panel p-4 rounded-2xl border border-border flex flex-col md:flex-row gap-4 justify-between items-stretch md:items-center">
        <div className="flex-1 max-w-md">
          <Input
            icon={Search}
            placeholder={t('orders.search_placeholder') || 'Search by customer name, email, or order ID...'}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="flex flex-wrap gap-1.5">
          {FILTER_TABS.map((status) => {
            const isActive = statusFilter === status;
            return (
              <button
                key={status}
                onClick={() => setStatusFilter(status)}
                className={`px-3 py-1.5 rounded-xl text-xs font-semibold uppercase tracking-wider transition-all border ${
                  isActive
                    ? 'bg-brand-primary text-white border-brand-primary shadow-sm'
                    : 'bg-surface-subtle border-border text-text-muted hover:text-text-primary hover:bg-surface-hover'
                }`}
              >
                {t(`orders.filters.${status}`) || status}
              </button>
            );
          })}
        </div>
      </div>

      {/* Orders Table Container */}
      <GlassCard className="rounded-2xl border border-border overflow-hidden">
        {isLoading ? (
          <div className="p-6 space-y-4">
            {Array.from({ length: 5 }).map((_, i) => (
              <SkeletonLoader key={i} type="text" lines={2} />
            ))}
          </div>
        ) : filteredOrders.length === 0 ? (
          <EmptyState
            icon={ShoppingCart}
            title={t('orders.empty.title') || 'No Orders Recorded'}
            description={t('orders.empty.subtitle') || 'Customer transactions through WhatsApp and online storefronts will appear here automatically.'}
          />
        ) : (
          <OrdersTable
            orders={filteredOrders}
            onViewOrder={(order) => { setSelectedOrder(order); setShowDetails(true); }}
            onAIProcess={(id) => aiProcessMutation.mutate(id)}
            onUpdateStatus={(id, status) => updateStatusMutation.mutate({ orderId: id, status })}
            onDeleteOrder={(id) => {
              if (window.confirm(t('orders.actions.delete_confirm') || 'Delete this order?')) {
                deleteOrderMutation.mutate(id);
              }
            }}
            isAIProcessing={aiProcessMutation.isPending}
          />
        )}
      </GlassCard>

      {/* Details Modal */}
      <OrderDetailsModal
        show={showDetails}
        order={selectedOrder}
        onClose={() => setShowDetails(false)}
      />
    </div>
  );
}
