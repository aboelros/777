import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
    CreditCard, Plus, DollarSign, Receipt, Copy, ExternalLink
} from 'lucide-react';
import { toast } from 'sonner';
import api from '../services/api';
import { useProjectStore } from '../store/projectStore';
import { motion, AnimatePresence } from 'framer-motion';
import useThemeStore from '../store/themeStore';
import { useTranslation } from '../lib/translations';

export default function Payments() {
    const { currentProject } = useProjectStore();
    const { t } = useTranslation();
    const queryClient = useQueryClient();
    const [showLinkModal, setShowLinkModal] = useState(false);

    const { data: invoices = [] } = useQuery({
        queryKey: ['invoices', currentProject?.id],
        queryFn: () => api.payments.getInvoices(currentProject.id),
        enabled: !!currentProject
    });

    if (!currentProject) return null;

    return (
        <div className="h-full flex flex-col p-6 max-w-7xl mx-auto space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold flex items-center gap-3">
                        <CreditCard className="w-8 h-8 text-green-400" />
                        {t('payments.title')}
                    </h1>
                    <p className="text-gray-400">{t('payments.subtitle')}</p>
                </div>
                <div className="flex gap-3">
                    <button className="btn-secondary flex items-center gap-2">
                        <Receipt className="w-4 h-4" /> {t('payments.new_invoice')}
                    </button>
                    <button
                        onClick={() => setShowLinkModal(true)}
                        className="btn-primary flex items-center gap-2"
                    >
                        <Plus className="w-4 h-4" /> {t('payments.quick_link')}
                    </button>
                </div>
            </div>

            {/* Invoices List */}
            <div className="bg-dark-900/50 rounded-2xl border border-white/5 overflow-hidden">
                <table className="w-full text-left">
                    <thead className="bg-white/5 border-b border-white/5">
                        <tr>
                            <th className="p-4 text-sm font-medium text-gray-400">{t('payments.table.invoice_num')}</th>
                            <th className="p-4 text-sm font-medium text-gray-400">{t('payments.table.customer')}</th>
                            <th className="p-4 text-sm font-medium text-gray-400">{t('payments.table.amount')}</th>
                            <th className="p-4 text-sm font-medium text-gray-400">{t('payments.table.status')}</th>
                            <th className="p-4 text-sm font-medium text-gray-400">{t('payments.table.date')}</th>
                            <th className="p-4 text-sm font-medium text-gray-400">{t('payments.table.actions')}</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                        {invoices.length === 0 ? (
                            <tr>
                                <td colSpan={6} className="p-8 text-center text-gray-500">
                                    {t('payments.table.empty')}
                                </td>
                            </tr>
                        ) : (
                            invoices.map(invoice => (
                                <tr key={invoice.id} className="hover:bg-white/5 transition-colors">
                                    <td className="p-4 font-mono text-sm">{invoice.invoice_number}</td>
                                    <td className="p-4 text-sm">{invoice.customer_id || 'Unknown'}</td>
                                    <td className="p-4 text-sm">${invoice.total_amount?.toFixed(2)}</td>
                                    <td className="p-4">
                                        <span className={`px-2 py-0.5 text-xs rounded-full bg-white/10 ${invoice.status === 'paid' ? 'text-green-400 bg-green-500/10' : 'text-yellow-400 bg-yellow-500/10'
                                            }`}>
                                            {invoice.status}
                                        </span>
                                    </td>
                                    <td className="p-4 text-sm text-gray-400">
                                        {new Date(invoice.issue_date).toLocaleDateString()}
                                    </td>
                                    <td className="p-4">
                                        <button className="text-gray-400 hover:text-white">{t('common.view')}</button>
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
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
    const { language } = useThemeStore();
    const t = useTranslation(language);
    const [amount, setAmount] = useState('');
    const [desc, setDesc] = useState('');
    const [generatedLink, setGeneratedLink] = useState(null);

    const createLinkMutation = useMutation({
        mutationFn: () => api.payments.createLink(projectId, { amount: parseFloat(amount), description: desc }),
        onSuccess: (data) => {
            setGeneratedLink(data.url);
            toast.success(t('payments.modal.success'));
        }
    });

    const copyLink = () => {
        navigator.clipboard.writeText(generatedLink);
        toast.success(t('payments.modal.copied'));
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="bg-dark-900 border border-white/10 rounded-xl p-6 w-full max-w-md shadow-2xl"
            >
                <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                    <DollarSign className="w-5 h-5 text-green-400" />
                    {t('payments.modal.title')}
                </h2>

                {!generatedLink ? (
                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm text-gray-400 mb-1">{t('payments.modal.amount')}</label>
                            <input
                                type="number"
                                value={amount} onChange={(e) => setAmount(e.target.value)}
                                className="w-full bg-dark-950 border border-white/10 rounded-lg p-2"
                                placeholder="0.00"
                                autoFocus
                            />
                        </div>
                        <div>
                            <label className="block text-sm text-gray-400 mb-1">{t('payments.modal.description')}</label>
                            <input
                                type="text"
                                value={desc} onChange={(e) => setDesc(e.target.value)}
                                className="w-full bg-dark-950 border border-white/10 rounded-lg p-2"
                                placeholder="Consultation Fee"
                            />
                        </div>
                        <div className="flex justify-end gap-2 mt-6">
                            <button onClick={onClose} className="px-4 py-2 text-gray-400 hover:text-white">{t('common.cancel')}</button>
                            <button
                                onClick={() => createLinkMutation.mutate()}
                                disabled={!amount}
                                className="btn-primary"
                            >
                                {t('payments.modal.generate')}
                            </button>
                        </div>
                    </div>
                ) : (
                    <div className="text-center space-y-4">
                        <div className="bg-green-500/10 text-green-400 p-4 rounded-lg break-all font-mono text-sm border border-green-500/20">
                            {generatedLink}
                        </div>
                        <div className="flex gap-2 justify-center">
                            <button onClick={copyLink} className="btn-secondary flex items-center gap-2">
                                <Copy className="w-4 h-4" /> {t('payments.modal.copy')}
                            </button>
                            <a href={generatedLink} target="_blank" rel="noreferrer" className="btn-primary flex items-center gap-2">
                                <ExternalLink className="w-4 h-4" /> {t('payments.modal.open')}
                            </a>
                        </div>
                        <button onClick={onClose} className="text-sm text-gray-500 hover:text-white mt-4">
                            {t('payments.modal.close')}
                        </button>
                    </div>
                )}
            </motion.div>
        </div>
    );
}
