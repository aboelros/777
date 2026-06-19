import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Bot, TrendingUp, AlertTriangle, Zap, MessageSquare, ArrowRight, Brain, Activity, Sparkles, Lock } from 'lucide-react';
import GlassCard from './GlassCard';
import { useTranslation } from '../lib/translations';

// Simulated AI Signals - Enhanced for "Predictive Intelligence" feel
const getMockSignals = (t) => [
    {
        id: 1,
        type: 'insight',
        icon: TrendingUp,
        color: 'text-emerald-400',
        borderColor: 'border-emerald-500/20',
        bgGradient: 'from-emerald-500/10 to-transparent',
        title: t('smart_signals.signals.revenue_velocity.title') || 'Revenue Velocity',
        message: t('smart_signals.signals.revenue_velocity.message') || 'Projected turnover +12% vs. baseline. High-value cohorts active.',
        time: t('common.just_now') || 'Just now'
    },
    {
        id: 2,
        type: 'warning',
        icon: Activity,
        color: 'text-accent-primary', // Gold for warnings in this theme
        borderColor: 'border-accent-primary/20',
        bgGradient: 'from-accent-primary/10 to-transparent',
        title: t('smart_signals.signals.anomaly.title') || 'Anomaly Detected',
        message: t('smart_signals.signals.anomaly.message') || 'DM volume deviation (+3σ). Support intervention recommended.',
        time: '15m ago'
    },
    {
        id: 3,
        type: 'opportunity',
        icon: Sparkles,
        color: 'text-sky-400',
        borderColor: 'border-sky-500/20',
        bgGradient: 'from-sky-500/10 to-transparent',
        title: t('smart_signals.signals.conversion.title') || 'Conversion Signal',
        message: t('smart_signals.signals.conversion.message') || '"Premium" intent detected in 8 active sessions. Auto-engage?',
        time: '1h ago'
    },
    {
        id: 4,
        type: 'security',
        icon: Lock,
        color: 'text-blue-400',
        borderColor: 'border-blue-500/20',
        bgGradient: 'from-blue-500/10 to-transparent',
        title: t('smart_signals.signals.system.title') || 'System Integrity',
        message: t('smart_signals.signals.system.message') || 'All APIs operational. 99.9% uptime maintained during peak load.',
        time: '2h ago'
    }
];

export default function SmartSignals() {
    const [signals, setSignals] = useState([]);
    const { t } = useTranslation();

    // Simulate "Streaming" analysis with a technical feel
    useEffect(() => {
        let timeouts = [];
        setSignals([]); // Reset
        const mockData = getMockSignals(t);

        mockData.forEach((signal, index) => {
            const timeout = setTimeout(() => {
                setSignals(prev => [signal, ...prev]);
            }, 800 + (index * 1200));
            timeouts.push(timeout);
        });

        return () => timeouts.forEach(clearTimeout);
    }, [t]);

    return (
        <GlassCard className="p-0 overflow-hidden h-full flex flex-col relative group border-accent-primary/10">
            {/* Ambient Intelligence Glow */}
            <div className="absolute top-0 end-0 w-64 h-64 bg-accent-primary/5 rounded-full blur-3xl opacity-20 pointer-events-none" />

            {/* Header */}
            <div className="p-5 border-b border-white/5 flex items-center justify-between bg-black/20 backdrop-blur-xl relative z-10">
                <div className="flex items-center gap-3">
                    <div className="relative p-2 rounded-lg bg-accent-primary/5 border border-accent-primary/10">
                        <Brain className="w-5 h-5 text-accent-primary" />
                        <motion.div
                            className="absolute inset-0 border border-accent-primary/30 rounded-lg"
                            animate={{ opacity: [0, 1, 0], scale: [1, 1.1, 1] }}
                            transition={{ duration: 3, repeat: Infinity }}
                        />
                    </div>
                    <div>
                        <h3 className="font-bold text-sm tracking-wide text-gray-100 ">
                            {t('smart_signals.title') || 'SMART SIGNALS'}
                        </h3>
                        <div className="flex items-center gap-1.5">
                            <span className="w-1.5 h-1.5 rounded-full bg-accent-primary animate-pulse" />
                            <p className="text-[10px] uppercase tracking-widest text-accent-primary/80 font-mono">
                                {t('smart_signals.live_analysis')}
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Signals Feed */}
            <div className="flex-1 overflow-y-auto p-5 space-y-4 custom-scrollbar relative z-10">
                {/* Scanner Line Effect */}
                <motion.div
                    className="absolute top-0 start-0 w-full h-[2px] bg-gradient-to-r from-transparent via-accent-primary/30 to-transparent z-0 pointer-events-none"
                    animate={{ top: ['0%', '100%', '0%'] }}
                    transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
                />

                <AnimatePresence mode='popLayout'>
                    {signals.length === 0 && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="flex flex-col items-center justify-center h-48 text-gray-500 space-y-4"
                        >
                            <div className="relative w-12 h-12">
                                <div className="absolute inset-0 rounded-full border-2 border-accent-primary/20" />
                                <div className="absolute inset-0 rounded-full border-t-2 border-accent-primary animate-spin" />
                            </div>
                            <p className="text-xs font-mono uppercase tracking-widest animate-pulse text-accent-primary/50">
                                {t('smart_signals.scanning')}
                            </p>
                        </motion.div>
                    )}

                    {signals.map((signal) => (
                        <motion.div
                            key={signal.id}
                            initial={{ opacity: 0, x: -20, filter: 'blur(10px)' }}
                            animate={{ opacity: 1, x: 0, filter: 'blur(0px)' }}
                            exit={{ opacity: 0, scale: 0.95 }}
                            transition={{ type: "spring", stiffness: 300, damping: 25 }}
                            className="group relative"
                        >
                            <div className={`
                                relative p-4 rounded-xl border border-white/5 bg-black/40 
                                hover:bg-white/[0.02] transition-all duration-500
                                hover:border-accent-primary/20 overflow-hidden
                            `}>
                                {/* Hover Gradient Background */}
                                <div className={`absolute inset-0 bg-gradient-to-r ${signal.bgGradient} opacity-0 group-hover:opacity-100 transition-opacity duration-500`} />

                                <div className="relative z-10 flex gap-4">
                                    {/* Icon Box */}
                                    <div className={`
                                        w-10 h-10 rounded-lg flex items-center justify-center shrink-0
                                        bg-white/5 border border-white/5 group-hover:scale-110 transition-transform duration-500
                                    `}>
                                        <signal.icon className={`w-5 h-5 ${signal.color}`} />
                                    </div>

                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center justify-between mb-1">
                                            <h4 className={`text-sm font-bold text-gray-200 group-hover:text-white transition-colors`}>
                                                {signal.title}
                                            </h4>
                                            <span className="text-[10px] font-mono text-gray-500 group-hover:text-accent-primary/70 transition-colors">
                                                {signal.time}
                                            </span>
                                        </div>
                                        <p className="text-xs text-gray-400 leading-relaxed font-light">
                                            {signal.message}
                                        </p>
                                    </div>
                                </div>

                                {/* Action Arrow */}
                                <div className="absolute bottom-2 end-2 opacity-0 group-hover:opacity-100 transition-all duration-300 ltr:translate-x-2 ltr:group-hover:translate-x-0 rtl:-translate-x-2 rtl:group-hover:translate-x-0">
                                    <ArrowRight className="w-3.5 h-3.5 text-accent-primary rtl:rotate-180" />
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </AnimatePresence>
            </div>
        </GlassCard>
    );
}
