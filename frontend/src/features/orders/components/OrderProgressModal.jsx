import { motion } from 'framer-motion';
import { X, CheckCircle2, Package, Clock, Truck, MessageSquare } from 'lucide-react';
import Badge from '@/components/ui/Badge';
import Button from '@/components/ui/Button';

export default function OrderProgressModal({
  show,
  progressData,
  onClose,
  onAutoProgress,
  onNotifyCustomer,
  isAutoProgressing,
  isNotifying,
}) {
  if (!show || !progressData) return null;

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-md flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.96 }}
        animate={{ opacity: 1, scale: 1 }}
        className="glass-card rounded-2xl border border-border max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6 sm:p-8"
      >
        <div className="flex items-center justify-between mb-6 pb-4 border-b border-border">
          <div>
            <h3 className="text-xl font-bold text-text-primary">
              Order Lifecycle: #{progressData.external_id || progressData.id}
            </h3>
            <p className="text-xs text-text-muted mt-0.5">Automated fulfillment & customer journey</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-xl text-text-muted hover:text-text-primary hover:bg-surface-subtle transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="space-y-6">
          {/* Progress Bar */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold uppercase tracking-wider text-text-muted">Progress</span>
              <span className="text-sm font-bold font-mono text-brand-primary">
                {progressData.progress_percentage || 0}%
              </span>
            </div>
            <div className="h-2.5 bg-surface-subtle rounded-full overflow-hidden border border-border">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${progressData.progress_percentage || 0}%` }}
                transition={{ duration: 0.8, ease: 'easeOut' }}
                className="h-full bg-brand-primary"
              />
            </div>
          </div>

          {/* Quick Metrics */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3 bg-surface-subtle border border-border rounded-xl">
              <p className="text-[11px] text-text-muted uppercase tracking-wider mb-1">Current State</p>
              <Badge variant="brand">{progressData.current_status || 'Pending'}</Badge>
            </div>
            <div className="p-3 bg-surface-subtle border border-border rounded-xl">
              <p className="text-[11px] text-text-muted uppercase tracking-wider mb-1">Next Step</p>
              <p className="text-sm font-semibold text-text-primary capitalize">{progressData.next_expected_status || 'Complete'}</p>
            </div>
            <div className="p-3 bg-surface-subtle border border-border rounded-xl">
              <p className="text-[11px] text-text-muted uppercase tracking-wider mb-1">Total</p>
              <p className="text-sm font-bold font-mono text-emerald-400">${progressData.total || 0}</p>
            </div>
            <div className="p-3 bg-surface-subtle border border-border rounded-xl">
              <p className="text-[11px] text-text-muted uppercase tracking-wider mb-1">Items</p>
              <p className="text-sm font-semibold text-text-primary">{progressData.items_count || 1} items</p>
            </div>
          </div>

          {/* Timeline */}
          {progressData.timeline && progressData.timeline.length > 0 && (
            <div>
              <h4 className="text-sm font-bold uppercase tracking-wider text-text-muted mb-3">Status Progression</h4>
              <div className="space-y-3">
                {progressData.timeline.map((event, index) => (
                  <div key={index} className="flex gap-3 text-sm">
                    <div className="w-7 h-7 rounded-full bg-brand-primary/10 border border-brand-primary/20 flex items-center justify-center text-brand-primary flex-shrink-0 mt-0.5">
                      <CheckCircle2 className="w-4 h-4" />
                    </div>
                    <div className="flex-1 p-3 bg-surface-subtle border border-border rounded-xl">
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-semibold text-text-primary capitalize">{event.to_status}</span>
                        <span className="text-xs text-text-muted font-mono">{new Date(event.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                      </div>
                      {event.note && <p className="text-xs text-text-secondary">{event.note}</p>}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-3 pt-4 border-t border-border">
            <Button
              onClick={onAutoProgress}
              disabled={isAutoProgressing}
              variant="primary"
              className="flex-1"
            >
              Auto-Progress Next Step
            </Button>
            <Button
              onClick={onNotifyCustomer}
              disabled={isNotifying}
              variant="secondary"
              className="flex-1"
            >
              Send Customer SMS / WhatsApp
            </Button>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
