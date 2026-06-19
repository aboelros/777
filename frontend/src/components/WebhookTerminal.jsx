import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Terminal, RefreshCw, X, Circle, Pause, Play, Download } from 'lucide-react';
import GlassCard from './GlassCard';
import api from '../services/api';
import { useProjectStore } from '../store/projectStore';
import { cn } from '../lib/utils'; // Standardized import
import { useTranslation } from '../lib/translations';

export default function WebhookTerminal({ onClose }) {
    const { currentProject } = useProjectStore();
    const [logs, setLogs] = useState([]);
    const [isPaused, setIsPaused] = useState(false);
    const [isConnected, setIsConnected] = useState(true);
    const logsEndRef = useRef(null);
    const { t } = useTranslation();

    // Poll for logs
    useEffect(() => {
        if (!currentProject || isPaused) return;

        const fetchLogs = async () => {
            try {
                const data = await api.integrationsgetLogs(currentProject.id, 50);
                setLogs(data);
                setIsConnected(true);
            } catch (error) {
                console.error('Failed to fetch logs:', error);
                setIsConnected(false);
            }
        };

        fetchLogs(); // Initial
        const interval = setInterval(fetchLogs, 3000); // Poll every 3s
        return () => clearInterval(interval);
    }, [currentProject, isPaused]);

    // Auto-scroll
    useEffect(() => {
        if (!isPaused && logsEndRef.current) {
            logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [logs, isPaused]);

    const getStatusColor = (status) => {
        if (status >= 200 && status < 300) return 'text-green-400';
        if (status >= 400 && status < 500) return 'text-cyan-400';
        if (status >= 500) return 'text-red-400';
        return 'text-gray-400';
    };

    const formatPayload = (payload) => {
        try {
            return JSON.stringify(payload, null, 2);
        } catch {
            return String(payload);
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
        >
            <GlassCard className="w-full max-w-4xl h-[80vh] flex flex-col p-0 overflow-hidden bg-dark-950/90 border-white/10 shadow-2xl">
                {/* Header */}
                <div className="flex items-center justify-between p-4 border-b border-white/5 bg-white/5">
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-black/40 border border-white/10">
                            <Terminal className="w-5 h-5 text-accent-400" />
                        </div>
                        <div>
                            <h3 className="font-mono text-sm font-semibold text-gray-200 flex items-center gap-2">
                                {t('api.integrationswebhook_url')}
                                <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
                            </h3>
                            <p className="text-[10px] text-gray-500 font-mono">
                                Streaming from api.webhook_gateway
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center gap-2">
                        <button
                            onClick={() => setIsPaused(!isPaused)}
                            className={cn(
                                "p-2 rounded-lg transition-colors flex items-center gap-2 text-xs font-mono border",
                                isPaused
                                    ? "bg-cyan-500/10 text-cyan-400 border-cyan-500/20 hover:bg-cyan-500/20"
                                    : "bg-green-500/10 text-green-400 border-green-500/20 hover:bg-green-500/20"
                            )}
                        >
                            {isPaused ? <Play className="w-3 h-3" /> : <Pause className="w-3 h-3" />}
                            {isPaused ? t('common.active') : t('common.active')}
                        </button>
                        <button
                            onClick={onClose}
                            className="p-2 rounded-lg hover:bg-white/10 text-gray-400 hover:text-white transition-colors"
                        >
                            <X className="w-5 h-5" />
                        </button>
                    </div>
                </div>

                {/* Console Output */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4 font-mono text-xs custom-scrollbar bg-black/60 scroll-smooth">
                    {logs.length === 0 ? (
                        <div className="flex flex-col items-center justify-center h-full text-zinc-700 space-y-3">
                            <div className="w-10 h-10 rounded-full border border-zinc-800 flex items-center justify-center animate-pulse">
                                <RefreshCw className="w-5 h-5 animate-spin" />
                            </div>
                            <p className="text-[10px] tracking-widest uppercase font-bold">{t('reports.controls.generating')}</p>
                        </div>
                    ) : (
                        logs.map((log) => (
                            <div key={log.id} className="group border-l border-zinc-800 pl-4 py-1 hover:border-accent-500/50 transition-colors">
                                <div className="flex items-center gap-3 mb-1.5">
                                    <span className="text-zinc-600 shrink-0 text-[10px]">
                                        [{new Date(log.timestamp).toLocaleTimeString()}]
                                    </span>
                                    <span className={cn(
                                        "font-bold px-1.5 py-0.5 rounded text-[10px]",
                                        log.method === 'POST' ? 'bg-blue-500/10 text-blue-400' : 'bg-sky-500/10 text-sky-400'
                                    )}>
                                        {log.method}
                                    </span>
                                    <span className="text-zinc-400 shrink-0 tracking-tight">{log.endpoint}</span>
                                    <div className="flex-1 border-b border-white/[0.03] mx-2 h-px" />
                                    <span className={`font-mono text-[10px] font-bold ${getStatusColor(log.status)}`}>
                                        HTTP_{log.status}
                                    </span>
                                </div>

                                {/* Payload Preview */}
                                <div className="bg-white/[0.02] border border-white/5 rounded-lg p-3 group-hover:bg-accent-500/[0.02] transition-colors overflow-x-auto">
                                    <pre className="text-zinc-500 group-hover:text-zinc-300 transition-colors whitespace-pre-wrap break-all leading-relaxed">
                                        {formatPayload(log.payload)}
                                    </pre>
                                </div>
                            </div>
                        ))
                    )}
                    <div ref={logsEndRef} />
                </div>

                {/* Footer */}
                <div className="px-4 py-2 bg-black/40 border-t border-white/5 flex items-center justify-between text-[10px] font-mono">
                    <div className="flex items-center gap-4">
                        <span className="text-zinc-600 uppercase">Input: listener_active</span>
                        <span className="text-zinc-600 uppercase">Buffer: 50_events</span>
                    </div>
                    <div className="flex items-center gap-2 text-zinc-500">
                        <span className="animate-pulse">●</span>
                        LIVE_ENCRYPTION_ACTIVE
                    </div>
                </div>
            </GlassCard>
        </motion.div>
    );
}
