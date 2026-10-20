import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { CreditCard, Plus, DollarSign, Receipt, Copy, ExternalLink, Check } from 'lucide-react';
import { toast } from 'sonner';
import { motion, AnimatePresence } from 'framer-motion';
import api from '@/services/api';
import { useProjectStore } from '@/store/projectStore';
import { useTranslation } from '@/lib/translations';
import Button from '@/components/ui/Button';
import Badge from '@/components/ui/Badge';
import Input from '@/components/ui/Input';
import { NoProjectState } from '@/components/ui/EmptyState';

/**
 * Standardized Automio Payments, Invoicing & Quick Checkout
 */
export default function Payments() {
  const { currentProject } = useProjectStore();
  const { t } = useTranslation();
  const [showLinkModal, setShowLinkModal] = useState(false);

  const { data: invoices = [], isLoading } = useQuery({
    queryKey: ['invoices', currentProject?.id],
    queryFn: () => api.payments.getInvoices(currentProject.id),
    enabled: !!currentProject,
  });

  if (!currentProject) {
    return (
      <div className="h-full flex items-center justify-center p-6">
        <NoProjectState
          title="No Project Selected"
          description="Please select or create a project workspace to manage customer invoices and generate checkout payment links."
        />
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-3 text-primary">
            <CreditCard className="w-6 h-6 text-status-success" />
            {t('payments.title')}
          </h1>
          <p className="text-sm text-secondary mt-1">{t('payments.subtitle')}</p>
        </div>
        <div className="flex items-center gap-2.5">
          <Button variant="secondary" size="sm" leftIcon={Receipt}>
            {t('payments.new_invoice')}
          </Button>
          <Button
            variant="primary"
            size="sm"
            leftIcon={Plus}
            onClick={() => setShowLinkModal(true)}
          >
            {t('payments.quick_link')}
          </Button>
        </div>
      </div>

      {/* Invoices Table Card */}
      <div className="bg-surface-card rounded-2xl border border-border/50 overflow-hidden shadow-surface-sm">
        <div className="overflow-x-auto custom-scrollbar">
          <table className="w-full text-left border-collapse">
            <thead className="bg-surface-subtle/50 border-b border-border/40 text-xs font-semibold text-secondary uppercase tracking-wider">
              <tr>
                <th className="p-4">{t('payments.table.invoice_num')}</th>
                <th className="p-4">{t('payments.table.customer')}</th>
                <th className="p-4">{t('payments.table.amount')}</th>
                <th className="p-4">{t('payments.table.status')}</th>
                <th className="p-4">{t('payments.table.date')}</th>
                <th className="p-4 text-right">{t('payments.table.actions')}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/30 text-sm">
              {invoices.length === 0 ? (
                <tr>
                  <td colSpan={6} className="p-12 text-center text-muted">
                    {t('payments.table.empty') || "No invoices generated yet for this workspace"}
                  </td>
                </tr>
              ) : (
                invoices.map((invoice) => (
                  <tr key={invoice.id} className="hover:bg-white/5 transition-colors">
                    <td className="p-4 font-mono text-xs text-primary font-semibold">{invoice.invoice_number}</td>
                    <td className="p-4 text-secondary">{invoice.customer_id || 'Unknown Customer'}</td>
                    <td className="p-4 font-mono font-medium text-primary">${invoice.total_amount?.toFixed(2)}</td>
                    <td className="p-4">
                      <Badge variant={invoice.status === 'paid' ? 'success' : 'warning'} size="sm" dot>
                        {invoice.status}
                      </Badge>
                    </td>
                    <td className="p-4 text-xs text-muted">
                      {new Date(invoice.issue_date || Date.now()).toLocaleDateString()}
                    </td>
                    <td className="p-4 text-right">
                      <Button variant="ghost" size="sm">
                        {t('common.view')}
                      </Button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Quick Link Modal */}
      <AnimatePresence>
        {showLinkModal && (
          <QuickLinkModal
            projectId={currentProject.id}
            onClose={() => setShowLinkModal(false)}
          />
        )}
      </AnimatePresence>
    </div>
  );
}

function QuickLinkModal({ projectId, onClose }) {
  const { t } = useTranslation();
  const [amount, setAmount] = useState('');
  const [desc, setDesc] = useState('');
  const [generatedLink, setGeneratedLink] = useState(null);
  const [copied, setCopied] = useState(false);

  const createLinkMutation = useMutation({
    mutationFn: () => api.payments.createLink(projectId, { amount: parseFloat(amount), description: desc }),
    onSuccess: (data) => {
      setGeneratedLink(data.url);
      toast.success(t('payments.modal.success') || "Payment link generated!");
    },
    onError: (err) => {
      toast.error(err.message || "Failed to create payment link");
    }
  });

  const copyLink = () => {
    if (generatedLink) {
      navigator.clipboard.writeText(generatedLink);
      setCopied(true);
      toast.success(t('payments.modal.copied') || "Link copied to clipboard!");
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="bg-surface-card border border-border/60 rounded-2xl p-6 w-full max-w-md shadow-surface-lg"
      >
        <h2 className="text-lg font-bold text-primary mb-4 flex items-center gap-2">
          <DollarSign className="w-5 h-5 text-status-success" />
          {t('payments.modal.title')}
        </h2>

        {!generatedLink ? (
          <div className="space-y-4">
            <Input
              label={t('payments.modal.amount')}
              type="number"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder="0.00"
              required
              autoFocus
            />
            <Input
              label={t('payments.modal.description')}
              type="text"
              value={desc}
              onChange={(e) => setDesc(e.target.value)}
              placeholder="Sales Order or Service Fee"
            />
            <div className="flex justify-end gap-2.5 pt-2">
              <Button variant="outline" onClick={onClose}>
                {t('common.cancel')}
              </Button>
              <Button
                variant="primary"
                onClick={() => createLinkMutation.mutate()}
                isLoading={createLinkMutation.isPending}
                disabled={!amount}
              >
                {t('payments.modal.generate')}
              </Button>
            </div>
          </div>
        ) : (
          <div className="text-center space-y-4">
            <div className="bg-surface-subtle text-brand-accent p-3.5 rounded-xl break-all font-mono text-xs border border-border/50">
              {generatedLink}
            </div>
            <div className="flex gap-2 justify-center">
              <Button variant="secondary" onClick={copyLink} leftIcon={copied ? Check : Copy}>
                {copied ? "Copied" : t('payments.modal.copy')}
              </Button>
              <a href={generatedLink} target="_blank" rel="noreferrer" className="inline-flex">
                <Button variant="primary" leftIcon={ExternalLink}>
                  {t('payments.modal.open')}
                </Button>
              </a>
            </div>
            <Button variant="ghost" size="sm" onClick={onClose} className="mt-2 text-muted">
              {t('payments.modal.close')}
            </Button>
          </div>
        )}
      </motion.div>
    </div>
  );
}
