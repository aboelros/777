import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, AlertTriangle, Users, ShoppingBag, Target, Zap, Brain, ArrowUpRight, Activity } from 'lucide-react';
import GlassCard from '../components/GlassCard';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, ArcElement, Filler } from 'chart.js';
import { useTranslation } from '../lib/translations';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, ArcElement, Filler);

export default function PredictiveAnalytics() {
    const { t } = useTranslation();
    const [forecast, setForecast] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Simulate loading
        setTimeout(() => setLoading(false), 1500);
    }, []);

    // ... (keep chart data logic but update colors to Gold/Void theme)
    const forecastChartData = {
        labels: Array.from({ length: 30 }, (_, i) => `Day ${i + 1}`),
        datasets: [
            {
                label: t('predictive.metrics.projection'),
                data: Array.from({ length: 30 }, () => Math.random() * 5000 + 8000), // Higher baseline
                borderColor: '#D4AF37', // Gold
                backgroundColor: (context) => {
                    const ctx = context.chart.ctx;
                    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
                    gradient.addColorStop(0, 'rgba(212, 175, 55, 0.4)');
                    gradient.addColorStop(1, 'rgba(212, 175, 55, 0)');
                    return gradient;
                },
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#000',
                pointBorderColor: '#D4AF37',
                pointBorderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6
            },
            {
                label: 'Baseline',
                data: Array.from({ length: 30 }, () => Math.random() * 2000 + 6000),
                borderColor: '#333',
                borderDash: [5, 5],
                tension: 0.4,
                pointRadius: 0
            }
        ]
    };

    return (
        <div className="p-8 space-y-8 relative overflow-hidden min-h-screen">
            {/* Global Ambient Glow */}
            <div className="absolute top-0 end-0 w-[500px] h-[500px] bg-accent-primary/5 rounded-full blur-[120px] pointer-events-none" />

            {/* Header */}
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-center justify-between relative z-10"
            >
                <div>
                    <h1 className="text-4xl font-bold mb-2 flex items-center gap-3 text-white">
                        <div className="p-2 rounded-xl bg-gradient-to-br from-accent-primary to-accent-dark shadow-lg shadow-accent-primary/20">
                            <Brain className="w-8 h-8 text-black" />
                        </div>
                        {/* Gradient Text */}
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-white via-white to-gray-400">
                            {t('predictive.title')}
                        </span>
                    </h1>
                    <p className="text-gray-400 font-light tracking-wide ps-16 max-w-xl">
                        {t('predictive.subtitle')}
                    </p>
                </div>

                <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-black/40 border border-accent-primary/20 backdrop-blur-md">
                    <div className="w-2 h-2 rounded-full bg-accent-primary animate-pulse" />
                    <span className="text-xs font-mono text-accent-primary tracking-widest uppercase">
                        {t('predictive.confidence')}: 98.4%
                    </span>
                </div>
            </motion.div>

            {/* Key Metrics Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 relative z-10">
                {[
                    { label: t('predictive.metrics.projection'), value: '$127,450', change: '+12.4%', icon: TrendingUp, color: 'text-emerald-400' },
                    { label: t('predictive.metrics.churn_risk'), value: '23', change: '-2 vs last week', icon: AlertTriangle, color: 'text-accent-primary' },
                    { label: t('predictive.metrics.conversion'), value: '34.2%', change: '+1.8%', icon: Zap, color: 'text-blue-400' }
                ].map((stat, i) => (
                    <motion.div
                        key={i}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.1 }}
                    >
                        <GlassCard className="p-6 relative overflow-hidden group border-white/5 hover:border-accent-primary/20 transition-all duration-500">
                            <div className="absolute top-0 end-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                                <stat.icon className="w-16 h-16 text-white" />
                            </div>

                            <div className="relative z-10">
                                <div className="flex items-center gap-2 mb-4">
                                    <div className={`p-2 rounded-lg bg-white/5 border border-white/10 ${stat.color}`}>
                                        <stat.icon className="w-5 h-5" />
                                    </div>
                                    <span className="text-sm text-gray-400 font-medium tracking-wide uppercase">{stat.label}</span>
                                </div>
                                <div className="text-4xl font-bold text-white mb-2 tracking-tight">{stat.value}</div>
                                <div className={`text-xs font-mono font-bold px-2 py-1 rounded inline-block ${stat.change.startsWith('+') ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'}`}>
                                    {stat.change} <span className="text-gray-500 font-light">{t('predictive.metrics.vs_baseline')}</span>
                                </div>
                            </div>
                        </GlassCard>
                    </motion.div>
                ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 relative z-10">
                {/* Main Forecast Chart */}
                <div className="lg:col-span-2">
                    <GlassCard className="p-8 h-full border-white/5 bg-black/40">
                        <div className="flex items-center justify-between mb-8">
                            <h2 className="text-xl font-bold text-white flex items-center gap-3 ">
                                <Activity className="w-5 h-5 text-accent-primary" />
                                {t('predictive.charts.revenue')}
                            </h2>
                            <div className="flex gap-2">
                                {['7D', '30D', '90D'].map(range => (
                                    <button key={range} className={`px-3 py-1 text-xs font-bold rounded-lg transition-all ${range === '30D' ? 'bg-accent-primary text-black' : 'bg-white/5 text-gray-500 hover:text-white'}`}>
                                        {range}
                                    </button>
                                ))}
                            </div>
                        </div>
                        <div className="h-[400px]">
                            <Line
                                data={forecastChartData}
                                options={{
                                    responsive: true,
                                    maintainAspectRatio: false,
                                    plugins: { legend: { display: false } },
                                    scales: {
                                        y: {
                                            grid: { color: 'rgba(255, 255, 255, 0.03)' },
                                            ticks: { color: '#666', font: { family: 'monospace' } },
                                            border: { display: false }
                                        },
                                        x: {
                                            grid: { display: false },
                                            ticks: { color: '#666', font: { family: 'monospace' } },
                                            border: { display: false }
                                        }
                                    },
                                    interaction: {
                                        mode: 'nearest',
                                        axis: 'x',
                                        intersect: false
                                    }
                                }}
                            />
                        </div>
                    </GlassCard>
                </div>

                {/* Risk & Opportunity Column */}
                <div className="space-y-6">
                    {/* Churn Risk */}
                    <GlassCard className="p-6 border-white/5">
                        <h2 className="text-lg font-bold text-white mb-6 flex items-center gap-2 ">
                            <AlertTriangle className="w-4 h-4 text-accent-primary" />
                            {t('predictive.risks.title')}
                        </h2>
                        <div className="space-y-4">
                            {[
                                { name: 'TechCorp Intl', risk: 85, loss: '$12k/yr' },
                                { name: 'Global Logistics', risk: 72, loss: '$8.5k/yr' },
                                { name: 'Alpha Stream', risk: 68, loss: '$24k/yr' }
                            ].map((client, i) => (
                                <div key={i} className="group p-4 rounded-xl bg-white/[0.02] border border-white/5 hover:bg-white/[0.05] transition-colors relative overflow-hidden">
                                    <div className="absolute left-0 top-0 bottom-0 w-[2px] bg-gradient-to-b from-red-500 to-transparent" />
                                    <div className="flex justify-between items-start mb-2">
                                        <div>
                                            <div className="font-bold text-gray-200">{client.name}</div>
                                            <div className="text-xs text-gray-500 font-mono">{t('predictive.metrics.potential_loss')}: {client.loss}</div>
                                        </div>
                                        <div className="text-right">
                                            <div className="text-lg font-bold text-accent-primary">{client.risk}%</div>
                                            <div className="text-[10px] text-red-400 uppercase tracking-widest">{t('predictive.metrics.risk_score')}</div>
                                        </div>
                                    </div>
                                    <div className="w-full h-1 bg-white/10 rounded-full overflow-hidden mt-2">
                                        <div
                                            className="h-full bg-gradient-to-r from-accent-primary to-orange-500"
                                            style={{ width: `${client.risk}%` }}
                                        />
                                    </div>
                                </div>
                            ))}
                        </div>
                        <button className="w-full mt-4 py-3 rounded-xl border border-white/10 text-xs font-bold uppercase tracking-widest text-gray-400 hover:text-white hover:bg-white/5 transition-all">
                            {t('predictive.risks.view_all')}
                        </button>
                    </GlassCard>

                    {/* AI Recommendations */}
                    <GlassCard className="p-6 border-white/5 bg-gradient-to-br from-sky-900/10 to-transparent">
                        <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2 ">
                            <Zap className="w-4 h-4 text-sky-400" />
                            {t('predictive.recommendations.title')}
                        </h2>
                        <div className="p-4 rounded-xl bg-sky-500/5 border border-sky-500/20 mb-4">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-xs font-bold text-sky-400 uppercase tracking-widest">{t('predictive.recommendations.top_opportunity')}</span>
                                <ArrowUpRight className="w-4 h-4 text-sky-400" />
                            </div>
                            <p className="text-sm text-gray-300 leading-relaxed">
                                Upsell <span className="text-white font-bold">"Enterprise Plan"</span> to
                                <span className="text-white font-bold"> TechCorp Intl</span> to reduce churn risk by 45%.
                            </p>
                        </div>
                        <button className="w-full py-3 rounded-xl bg-sky-600 hover:bg-sky-500 text-white shadow-lg shadow-sky-900/20 text-xs font-bold uppercase tracking-widest transition-all">
                            {t('predictive.recommendations.execute')}
                        </button>
                    </GlassCard>
                </div>
            </div>
        </div>
    );
}
