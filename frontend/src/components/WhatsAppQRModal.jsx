import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, CheckCircle, AlertCircle, AlertTriangle, RefreshCw, Power, Smartphone } from 'lucide-react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import api from '@/services/api';
import Button from '@/components/ui/Button';

export default function WhatsAppQRModal({
  isOpen,
  onClose,
  projectId,
  integrationId,
  initialQRCode = null,
}) {
  const queryClient = useQueryClient();
  const [qrCode, setQrCode] = useState(initialQRCode);
  const [connectionStatus, setConnectionStatus] = useState(initialQRCode ? 'ready' : 'loading');
  const [errorMessage, setErrorMessage] = useState('');

  const fetchQRMutation = useMutation({
    mutationFn: async () => {
      if (!projectId || !integrationId) return null;
      return await api.integrations.waGateway.getQR(projectId, integrationId);
    },
    onSuccess: (data) => {
      const qr = data?.qr_url || data?.qr_code || data?.qr;
      const isConnected = data?.status === 'connected' || data?.connected || data?.integration_status === 'connected';

      if (isConnected) {
        setConnectionStatus('connected');
        setQrCode(null);
        queryClient.invalidateQueries(['integrations', projectId]);
        setTimeout(() => onClose(), 1800);
      } else if (data?.status === 'connecting') {
        setConnectionStatus('connecting');
        if (qr) setQrCode(qr);
      } else if (qr) {
        setQrCode(qr);
        setConnectionStatus('ready');
        setErrorMessage('');
      } else if (data?.status === 'loading' && !qrCode) {
        setConnectionStatus('loading');
      }
    },
    onError: (err) => {
      if (!qrCode) {
        const sanitized = (err.response?.data?.detail || err.message || 'Unable to load QR')
          .replace(/Bearer\s+[^\s]+/gi, '[REDACTED]')
          .replace(/https?:\/\/[^\s]+/gi, '[URL]');
        setErrorMessage(sanitized);
        setConnectionStatus('error');
      }
    },
  });

  const logoutMutation = useMutation({
    mutationFn: () => api.integrations.waGateway.logout(projectId, integrationId),
    onSuccess: () => {
      toast.success('Session logged out');
      queryClient.invalidateQueries(['integrations', projectId]);
      setQrCode(null);
      setConnectionStatus('disconnected');
    },
    onError: () => toast.error('Failed to logout session'),
  });

  useEffect(() => {
    if (!isOpen || !projectId || !integrationId) return;

    if (initialQRCode) {
      setQrCode(initialQRCode);
      setConnectionStatus('ready');
    }

    // Initial fetch
    fetchQRMutation.mutate();

    // Smooth poll every 5 seconds without triggering Cloudflare rate limits
    const interval = setInterval(() => {
      if (connectionStatus !== 'connected') {
        fetchQRMutation.mutate();
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [isOpen, projectId, integrationId, initialQRCode]);

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 bg-black/70 backdrop-blur-md flex items-center justify-center z-50 p-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.96 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.96 }}
          className="glass-card p-6 sm:p-8 max-w-md w-full rounded-2xl border border-border space-y-5"
        >
          <div className="flex items-center justify-between pb-3 border-b border-border">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center text-white shadow-md">
                <Smartphone className="w-5 h-5" />
              </div>
              <div>
                <h2 className="text-lg font-bold text-text-primary">WhatsApp Linked Device</h2>
                <div className="flex items-center gap-2 mt-0.5">
                  <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20">
                    Unofficial / Self-Hosted
                  </span>
                </div>
              </div>
            </div>
            <button onClick={onClose} className="p-2 text-text-muted hover:text-text-primary transition-colors">
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-xl text-amber-300 text-xs space-y-1">
            <div className="font-semibold flex items-center gap-1.5 text-amber-400">
              <AlertTriangle className="w-4 h-4 shrink-0" />
              Account Safety Warning
            </div>
            <p className="text-[11px] text-amber-300/80 leading-relaxed">
              Baileys is an unofficial client. WhatsApp may restrict or ban numbers using unofficial tools. Use consent-based messaging only.
            </p>
          </div>

          <div className="bg-bg-surface/50 border border-border/50 rounded-xl p-5 flex flex-col items-center justify-center min-h-[260px]">
            {connectionStatus === 'connected' ? (
              <div className="text-center space-y-2 py-6">
                <CheckCircle className="w-12 h-12 text-emerald-400 mx-auto" />
                <p className="font-bold text-text-primary">WhatsApp Connected</p>
                <p className="text-xs text-text-muted">Account is paired and ready for automated messaging.</p>
              </div>
            ) : connectionStatus === 'connecting' ? (
              <div className="text-center space-y-2 py-6">
                <RefreshCw className="w-10 h-10 text-brand-primary animate-spin mx-auto" />
                <p className="font-bold text-text-primary">Connecting to WhatsApp...</p>
                <p className="text-xs text-text-muted">Device scanned! Finalizing handshake...</p>
              </div>
            ) : connectionStatus === 'error' && !qrCode ? (
              <div className="text-center space-y-2 py-6">
                <AlertCircle className="w-12 h-12 text-rose-400 mx-auto" />
                <p className="font-bold text-rose-400">Connection Error</p>
                <p className="text-xs text-text-muted max-w-xs">{errorMessage || 'Could not load QR code'}</p>
                <Button size="sm" variant="secondary" onClick={() => fetchQRMutation.mutate()} leftIcon={RefreshCw}>
                  Retry
                </Button>
              </div>
            ) : qrCode ? (
              <div className="text-center space-y-3">
                <div className="bg-white p-3 rounded-xl shadow-md inline-block">
                  <img src={qrCode} alt="WhatsApp QR Code" className="w-52 h-52 object-contain" />
                </div>
                <p className="text-xs text-text-muted">
                  Open WhatsApp &gt; Linked Devices &gt; Link a Device to scan
                </p>
              </div>
            ) : (
              <div className="text-center space-y-3 py-8">
                <RefreshCw className="w-8 h-8 text-brand-primary animate-spin mx-auto" />
                <p className="text-xs text-text-muted">Initializing gateway session and generating QR...</p>
              </div>
            )}
          </div>

          <div className="flex items-center gap-3 pt-2">
            <Button
              type="button"
              variant="secondary"
              size="sm"
              className="flex-1"
              onClick={() => fetchQRMutation.mutate()}
              isLoading={fetchQRMutation.isPending}
              leftIcon={RefreshCw}
            >
              Refresh QR
            </Button>
            <Button
              type="button"
              variant="danger"
              size="sm"
              className="flex-1"
              onClick={() => logoutMutation.mutate()}
              isLoading={logoutMutation.isPending}
              leftIcon={Power}
            >
              Logout Session
            </Button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
