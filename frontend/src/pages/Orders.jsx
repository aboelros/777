import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ShoppingCart,
  Package,
  Truck,
  CheckCircle,
  XCircle,
  Clock,
  Search,
  Filter,
  Download,
  Eye,
  Edit,
  RefreshCw,
  TrendingUp,
  DollarSign,
  AlertCircle,
  Sparkles,
  Trash2
} from 'lucide-react';
import GlassCard from '../components/GlassCard';
import api from '../services/api';
import { useProjectStore } from '../store/projectStore';
import { formatCurrency, formatDateTime } from '../utils/helpers';
import { toast } from 'sonner';
import useThemeStore from '../store/themeStore';
import { useTranslation } from '../lib/translations';

const STATUS_CONFIG = {
  pending: {
    icon: Clock,
    color: 'text-yellow-400',
    bg: 'bg-yellow-500/20',
    border: 'border-yellow-500/50',
    label: 'Pending'
  },
  processing: {
    icon: RefreshCw,
    color: 'text-blue-400',
    bg: 'bg-blue-500/20',
    border: 'border-blue-500/50',
    label: 'Processing'
  },
  fulfilled: {
    icon: CheckCircle,
    color: 'text-green-400',
    bg: 'bg-green-500/20',
    border: 'border-green-500/50',
    label: 'Fulfilled'
  },
  shipped: {
    icon: Truck,
    color: 'text-purple-400',
    bg: 'bg-purple-500/20',
    border: 'border-purple-500/50',
    label: 'Shipped'
  },
  cancelled: {
    icon: XCircle,
    color: 'text-red-400',
    bg: 'bg-red-500/20',
    border: 'border-red-500/50',
    label: 'Cancelled'
  }
};

export default function Orders() {
  const { currentProject } = useProjectStore();
  const { t } = useTranslation();
  const queryClient = useQueryClient();

  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [showDetails, setShowDetails] = useState(false);

  // Fetch orders
  const { data: ordersData, isLoading } = useQuery({
    queryKey: ['orders', currentProject?.id, statusFilter],
    queryFn: () => api.orders.list(currentProject?.id, { status: statusFilter }),
    enabled: !!currentProject,
  });

  // Fetch order stats
  const { data: stats } = useQuery({
    queryKey: ['orderStats', currentProject?.id],
    queryFn: () => api.orders.stats(currentProject?.id),
    enabled: !!currentProject,
  });

  // Update order status mutation
  const updateStatusMutation = useMutation({
    mutationFn: ({ orderId, status }) => api.orders.updateStatus(orderId, status),
    onSuccess: () => {
      queryClient.invalidateQueries(['orders']);
      queryClient.invalidateQueries(['orderStats']);
    },
  });

  // AI process order mutation
  const aiProcessMutation = useMutation({
    mutationFn: (orderId) => api.orders.aiProcess(currentProject?.id, orderId),
    onSuccess: () => {
      queryClient.invalidateQueries(['orders']);
      toast.success('AI processing started');
    },
    onError: (err) => {
      toast.error('AI processing failed');
    }
  });

  // Delete order mutation
  const deleteOrderMutation = useMutation({
    mutationFn: (orderId) => api.orders.delete(currentProject?.id, orderId),
    onSuccess: () => {
      queryClient.invalidateQueries(['orders']);
      queryClient.invalidateQueries(['orderStats']);
      toast.success('Order deleted successfully');
      setShowDetails(false);
    },
    onError: (error) => {
      toast.error(`Failed to delete order: ${error.message}`);
    }
  });

  const handleDeleteOrder = (orderId) => {
    if (window.confirm(t('orders.actions.delete_confirm'))) {
      deleteOrderMutation.mutate(orderId);
    }
  };

  const handleUpdateStatus = (orderId, newStatus) => {
    updateStatusMutation.mutate({ orderId, status: newStatus });
  };

  const handleAIProcess = (orderId) => {
    aiProcessMutation.mutate(orderId);
  };

  const filteredOrders = ordersData?.orders?.filter(order =>
    searchQuery === '' ||
    order.customer_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    order.customer_email?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    order.external_id?.toLowerCase().includes(searchQuery.toLowerCase())
  ) || [];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-4 sm:p-6 lg:p-8" >
      <div className="max-w-[1800px] mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-green-400 via-blue-400 to-purple-400 mb-2 flex items-center gap-3">
            <ShoppingCart className="w-10 h-10 text-green-400" />
            {t('orders.title')}
          </h1>
          <p className="text-slate-400">{t('orders.subtitle')}</p>
        </motion.div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {[
            {
              title: t('orders.stats.total_orders'),
              value: stats?.total_orders || 0,
              change: '+12.5%',
              icon: ShoppingCart,
              color: 'from-blue-500 to-cyan-500'
            },
            {
              title: t('orders.stats.total_revenue'),
              value: formatCurrency(stats?.total_revenue || 0),
              change: '+18.2%',
              icon: DollarSign,
              color: 'from-green-500 to-emerald-500'
            },
            {
              title: t('orders.stats.pending_orders'),
              value: stats?.pending_orders || 0,
              change: '-5.4%',
              icon: Clock,
              color: 'from-yellow-500 to-orange-500'
            },
            {
              title: t('orders.stats.fulfillment_rate'),
              value: `${stats?.fulfillment_rate || 0}%`,
              change: '+3.1%',
              icon: TrendingUp,
              color: 'from-purple-500 to-pink-500'
            }
          ].map((stat, index) => (
            <motion.div
              key={stat.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <GlassCard className="relative overflow-hidden group hover:scale-105 transition-transform">
                <div className={`absolute inset-0 bg-gradient-to-br ${stat.color} opacity-10 group-hover:opacity-20 transition-opacity`} />
                <div className="relative p-6">
                  <div className="flex items-center justify-between mb-4">
                    <stat.icon className="w-8 h-8 text-slate-400" />
                    <span className={`text-xs font-medium px-2 py-1 rounded-full ${stat.change.startsWith('+')
                      ? 'bg-green-500/20 text-green-400'
                      : 'bg-red-500/20 text-red-400'
                      }`}>
                      {stat.change}
                    </span>
                  </div>
                  <p className="text-slate-400 text-sm mb-1">{stat.title}</p>
                  <p className="text-3xl font-bold text-white">{stat.value}</p>
                </div>
              </GlassCard>
            </motion.div>
          ))}
        </div>

        {/* Filters and Search */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="mb-6"
        >
          <GlassCard className="p-4">
            <div className="flex flex-col lg:flex-row gap-4">
              {/* Search */}
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                <input
                  type="text"
                  placeholder={t('orders.search_placeholder')}
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 bg-white/5 border border-white/10 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500/50 transition-all"
                />
              </div>

              {/* Status Filter */}
              <div className="flex flex-wrap gap-2">
                {['all', 'pending', 'processing', 'fulfilled', 'shipped', 'cancelled'].map((status) => {
                  const config = STATUS_CONFIG[status];
                  const isActive = statusFilter === status;

                  return (
                    <motion.button
                      key={status}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => setStatusFilter(status)}
                      className={`px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2 ${isActive
                        ? 'bg-purple-500/20 text-purple-300 ring-1 ring-purple-500/50'
                        : 'bg-white/5 text-slate-400 hover:bg-white/10'
                        }`}
                    >
                      {config && <config.icon className="w-4 h-4" />}
                      {t(`orders.filters.${status}`)}
                    </motion.button>
                  );
                })}
              </div>
            </div>
          </GlassCard>
        </motion.div>

        {/* Orders Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <GlassCard className="overflow-hidden">
            {isLoading ? (
              <div className="flex items-center justify-center h-64">
                <div className="animate-spin w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full" />
              </div>
            ) : filteredOrders.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-64 text-slate-400">
                <ShoppingCart className="w-20 h-20 mb-4 opacity-20" />
                <p className="text-xl font-medium mb-2">{t('orders.empty.title')}</p>
                <p className="text-center">{t('orders.empty.subtitle')}</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-white/10 bg-white/5">
                      <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                        {t('orders.table.id')}
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                        {t('orders.table.customer')}
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                        {t('orders.table.date')}
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                        {t('orders.table.total')}
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                        {t('orders.table.status')}
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                        {t('orders.table.actions')}
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    <AnimatePresence>
                      {filteredOrders.map((order, index) => {
                        const statusConfig = STATUS_CONFIG[order.status] || STATUS_CONFIG.pending;
                        const StatusIcon = statusConfig.icon;

                        return (
                          <motion.tr
                            key={order.id}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            transition={{ delay: index * 0.05 }}
                            className="hover:bg-white/5 transition-colors group"
                          >
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="flex items-center gap-2">
                                <Package className="w-4 h-4 text-slate-400" />
                                <span className="text-white font-medium">#{order.external_id}</span>
                              </div>
                            </td>
                            <td className="px-6 py-4">
                              <div>
                                <p className="text-white font-medium">{order.customer_name}</p>
                                <p className="text-xs text-slate-400">{order.customer_email}</p>
                              </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-slate-300">
                              {formatDateTime(order.order_date, 'short')}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className="text-white font-semibold">
                                {formatCurrency(order.total, order.currency)}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium ${statusConfig.bg} ${statusConfig.color} border ${statusConfig.border}`}>
                                <StatusIcon className="w-3 h-3" />
                                {t(`orders.filters.${order.status}`)}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="flex items-center gap-2">
                                <motion.button
                                  whileHover={{ scale: 1.1 }}
                                  whileTap={{ scale: 0.9 }}
                                  onClick={() => {
                                    setSelectedOrder(order);
                                    setShowDetails(true);
                                  }}
                                  className="p-2 bg-blue-500/20 text-blue-400 rounded-lg hover:bg-blue-500/30 transition-colors"
                                  title={t('orders.actions.view')}
                                >
                                  <Eye className="w-4 h-4" />
                                </motion.button>

                                <motion.button
                                  whileHover={{ scale: 1.1 }}
                                  whileTap={{ scale: 0.9 }}
                                  onClick={() => handleAIProcess(order.id)}
                                  disabled={aiProcessMutation.isLoading}
                                  className="p-2 bg-purple-500/20 text-purple-400 rounded-lg hover:bg-purple-500/30 transition-colors disabled:opacity-50"
                                  title={t('orders.actions.ai_process')}
                                >
                                  <Sparkles className="w-4 h-4" />
                                </motion.button>

                                {order.status !== 'fulfilled' && order.status !== 'cancelled' && (
                                  <motion.button
                                    whileHover={{ scale: 1.1 }}
                                    whileTap={{ scale: 0.9 }}
                                    onClick={() => handleUpdateStatus(order.id, 'fulfilled')}
                                    className="p-2 bg-green-500/20 text-green-400 rounded-lg hover:bg-green-500/30 transition-colors"
                                    title={t('orders.actions.fulfill')}
                                  >
                                    <CheckCircle className="w-4 h-4" />
                                  </motion.button>
                                )}

                                <motion.button
                                  whileHover={{ scale: 1.1 }}
                                  whileTap={{ scale: 0.9 }}
                                  onClick={() => handleDeleteOrder(order.id)}
                                  className="p-2 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 transition-colors"
                                  title={t('orders.actions.delete')}
                                >
                                  <Trash2 className="w-4 h-4" />
                                </motion.button>
                              </div>
                            </td>
                          </motion.tr>
                        );
                      })}
                    </AnimatePresence>
                  </tbody>
                </table>
              </div>
            )}
          </GlassCard>
        </motion.div>

        {/* Order Details Modal */}
        <AnimatePresence>
          {showDetails && selectedOrder && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
              onClick={() => setShowDetails(false)}
            >
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
                onClick={(e) => e.stopPropagation()}
                className="w-full max-w-2xl max-h-[90vh] overflow-y-auto"
              >
                <GlassCard className="p-6">
                  <div className="flex items-center justify-between mb-6">
                    <h2 className="text-2xl font-bold text-white">{t('orders.details.title')}</h2>
                    <button
                      onClick={() => setShowDetails(false)}
                      className="text-slate-400 hover:text-white transition-colors"
                    >
                      <XCircle className="w-6 h-6" />
                    </button>
                  </div>

                  <div className="space-y-6">
                    {/* Order Info */}
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-slate-400 text-sm mb-1">Order ID</p>
                        <p className="text-white font-medium">#{selectedOrder.external_id}</p>
                      </div>
                      <div>
                        <p className="text-slate-400 text-sm mb-1">Date</p>
                        <p className="text-white font-medium">{formatDateTime(selectedOrder.order_date)}</p>
                      </div>
                      <div>
                        <p className="text-slate-400 text-sm mb-1">{t('orders.table.status')}</p>
                        <span className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium ${STATUS_CONFIG[selectedOrder.status]?.bg} ${STATUS_CONFIG[selectedOrder.status]?.color}`}>
                          {t(`orders.filters.${selectedOrder.status}`)}
                        </span>
                      </div>
                      <div>
                        <p className="text-slate-400 text-sm mb-1">Total</p>
                        <p className="text-white font-bold text-lg">{formatCurrency(selectedOrder.total, selectedOrder.currency)}</p>
                      </div>
                    </div>

                    {/* Customer Info */}
                    <div className="border-t border-white/10 pt-6">
                      <h3 className="text-lg font-semibold text-white mb-4">{t('orders.details.customer_info')}</h3>
                      <div className="space-y-2">
                        <p className="text-white">{selectedOrder.customer?.name || selectedOrder.customer_name}</p>
                        <p className="text-slate-400">{selectedOrder.customer?.email || selectedOrder.customer_email}</p>
                        <p className="text-slate-400">{selectedOrder.customer?.phone || selectedOrder.customer_phone}</p>
                      </div>
                    </div>

                    {/* Delivery Address */}
                    {selectedOrder.customer?.address && (
                      <div className="border-t border-white/10 pt-6">
                        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                          <Truck className="w-5 h-5 text-purple-400" />
                          {t('orders.details.delivery_address')}
                        </h3>
                        <div className="bg-white/5 rounded-lg p-4 space-y-1">
                          {typeof selectedOrder.customer.address === 'string' ? (
                            <p className="text-slate-300">{selectedOrder.customer.address}</p>
                          ) : (
                            <>
                              {selectedOrder.customer.address.street && (
                                <p className="text-slate-300">{selectedOrder.customer.address.street}</p>
                              )}
                              {selectedOrder.customer.address.city && (
                                <p className="text-slate-300">
                                  {selectedOrder.customer.address.city}
                                  {selectedOrder.customer.address.state && `, ${selectedOrder.customer.address.state}`}
                                  {selectedOrder.customer.address.zip && ` ${selectedOrder.customer.address.zip}`}
                                </p>
                              )}
                              {selectedOrder.customer.address.country && (
                                <p className="text-slate-300">{selectedOrder.customer.address.country}</p>
                              )}
                              {!selectedOrder.customer.address.street && !selectedOrder.customer.address.city && (
                                <p className="text-slate-300">{JSON.stringify(selectedOrder.customer.address)}</p>
                              )}
                            </>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Items */}
                    {selectedOrder.line_items && selectedOrder.line_items.length > 0 && (
                      <div className="border-t border-white/10 pt-6">
                        <h3 className="text-lg font-semibold text-white mb-4">{t('orders.details.items')}</h3>
                        <div className="space-y-3">
                          {selectedOrder.line_items.map((item, index) => (
                            <div key={index} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                              <div>
                                <p className="text-white font-medium">{item.title || item.name}</p>
                                <p className="text-sm text-slate-400">{t('orders.details.quantity')}: {item.quantity}</p>
                              </div>
                              <p className="text-white font-semibold">{formatCurrency(item.price)}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </GlassCard>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div >
  );
}
