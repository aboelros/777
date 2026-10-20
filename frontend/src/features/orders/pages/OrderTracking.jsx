import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Package, Clock, CheckCircle2, TrendingUp, AlertCircle, Play, Send } from 'lucide-react';
import { toast } from 'sonner';
import api from '@/services/api';
import { useProjectStore } from '@/store/projectStore';
import GlassCard from '@/components/ui/GlassCard';
import Button from '@/components/ui/Button';
import Badge from '@/components/ui/Badge';
import { NoProjectState, EmptyState } from '@/components/ui/EmptyState';
import SkeletonLoader from '@/components/ui/SkeletonLoader';
import OrderProgressModal from '../components/OrderProgressModal';

export default function OrderTracking() {
  const { currentProject } = useProjectStore();
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [showProgressModal, setShowProgressModal] = useState(false);
  const queryClient = useQueryClient();

  const { data: statsData } = useQuery({
    queryKey: ['order-stats', currentProject?.id],
    queryFn: async () => {
      const response = await api.get(`/order-management/${currentProject.id}/orders/stats`);
      return response.data;
    },
    enabled: !!currentProject?.id,
  });

  const { data: attentionData, isLoading } = useQuery({
    queryKey: ['orders-attention', currentProject?.id],
    queryFn: async () => {
      const response = await api.get(`/order-management/${currentProject.id}/orders/requiring-attention`);
      return response.data;
    },
    enabled: !!currentProject?.id,
    refetchInterval: 30000,
  });

  const { data: progressData, refetch: refetchProgress } = useQuery({
    queryKey: ['order-progress', selectedOrder],
    queryFn: async () => {
      const response = await api.get(`/order-management/${currentProject.id}/orders/${selectedOrder}/progress`);
      return response.data;
    },
    enabled: !!selectedOrder && !!currentProject?.id,
  });

  const autoProgressMutation = useMutation({
    mutationFn: async (orderId) => {
      const response = await api.post(`/order-management/${currentProject.id}/orders/${orderId}/auto-progress`);
      return response.data;
    },
    onSuccess: (data) => {
      if (data.progressed) {
        toast.success('Order automatically progressed! 🎉');
      } else {
        toast.info(data.reason || 'Order not ready to progress');
      }
      queryClient.invalidateQueries(['orders-attention']);
      queryClient.invalidateQueries(['order-stats']);
      if (selectedOrder) refetchProgress();
    },
  });

  const sendNotificationMutation = useMutation({
    mutationFn: async ({ orderId, messageType }) => {
      const response = await api.post(`/order-management/${currentProject.id}/orders/notify`, {
        order_id: orderId,
        message_type: messageType,
      });
      return response.data;
    },
    onSuccess: () => {
      toast.success('Customer notified! 💬');
      if (selectedOrder) refetchProgress();
    },
  });

  if (!currentProject) {
    return <NoProjectState subtitle="Select a project to monitor active order fulfillment and alerts" />;
  }

  const attentionOrders = attentionData?.orders || [];

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-3 text-text-primary tracking-tight">
          <span className="p-2.5 rounded-xl bg-brand-primary/10 border border-brand-primary/20 text-brand-primary">
            <Package className="w-6 h-6" />
          </span>
          Order Operations & Automation
        </h1>
        <p className="text-sm text-text-secondary mt-1">Autonomous fulfillment monitoring & real-time delivery alerts</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Total Tracked', val: statsData?.total_orders || 0, icon: Package, color: 'text-brand-primary' },
          { label: 'Pending Action', val: statsData?.orders_by_status?.pending || 0, icon: Clock, color: 'text-amber-400' },
          { label: 'In Processing', val: statsData?.orders_by_status?.processing || 0, icon: TrendingUp, color: 'text-sky-400' },
          { label: 'Fulfilled', val: statsData?.orders_by_status?.fulfilled || 0, icon: CheckCircle2, color: 'text-emerald-400' },
        ].map((item, idx) => (
          <GlassCard key={idx} className="p-5 border border-border rounded-2xl flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-wider text-text-muted font-semibold">{item.label}</p>
              <p className="text-2xl font-bold font-mono text-text-primary mt-1">{item.val}</p>
            </div>
            <item.icon className={`w-8 h-8 ${item.color} opacity-80`} />
          </GlassCard>
        ))}
      </div>

      {/* Orders Requiring Attention */}
      <GlassCard className="p-6 rounded-2xl border border-border">
        <div className="flex items-center justify-between mb-6 pb-4 border-b border-border">
          <div className="flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-amber-400" />
            <h2 className="text-lg font-bold text-text-primary">Orders Requiring Operational Review</h2>
          </div>
          <Badge variant="warning">{attentionOrders.length} pending issues</Badge>
        </div>

        {isLoading ? (
          <div className="space-y-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <SkeletonLoader key={i} type="text" lines={2} />
            ))}
          </div>
        ) : attentionOrders.length === 0 ? (
          <div className="text-center py-12">
            <CheckCircle2 className="w-12 h-12 text-emerald-400 mx-auto mb-3" />
            <p className="text-text-primary font-semibold">All orders are progressing normally</p>
            <p className="text-text-muted text-sm mt-1">Autonomous agents are routing messages and processing shipments.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {attentionOrders.map((order) => (
              <div
                key={order.order_id}
                className="p-4 rounded-xl border border-border bg-surface-subtle flex flex-col md:flex-row md:items-center justify-between gap-4"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-mono font-bold text-text-primary">#{order.external_id}</span>
                    <Badge variant="warning">{order.status}</Badge>
                    <span className="text-xs text-text-muted font-mono">{order.age_hours}h ago</span>
                  </div>
                  <p className="text-sm text-text-secondary">
                    {order.customer?.name || 'Customer'} • <strong className="text-text-primary">${order.total}</strong> • {order.reason?.replace(/_/g, ' ')}
                  </p>
                </div>

                <div className="flex items-center gap-2">
                  <Button
                    onClick={() => { setSelectedOrder(order.order_id); setShowProgressModal(true); }}
                    variant="secondary"
                    size="sm"
                  >
                    View Timeline
                  </Button>
                  <Button
                    onClick={() => autoProgressMutation.mutate(order.order_id)}
                    disabled={autoProgressMutation.isPending}
                    variant="primary"
                    size="sm"
                    leftIcon={Play}
                  >
                    Auto-Progress
                  </Button>
                  <Button
                    onClick={() => sendNotificationMutation.mutate({ orderId: order.order_id, messageType: 'processing' })}
                    disabled={sendNotificationMutation.isPending}
                    variant="outline"
                    size="sm"
                    leftIcon={Send}
                  >
                    Notify
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </GlassCard>

      {/* Progress & Timeline Modal */}
      <OrderProgressModal
        show={showProgressModal}
        progressData={progressData}
        onClose={() => { setShowProgressModal(false); setSelectedOrder(null); }}
        onAutoProgress={() => autoProgressMutation.mutate(selectedOrder)}
        onNotifyCustomer={() => sendNotificationMutation.mutate({ orderId: selectedOrder, messageType: 'processing' })}
        isAutoProgressing={autoProgressMutation.isPending}
        isNotifying={sendNotificationMutation.isPending}
      />
    </div>
  );
}
