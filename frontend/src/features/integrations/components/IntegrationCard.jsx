import { motion } from 'framer-motion';
import { Settings as SettingsIcon, RefreshCw, CheckCircle, Trash2, BookOpen } from 'lucide-react';
import GlassCard from '@/components/ui/GlassCard';
import Button from '@/components/ui/Button';
import Badge from '@/components/ui/Badge';
import { useTranslation } from '@/lib/translations';

export default function IntegrationCard({
  integration,
  status,
  isConnecting,
  isSyncing,
  isVerifying,
  isDeleting,
  hasIntegration,
  existingIntegrationId,
  onConnect,
  onSync,
  onVerify,
  onDelete,
  onOpenInstructions,
}) {
  const { t } = useTranslation();
  const isConnected = status === 'connected';
  const isPending = status === 'pending';
  const isError = status === 'error';

  const badgeVariant = isConnected ? 'success' : isPending ? 'warning' : isError ? 'danger' : 'default';

  return (
    <GlassCard className="p-6 rounded-2xl border border-border hover:border-brand-primary/30 transition-all flex flex-col justify-between">
      <div>
        <div className="flex items-start justify-between mb-4">
          <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${integration.color} flex items-center justify-center text-white shadow-sm`}>
            <integration.icon className="w-6 h-6" />
          </div>
          <Badge variant={badgeVariant} withDot>
            {status}
          </Badge>
        </div>

        <h3 className="text-lg font-bold text-text-primary mb-1">{integration.name}</h3>
        <p className="text-xs text-text-secondary mb-6 line-clamp-2">{integration.description}</p>
      </div>

      <div className="space-y-2">
        <div className="flex gap-2">
          {isConnected ? (
            <>
              <Button
                onClick={() => onSync(integration.id)}
                disabled={isSyncing}
                variant="secondary"
                size="sm"
                className="flex-1"
                isLoading={isSyncing}
                leftIcon={RefreshCw}
              >
                Sync
              </Button>
              <Button
                onClick={() => onDelete(existingIntegrationId || integration.id)}
                disabled={isDeleting}
                variant="danger"
                size="sm"
                className="px-3"
                title="Disconnect"
              >
                <Trash2 className="w-4 h-4" />
              </Button>
            </>
          ) : isPending ? (
            <>
              <Button
                onClick={() => onVerify(integration.id)}
                disabled={isVerifying}
                variant="primary"
                size="sm"
                className="flex-1"
                isLoading={isVerifying}
                leftIcon={CheckCircle}
              >
                Verify
              </Button>
              <Button
                onClick={() => onConnect(integration.id)}
                variant="secondary"
                size="sm"
                className="px-3"
              >
                <SettingsIcon className="w-4 h-4" />
              </Button>
            </>
          ) : (
            <Button
              onClick={() => onConnect(integration.id)}
              disabled={isConnecting}
              variant="primary"
              size="sm"
              className="w-full"
              isLoading={isConnecting}
            >
              {isError ? 'Reconnect' : 'Connect Channel'}
            </Button>
          )}
        </div>

        <button
          type="button"
          onClick={() => onOpenInstructions(integration)}
          className="w-full py-2 px-3 rounded-xl bg-surface-subtle border border-border text-xs font-semibold text-text-secondary hover:text-text-primary hover:bg-surface-hover transition-colors flex items-center justify-center gap-1.5"
        >
          <BookOpen className="w-3.5 h-3.5 text-brand-primary" />
          Setup Guide
        </button>
      </div>
    </GlassCard>
  );
}
