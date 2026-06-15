import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import {
  Package,
  Clock,
  CheckCircle2,
  XCircle,
  Truck,
  MessageSquare,
  TrendingUp,
  AlertCircle,
  Send,
  Play,
  MoreVertical,
  Calendar,
  User,
  DollarSign
} from 'lucide-react';
import GlassCard from '../components/GlassCard';
import api from '../services/api';
import { useProjectStore } from '../store/projectStore';
import { toast } from 'sonner';

export default function OrderTracking() {
  const { currentProject } = useProjectStore();
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [showProgressModal, setShowProgressModal] = useState(false);
  const queryClient = useQueryClient();

  // Fetch order statistics
  const { data: statsData } = useQuery({
    queryKey: ['order-stats', currentProject?.id],
    queryFn: async () => {
      const response = await api.get(`/order-management/${currentProject.id}/orders/stats`);
      return response.data;
    },
    enabled: !!currentProject,
  });

  // Fetch orders requiring attention
  const { data: attentionData, isLoading } = useQuery({
    queryKey: ['orders-attention', currentProject?.id],
    queryFn: async () => {
      const response = await api.get(`/order-management/${currentProject.id}/orders/requiring-attention`);
      return response.data;
    },
    enabled: !!currentProject,
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  // Fetch order progress
  const { data: progressData, refetch: refetchProgress } = useQuery({
    queryKey: ['order-progress', selectedOrder],
    queryFn: async () => {
      const response = await api.get(`/order-management/${currentProject.id}/orders/${selectedOrder}/progress`);
      return response.data;
    },
    enabled: !!selectedOrder,
  });

  // Update order status mutation
  const updateStatusMutation = useMutation({
    mutationFn: async ({ orderId, status }) => {
      const response = await api.post(`/order-management/${currentProject.id}/orders/update-status`, {
        order_id: orderId,
        new_status: status,
        notify_customer: true,
        auto_message: true,
      });
      return response.data;
    },
    onSuccess: () => {
      toast.success('Order status updated and customer notified! 📦');
      queryClient.invalidateQueries(['orders-attention']);
      queryClient.invalidateQueries(['order-stats']);
      if (selectedOrder) refetchProgress();
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Failed to update order');
    },
  });

  // Auto-progress order mutation
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

  // Send notification mutation
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

  const getStatusColor = (status) => {
    const colors = {
      pending: 'bg-yellow-500/20 text-yellow-400',
      processing: 'bg-blue-500/20 text-blue-400',
      shipped: 'bg-purple-500/20 text-purple-400',
      fulfilled: 'bg-green-500/20 text-green-400',
      cancelled: 'bg-red-500/20 text-red-400',
    };
    return colors[status?.toLowerCase()] || 'bg-gray-500/20 text-gray-400';
  };

  const getStatusIcon = (status) => {
    const icons = {
      pending: Clock,
      processing: Package,
      shipped: Truck,
      fulfilled: CheckCircle2,
      cancelled: XCircle,
    };
    const Icon = icons[status?.toLowerCase()] || Package;
    return <Icon className="w-5 h-5" />;
  };

  return (
    <div className="min-h-screen bg-dark-950 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-accent-400 to-accent-600 bg-clip-text text-transparent">
              Order Management
            </h1>
            <p className="text-gray-400 mt-1">AI-powered order tracking and automation</p>
          </div>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {statsData && (
            <>
              <GlassCard className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-400">Total Orders</p>
                    <p className="text-2xl font-bold text-white mt-1">
                      {statsData.total_orders}
                    </p>
                  </div>
                  <Package className="w-10 h-10 text-accent-400" />
                </div>
              </GlassCard>

              <GlassCard className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-400">Pending</p>
                    <p className="text-2xl font-bold text-yellow-400 mt-1">
                      {statsData.orders_by_status?.pending || 0}
                    </p>
                  </div>
                  <Clock className="w-10 h-10 text-yellow-400" />
                </div>
              </GlassCard>

              <GlassCard className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-400">Processing</p>
                    <p className="text-2xl font-bold text-blue-400 mt-1">
                      {statsData.orders_by_status?.processing || 0}
                    </p>
                  </div>
                  <TrendingUp className="w-10 h-10 text-blue-400" />
                </div>
              </GlassCard>

              <GlassCard className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-400">Fulfilled</p>
                    <p className="text-2xl font-bold text-green-400 mt-1">
                      {statsData.orders_by_status?.fulfilled || 0}
                    </p>
                  </div>
                  <CheckCircle2 className="w-10 h-10 text-green-400" />
                </div>
              </GlassCard>
            </>
          )}
        </div>

        {/* Orders Requiring Attention */}
        <GlassCard className="p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <AlertCircle className="w-6 h-6 text-yellow-400" />
              <h2 className="text-xl font-semibold text-white">
                Orders Requiring Attention
              </h2>
            </div>
            <span className="px-3 py-1 bg-yellow-500/20 text-yellow-400 rounded-full text-sm font-medium">
              {attentionData?.total || 0} orders
            </span>
          </div>

          {isLoading ? (
            <div className="text-center py-8 text-gray-400">Loading orders...</div>
          ) : attentionData?.orders?.length === 0 ? (
            <div className="text-center py-12">
              <CheckCircle2 className="w-16 h-16 text-green-400 mx-auto mb-4" />
              <p className="text-gray-400 text-lg">All orders are on track! 🎉</p>
            </div>
          ) : (
            <div className="space-y-3">
              {attentionData?.orders?.map((order) => (
                <motion.div
                  key={order.order_id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-dark-800/50 rounded-lg p-4 border border-accent-500/20 hover:border-accent-500/40 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        {getStatusIcon(order.status)}
                        <span className="font-semibold text-white">
                          Order #{order.external_id}
                        </span>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(order.status)}`}>
                          {order.status}
                        </span>
                        <span className="text-xs text-gray-400">
                          {order.age_hours}h ago
                        </span>
                      </div>

                      <div className="flex items-center gap-6 text-sm text-gray-400">
                        <div className="flex items-center gap-2">
                          <User className="w-4 h-4" />
                          {order.customer?.name || 'Unknown'}
                        </div>
                        <div className="flex items-center gap-2">
                          <DollarSign className="w-4 h-4" />
                          ${order.total}
                        </div>
                        <div className="flex items-center gap-2">
                          <AlertCircle className="w-4 h-4" />
                          {order.reason.replace('_', ' ')}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => {
                          setSelectedOrder(order.order_id);
                          setShowProgressModal(true);
                        }}
                        className="px-4 py-2 bg-accent-500/20 hover:bg-accent-500/30 text-accent-400 rounded-lg transition-colors text-sm font-medium"
                      >
                        View Progress
                      </button>
                      
                      <button
                        onClick={() => autoProgressMutation.mutate(order.order_id)}
                        disabled={autoProgressMutation.isLoading}
                        className="p-2 bg-blue-500/20 hover:bg-blue-500/30 text-blue-400 rounded-lg transition-colors"
                        title="Auto-progress order"
                      >
                        <Play className="w-5 h-5" />
                      </button>

                      <button
                        onClick={() => sendNotificationMutation.mutate({ 
                          orderId: order.order_id,
                          messageType: 'processing'
                        })}
                        disabled={sendNotificationMutation.isLoading}
                        className="p-2 bg-green-500/20 hover:bg-green-500/30 text-green-400 rounded-lg transition-colors"
                        title="Notify customer"
                      >
                        <Send className="w-5 h-5" />
                      </button>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </GlassCard>

        {/* Order Progress Modal */}
        {showProgressModal && selectedOrder && progressData && (
          <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-dark-900 rounded-xl border border-accent-500/30 max-w-3xl w-full max-h-[90vh] overflow-y-auto"
            >
              <div className="p-6 border-b border-accent-500/20">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-xl font-bold text-white">
                      Order #{progressData.external_id}
                    </h3>
                    <p className="text-sm text-gray-400 mt-1">
                      Complete order progress and timeline
                    </p>
                  </div>
                  <button
                    onClick={() => {
                      setShowProgressModal(false);
                      setSelectedOrder(null);
                    }}
                    className="text-gray-400 hover:text-white transition-colors"
                  >
                    <XCircle className="w-6 h-6" />
                  </button>
                </div>
              </div>

              <div className="p-6 space-y-6">
                {/* Progress Bar */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-400">Progress</span>
                    <span className="text-sm font-semibold text-accent-400">
                      {progressData.progress_percentage}%
                    </span>
                  </div>
                  <div className="h-3 bg-dark-800 rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${progressData.progress_percentage}%` }}
                      transition={{ duration: 1, ease: 'easeOut' }}
                      className="h-full bg-gradient-to-r from-accent-500 to-accent-600"
                    />
                  </div>
                </div>

                {/* Status and Details */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-dark-800/50 rounded-lg p-4">
                    <p className="text-sm text-gray-400 mb-1">Current Status</p>
                    <div className="flex items-center gap-2">
                      {getStatusIcon(progressData.current_status)}
                      <span className="font-semibold text-white capitalize">
                        {progressData.current_status}
                      </span>
                    </div>
                  </div>

                  <div className="bg-dark-800/50 rounded-lg p-4">
                    <p className="text-sm text-gray-400 mb-1">Next Status</p>
                    <span className="font-semibold text-accent-400 capitalize">
                      {progressData.next_expected_status || 'Complete'}
                    </span>
                  </div>

                  <div className="bg-dark-800/50 rounded-lg p-4">
                    <p className="text-sm text-gray-400 mb-1">Order Total</p>
                    <span className="font-semibold text-white">
                      ${progressData.total}
                    </span>
                  </div>

                  <div className="bg-dark-800/50 rounded-lg p-4">
                    <p className="text-sm text-gray-400 mb-1">Items</p>
                    <span className="font-semibold text-white">
                      {progressData.items_count} items
                    </span>
                  </div>
                </div>

                {/* Timeline */}
                <div>
                  <h4 className="text-lg font-semibold text-white mb-4">Status Timeline</h4>
                  <div className="space-y-4">
                    {progressData.timeline?.map((event, index) => (
                      <div key={index} className="flex gap-4">
                        <div className="flex flex-col items-center">
                          <div className={`w-10 h-10 rounded-full flex items-center justify-center ${getStatusColor(event.to_status)}`}>
                            {getStatusIcon(event.to_status)}
                          </div>
                          {index < progressData.timeline.length - 1 && (
                            <div className="w-0.5 h-12 bg-accent-500/20" />
                          )}
                        </div>
                        <div className="flex-1 pb-4">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="font-semibold text-white capitalize">
                              {event.to_status}
                            </span>
                            {event.automated && (
                              <span className="px-2 py-0.5 bg-blue-500/20 text-blue-400 text-xs rounded">
                                Auto
                              </span>
                            )}
                          </div>
                          <p className="text-sm text-gray-400">
                            {new Date(event.timestamp).toLocaleString()}
                          </p>
                          {event.note && (
                            <p className="text-sm text-gray-300 mt-1">{event.note}</p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Customer Notifications */}
                {progressData.notifications_sent?.length > 0 && (
                  <div>
                    <h4 className="text-lg font-semibold text-white mb-4">Customer Notifications</h4>
                    <div className="space-y-3">
                      {progressData.notifications_sent.map((notification) => (
                        <div key={notification.id} className="bg-dark-800/50 rounded-lg p-4">
                          <div className="flex items-start gap-3">
                            <MessageSquare className="w-5 h-5 text-accent-400 mt-1" />
                            <div className="flex-1">
                              <p className="text-sm text-white">{notification.content}</p>
                              <div className="flex items-center gap-4 mt-2 text-xs text-gray-400">
                                <span>{notification.platform}</span>
                                <span>{new Date(notification.created_at).toLocaleString()}</span>
                                <span className="capitalize">{notification.status}</span>
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Actions */}
                <div className="flex gap-3">
                  <button
                    onClick={() => autoProgressMutation.mutate(selectedOrder)}
                    disabled={autoProgressMutation.isLoading}
                    className="flex-1 py-3 bg-accent-500 hover:bg-accent-600 text-white font-semibold rounded-lg transition-colors disabled:opacity-50"
                  >
                    Auto-Progress Order
                  </button>
                  <button
                    onClick={() => sendNotificationMutation.mutate({ 
                      orderId: selectedOrder,
                      messageType: 'processing'
                    })}
                    disabled={sendNotificationMutation.isLoading}
                    className="px-6 py-3 bg-green-500/20 hover:bg-green-500/30 text-green-400 font-semibold rounded-lg transition-colors"
                  >
                    Notify Customer
                  </button>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </div>
    </div>
  );
}
