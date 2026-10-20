import { motion, AnimatePresence } from 'framer-motion';
import { X, Truck, Package, User, DollarSign } from 'lucide-react';
import Badge from '@/components/ui/Badge';
import { formatCurrency, formatDateTime } from '@/utils/helpers';
import { useTranslation } from '@/lib/translations';

export default function OrderDetailsModal({ show, order, onClose }) {
  const { t } = useTranslation();

  if (!show || !order) return null;

  return (
    <AnimatePresence>
      <div
        className="fixed inset-0 bg-black/70 backdrop-blur-md z-50 flex items-center justify-center p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.96, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.96, opacity: 0 }}
          onClick={(e) => e.stopPropagation()}
          className="w-full max-w-2xl max-h-[90vh] overflow-y-auto glass-card rounded-2xl p-6 sm:p-8 border border-border"
        >
          <div className="flex items-center justify-between mb-6 pb-4 border-b border-border">
            <div>
              <h2 className="text-xl font-bold text-text-primary">
                {t('orders.details.title') || 'Order Details'}
              </h2>
              <p className="text-xs font-mono text-text-muted mt-0.5">#{order.external_id || order.id}</p>
            </div>
            <button
              onClick={onClose}
              className="p-2 rounded-xl text-text-muted hover:text-text-primary hover:bg-surface-subtle transition-colors"
              aria-label="Close details"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="space-y-6">
            {/* Order Primary Details */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-4 rounded-xl bg-surface-subtle border border-border">
              <div>
                <p className="text-xs text-text-muted uppercase tracking-wider mb-1">Status</p>
                <Badge variant={order.status === 'fulfilled' ? 'success' : 'warning'} withDot>
                  {order.status}
                </Badge>
              </div>
              <div>
                <p className="text-xs text-text-muted uppercase tracking-wider mb-1">Order Date</p>
                <p className="text-sm font-medium text-text-primary">{formatDateTime(order.order_date, 'short')}</p>
              </div>
              <div>
                <p className="text-xs text-text-muted uppercase tracking-wider mb-1">Total</p>
                <p className="text-lg font-bold font-mono text-emerald-400">
                  {formatCurrency(order.total, order.currency)}
                </p>
              </div>
              <div>
                <p className="text-xs text-text-muted uppercase tracking-wider mb-1">Items</p>
                <p className="text-sm font-semibold text-text-primary">{order.line_items?.length || 0} items</p>
              </div>
            </div>

            {/* Customer Info */}
            <div className="border border-border rounded-xl p-4 bg-surface-subtle">
              <h3 className="text-sm font-semibold text-text-primary mb-3 flex items-center gap-2">
                <User className="w-4 h-4 text-brand-primary" />
                {t('orders.details.customer_info') || 'Customer Information'}
              </h3>
              <div className="space-y-1 text-sm text-text-secondary">
                <p className="font-semibold text-text-primary">{order.customer?.name || order.customer_name || 'Walk-in Customer'}</p>
                <p>{order.customer?.email || order.customer_email || 'No email provided'}</p>
                <p>{order.customer?.phone || order.customer_phone || 'No phone provided'}</p>
              </div>
            </div>

            {/* Delivery Address */}
            {order.customer?.address && (
              <div className="border border-border rounded-xl p-4 bg-surface-subtle">
                <h3 className="text-sm font-semibold text-text-primary mb-3 flex items-center gap-2">
                  <Truck className="w-4 h-4 text-brand-primary" />
                  {t('orders.details.delivery_address') || 'Shipping Address'}
                </h3>
                <div className="text-sm text-text-secondary">
                  {typeof order.customer.address === 'string' ? (
                    <p>{order.customer.address}</p>
                  ) : (
                    <p>
                      {[
                        order.customer.address.street,
                        order.customer.address.city,
                        order.customer.address.state,
                        order.customer.address.country,
                      ].filter(Boolean).join(', ')}
                    </p>
                  )}
                </div>
              </div>
            )}

            {/* Line Items */}
            {order.line_items && order.line_items.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-text-primary mb-3 flex items-center gap-2">
                  <Package className="w-4 h-4 text-brand-primary" />
                  {t('orders.details.items') || 'Purchased Products'}
                </h3>
                <div className="space-y-2">
                  {order.line_items.map((item, index) => (
                    <div key={index} className="flex items-center justify-between p-3.5 bg-surface-subtle border border-border rounded-xl text-sm">
                      <div>
                        <p className="font-medium text-text-primary">{item.title || item.name}</p>
                        <p className="text-xs text-text-muted">Quantity: {item.quantity}</p>
                      </div>
                      <p className="font-mono font-bold text-text-primary">{formatCurrency(item.price)}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
