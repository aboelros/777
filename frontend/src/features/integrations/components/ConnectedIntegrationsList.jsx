import React from 'react';
import { motion } from 'framer-motion';
import { 
  Trash2, 
  RefreshCw, 
  CheckCircle, 
  AlertCircle, 
  Clock, 
  Plug,
  ExternalLink 
} from 'lucide-react';
import GlassCard from '../../../components/ui/GlassCard';
import Button from '../../../components/ui/Button';

export default function ConnectedIntegrationsList({
  integrations = [],
  onDelete,
  onSync,
  isDeleting = false,
  isSyncing = false,
  onManage
}) {
  const list = Array.isArray(integrations) ? integrations : (integrations?.data || []);

  const getStatusBadge = (status) => {
    switch (status) {
      case 'connected':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
            <CheckCircle className="w-3.5 h-3.5" />
            Connected
          </span>
        );
      case 'pending':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-500/15 text-amber-400 border border-amber-500/30">
            <Clock className="w-3.5 h-3.5" />
            Pending Verification
          </span>
        );
      case 'error':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-rose-500/15 text-rose-400 border border-rose-500/30">
            <AlertCircle className="w-3.5 h-3.5" />
            Error
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-slate-500/15 text-slate-400 border border-slate-500/30">
            Disconnected
          </span>
        );
    }
  };

  return (
    <div className="mt-10 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-sky-500 to-indigo-600 flex items-center justify-center text-white shadow-lg shadow-sky-500/20">
            <Plug className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              Active Integrations
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-sky-500/20 text-sky-400 border border-sky-500/30">
                {list.length}
              </span>
            </h2>
            <p className="text-xs text-slate-400">Manage and disconnect your active platform connections</p>
          </div>
        </div>

        {onManage && (
          <Button
            onClick={onManage}
            variant="ghost"
            size="sm"
            className="text-slate-400 hover:text-white"
            rightIcon={ExternalLink}
          >
            Advanced Management
          </Button>
        )}
      </div>

      {list.length === 0 ? (
        <GlassCard className="p-8 text-center border-dashed border-white/10">
          <p className="text-sm text-slate-400">No active integrations connected to this project yet.</p>
          <p className="text-xs text-slate-500 mt-1">Select a platform above to connect your store or messaging channel.</p>
        </GlassCard>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {list.map((item) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="h-full"
            >
              <GlassCard className="p-5 flex flex-col justify-between h-full bg-slate-900/60 border border-white/10 hover:border-sky-500/30 transition-all duration-300">
                <div>
                  <div className="flex items-start justify-between gap-2 mb-3">
                    <div>
                      <h3 className="font-semibold text-white capitalize text-base">
                        {item.name || item.provider}
                      </h3>
                      <span className="text-xs text-slate-400 uppercase tracking-wider font-mono">
                        {item.provider}
                      </span>
                    </div>
                    {getStatusBadge(item.status)}
                  </div>

                  <div className="text-xs text-slate-400 space-y-1 mb-4">
                    <p className="truncate">
                      <span className="text-slate-500">ID:</span> <span className="font-mono text-slate-300">{item.id}</span>
                    </p>
                    {item.updated_at && (
                      <p className="text-slate-500">
                        Updated: {new Date(item.updated_at).toLocaleDateString()}
                      </p>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-2 pt-3 border-t border-white/5">
                  {item.status === 'connected' && onSync && (
                    <Button
                      onClick={() => onSync(item.id)}
                      disabled={isSyncing}
                      variant="secondary"
                      size="sm"
                      className="flex-1"
                      leftIcon={RefreshCw}
                    >
                      Sync
                    </Button>
                  )}

                  <Button
                    onClick={() => onDelete(item.id)}
                    disabled={isDeleting}
                    variant="danger"
                    size="sm"
                    className="flex-1 font-medium"
                    leftIcon={Trash2}
                    isLoading={isDeleting}
                  >
                    Disconnect
                  </Button>
                </div>
              </GlassCard>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
