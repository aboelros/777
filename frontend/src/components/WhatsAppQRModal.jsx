import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, CheckCircle, AlertCircle, Smartphone } from 'lucide-react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import api from '../services/api';
import { useTranslation } from '../lib/translations';

export default function WhatsAppQRModal({ isOpen, onClose, projectId, integrationId, initialQRCode }) {
    const queryClient = useQueryClient();
    const [connectionStatus, setConnectionStatus] = useState('ready'); // ready, connecting, connected, error
    const { t } = useTranslation();

    // Connect mutation - WhatsApp Business API doesn't need QR codes
    const connectMutation = useMutation({
        mutationFn: () => api.integrations.verifyIntegration(projectId, integrationId),
        onSuccess: (data) => {
            if (data.status === 'success' || data.integration_status === 'connected') {
                setConnectionStatus('connected');
                toast.success(t('integrations.connect_success'));
                setTimeout(() => {
                    queryClient.invalidateQueries(['integrations']);
                    onClose();
                }, 2000);
            } else {
                setConnectionStatus('error');
                toast.error(data.message || t('common.error'));
            }
        },
        onError: (error) => {
            setConnectionStatus('error');
            toast.error(error.message || t('common.error'));
        },
    });

    // Disconnect mutation
    const disconnectMutation = useMutation({
        mutationFn: () => api.integrations.disconnectIntegration(projectId, integrationId),
        onSuccess: () => {
            toast.success(t('common.save'));
            queryClient.invalidateQueries(['integrations']);
            onClose();
        },
        onError: (error) => {
            toast.error(error.message || t('common.error'));
        },
    });

    const handleConnect = () => {
        setConnectionStatus('connecting');
        connectMutation.mutate();
    };

    if (!isOpen) return null;

    return (
        <AnimatePresence>
            <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    className="glass-card p-8 max-w-md w-full rounded-2xl relative"
                >
                    {/* Close button */}
                    <button
                        onClick={onClose}
                        className="absolute top-4 right-4 text-slate-400 hover:text-white transition-colors"
                    >
                        <X className="w-6 h-6" />
                    </button>

                    {/* Header */}
                    <div className="text-center mb-6">
                        <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-emerald-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                            <Smartphone className="w-8 h-8 text-white" />
                        </div>
                        <h2 className="text-2xl font-bold text-white mb-2">WhatsApp Business API</h2>
                        <p className="text-slate-400 text-sm">
                            {t('integrations.connect_with_meta').replace('Meta', 'WhatsApp Business')}
                        </p>
                    </div>

                    {/* Content */}
                    <div className="space-y-6">
                        {/* Ready State */}
                        {connectionStatus === 'ready' && (
                            <div className="space-y-4">
                                {initialQRCode ? (
                                    /* Show WA-Gateway Session in iframe */
                                    <div className="space-y-3">
                                        <p className="text-slate-700 text-sm font-medium text-center bg-white px-4 py-2 rounded-t-lg">Scan QR Code with WhatsApp</p>
                                        <div className="bg-white rounded-lg overflow-hidden" style={{ height: '500px' }}>
                                            <iframe
                                                src={initialQRCode}
                                                className="w-full h-full border-0"
                                                title="WA-Gateway QR Code"
                                                sandbox="allow-same-origin allow-scripts"
                                            />
                                        </div>
                                        <div className="bg-white p-3 rounded-b-lg space-y-2">
                                            <p className="text-slate-600 text-xs text-center">
                                                📱 Open WhatsApp → Settings → Linked Devices → Link a Device
                                            </p>
                                            <a
                                                href={initialQRCode}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="block w-full text-center px-3 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg transition-colors text-xs"
                                            >
                                                Open in New Tab
                                            </a>
                                        </div>
                                    </div>
                                ) : (
                                    /* Show Business API Info */
                                    <div className="bg-white/5 border border-white/10 rounded-lg p-4 space-y-2">
                                        <p className="text-white font-medium text-sm mb-2">About WhatsApp Business API:</p>
                                        <ul className="text-slate-300 text-sm space-y-1 list-disc list-inside">
                                            <li>Official Meta WhatsApp API</li>
                                            <li>No QR codes needed</li>
                                            <li>Production-ready and reliable</li>
                                            <li>Configured via backend credentials</li>
                                        </ul>
                                    </div>
                                )}
                                {!initialQRCode && (
                                    <button
                                        onClick={handleConnect}
                                        className="w-full btn-primary"
                                    >
                                        {t('integrations.connect_with_meta').replace('Meta', 'WhatsApp')}
                                    </button>
                                )}
                            </div>
                        )}

                        {/* Connecting State */}
                        {connectionStatus === 'connecting' && (
                            <div className="flex flex-col items-center justify-center py-8">
                                <div className="animate-spin w-12 h-12 border-4 border-green-500 border-t-transparent rounded-full mb-4" />
                                <p className="text-slate-400 text-center">
                                    {t('reports.controls.generating')}
                                </p>
                            </div>
                        )}

                        {/* Error State */}
                        {connectionStatus === 'error' && (
                            <div className="flex flex-col items-center justify-center py-8">
                                <AlertCircle className="w-16 h-16 text-red-400 mb-4" />
                                <p className="text-red-400 mb-2">{t('common.error')}</p>
                                <p className="text-slate-400 text-sm text-center mb-4">
                                    {t('settings.subtitle')}
                                </p>
                                <button
                                    onClick={handleConnect}
                                    className="px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg transition-colors"
                                >
                                    {t('common.active')}
                                </button>
                            </div>
                        )}

                        {/* Connected State */}
                        {connectionStatus === 'connected' && (
                            <div className="flex flex-col items-center justify-center py-8">
                                <CheckCircle className="w-16 h-16 text-green-400 mb-4" />
                                <p className="text-green-400 text-lg font-medium mb-2">{t('common.active')}</p>
                                <p className="text-slate-400 text-sm">{t('integrations.connect_success')}</p>
                            </div>
                        )}
                    </div>

                    {/* Footer */}
                    {connectionStatus === 'connected' && (
                        <div className="mt-6 flex gap-3">
                            <button
                                onClick={() => disconnectMutation.mutate()}
                                disabled={disconnectMutation.isPending}
                                className="flex-1 px-4 py-2 bg-red-500/10 border border-red-500/30 text-red-400 rounded-lg hover:bg-red-500/20 transition-colors disabled:opacity-50"
                            >
                                {t('common.cancel')}
                            </button>
                            <button
                                onClick={onClose}
                                className="flex-1 px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg transition-colors"
                            >
                                {t('common.save')}
                            </button>
                        </div>
                    )}
                </motion.div>
            </div>
        </AnimatePresence>
    );
}
