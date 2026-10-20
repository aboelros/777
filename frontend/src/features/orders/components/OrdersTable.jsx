import { motion, AnimatePresence } from 'framer-motion';
import { Package, Eye, Sparkles, CheckCircle, Trash2, Clock, RefreshCw, Truck, XCircle } from 'lucide-react';
import Badge from '@/components/ui/Badge';
import { formatCurrency, formatDateTime } from '@/utils/helpers';
import { useTranslation } from '@/lib/translations';

const STATUS_VARIANTS = {
  pending: { variant: 'warning', icon: Clock },
  processing: { variant: 'info', icon: RefreshCw },
  fulfilled: { variant: 'success', icon: CheckCircle },
  shipped: { variant: 'brand', icon: Truck },
  cancelled: { variant: 'danger', icon: XCircle },
};

export default function OrdersTable({
  orders,
  onViewOrder,
  onAIProcess,
  onUpdateStatus,
  onDeleteOrder,
  isAIProcessing,
}) {
  const { t } = useTranslation();

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left border-collapse">
        <thead>
          <tr className="border-b border-border bg-surface-subtle/50 text-xs font-semibold text-text-muted uppercase tracking-wider">
            <th className="px-6 py-4">{t('orders.table.id') || 'Order ID'}</th>
            <th className="px-6 py-4">{t('orders.table.customer') || 'Customer'}</th>
            <th className="px-6 py-4">{t('orders.table.date') || 'Date'}</th>
            <th className="px-6 py-4">{t('orders.table.total') || 'Total'}</th>
            <th className="px-6 py-4">{t('orders.table.status') || 'Status'}</th>
            <th className="px-6 py-4 text-right">{t('orders.table.actions') || 'Actions'}</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-border/50 text-sm">
          <AnimatePresence>
            {orders.map((order, index) => {
              const statusMeta = STATUS_VARIANTS[order.status] || STATUS_VARIANTS.pending;
              const StatusIcon = statusMeta.icon;

              return (
                <motion.tr
                  key={order.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  transition={{ delay: index * 0.03 }}
                  className="hover:bg-surface-subtle/70 transition-colors group"
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-2 font-mono font-medium text-text-primary">
                      <Package className="w-4 h-4 text-text-muted" />
                      #{order.external_id || order.id?.slice(0, 8)}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <p className="font-semibold text-text-primary">{order.customer_name || 'Walk-in Customer'}</p>
                    <p className="text-xs text-text-muted">{order.customer_email || order.customer_phone || '—'}</p>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-text-secondary">
                    {formatDateTime(order.order_date, 'short')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap font-mono font-bold text-text-primary">
                    {formatCurrency(order.total, order.currency)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <Badge variant={statusMeta.variant} withDot>
                      <StatusIcon className="w-3 h-3 mr-1 inline" />
                      {t(`orders.filters.${order.status}`) || order.status}
                    </Badge>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right">
                    <div className="flex items-center justify-end gap-1.5">
                      <button
                        onClick={() => onViewOrder(order)}
                        className="p-2 rounded-lg text-text-secondary hover:text-brand-primary hover:bg-brand-primary/10 transition-colors"
                        title={t('orders.actions.view') || 'View Details'}
                        aria-label="View Order"
                      >
                        <Eye className="w-4 h-4" />
                      </button>

                      <button
                        onClick={() => onAIProcess(order.id)}
                        disabled={isAIProcessing}
                        className="p-2 rounded-lg text-text-secondary hover:text-brand-primary hover:bg-brand-primary/10 transition-colors disabled:opacity-40"
                        title={t('orders.actions.ai_process') || 'AI Process'}
                        aria-label="AI Process Order"
                      >
                        <Sparkles className="w-4 h-4" />
                      </button>

                      {order.status !== 'fulfilled' && order.status !== 'cancelled' && (
                        <button
                          onClick={() => onUpdateStatus(order.id, 'fulfilled')}
                          className="p-2 rounded-lg text-text-secondary hover:text-emerald-400 hover:bg-emerald-500/10 transition-colors"
                          title={t('orders.actions.fulfill') || 'Mark Fulfilled'}
                          aria-label="Fulfill Order"
                        >
                          <CheckCircle className="w-4 h-4" />
                        </button>
                      )}

                      <button
                        onClick={() => onDeleteOrder(order.id)}
                        className="p-2 rounded-lg text-text-secondary hover:text-red-400 hover:bg-red-500/10 transition-colors"
                        title={t('orders.actions.delete') || 'Delete'}
                        aria-label="Delete Order"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </motion.tr>
              );
            })}
          </AnimatePresence>
        </tbody>
      </table>
    </div>
  );
}
