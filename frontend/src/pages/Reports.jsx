import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import {
  BarChart3,
  TrendingUp,
  DollarSign,
  Users,
  MessageSquare,
  Package,
  Sparkles,
  Download,
  Calendar,
  Brain,
  Target,
  Activity,
  PieChart,
  LineChart,
  AlertTriangle,
  ArrowUp,
  ArrowDown
} from 'lucide-react';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  LineChart as RechartsLineChart,
  Line,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';
import GlassCard from '../components/GlassCard';
import Button from '../components/Button';
import api from '../services/api';
import { useProjectStore } from '../store/projectStore';
import { formatCurrency, formatNumber, formatDateTime } from '../utils/helpers';
import useThemeStore from '../store/themeStore';
import { useTranslation } from '../lib/translations';
import ApiErrorState from '../components/ApiErrorState';
import SkeletonLoader from '../components/SkeletonLoader';

const REPORT_TYPES = [
  {
    id: 'sales',
    icon: DollarSign,
    color: 'from-green-500 to-emerald-500'
  },
  {
    id: 'orders',
    icon: Package,
    color: 'from-blue-500 to-cyan-500'
  },
  {
    id: 'customers',
    icon: Users,
    color: 'from-purple-500 to-pink-500'
  },
  {
    id: 'performance',
    icon: Activity,
    color: 'from-orange-500 to-red-500'
  },
  {
    id: 'roi',
    icon: Target,
    color: 'from-indigo-500 to-purple-500'
  }
];

const CHART_COLORS = ['#8b5cf6', '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#ec4899'];

export default function Reports() {
  const { currentProject } = useProjectStore();
  const { t } = useTranslation();
  const queryClient = useQueryClient();

  const [selectedReportType, setSelectedReportType] = useState('sales');
  const [dateRange, setDateRange] = useState('last_30_days');
  const [generatingReport, setGeneratingReport] = useState(false);

  // Fetch existing reports
  const { data: reportsList, isLoading: reportsLoading } = useQuery({
    queryKey: ['reports', currentProject?.id],
    queryFn: () => api.reports.list(currentProject?.id),
    enabled: !!currentProject?.id,
  });

  const { data: dashboardSummary, isLoading: summaryLoading, error: summaryError, refetch: refetchSummary } = useQuery({
    queryKey: ['dashboard-summary', currentProject?.id],
    queryFn: () => api.reports.getDashboardSummary(currentProject?.id),
    enabled: !!currentProject?.id,
    refetchInterval: 60000 // Refresh every minute
  });

  // Generate new report mutation
  const generateReportMutation = useMutation({
    mutationFn: (data) => api.reports.generate(currentProject?.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['reports']);
      setGeneratingReport(false);
    },
  });

  const handleGenerateReport = () => {
    if (!currentProject?.id) {
      console.error('No project selected');
      return;
    }

    setGeneratingReport(true);

    const now = new Date();
    let startDate = new Date();

    switch (dateRange) {
      case 'last_7_days':
        startDate.setDate(now.getDate() - 7);
        break;
      case 'last_30_days':
        startDate.setDate(now.getDate() - 30);
        break;
      case 'last_month':
        startDate = new Date(now.getFullYear(), now.getMonth() - 1, 1);
        break;
      default:
        startDate.setDate(now.getDate() - 30);
    }

    generateReportMutation.mutate({
      report_type: selectedReportType,
      start_date: startDate.toISOString(),
      end_date: now.toISOString()
    });
  };

  const latestReport = reportsList?.find(r => r.report_type === selectedReportType);
  const reportData = latestReport?.payload;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-4 sm:p-6 lg:p-8">
      <div className="max-w-[1800px] mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-pink-400 to-red-400 mb-2 flex items-center gap-3">
            <BarChart3 className="w-10 h-10 text-purple-400" />
            {t('reports.title')}
          </h1>
          <p className="text-slate-400">{t('reports.subtitle')}</p>
        </motion.div>

        {/* Sales Overview & Escalations */}
        {summaryLoading ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <SkeletonLoader type="card" className="h-[200px]" />
            <SkeletonLoader type="card" className="h-[200px]" />
            <SkeletonLoader type="card" className="lg:col-span-2 h-[150px]" />
          </div>
        ) : summaryError ? (
          <div className="mb-8">
            <ApiErrorState error={summaryError} onRetry={refetchSummary} />
          </div>
        ) : dashboardSummary && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8"
          >
            {/* Today's Support Risks */}
            <GlassCard className="p-6 border-l-4 border-l-red-500 bg-red-500/5">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-red-500/20 rounded-lg">
                    <AlertTriangle className="w-6 h-6 text-red-500" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-white">{t('reports.cards.escalations')}</h3>
                    <p className="text-xs text-red-300">{t('reports.cards.escalations_desc')}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-3xl font-bold text-white">{dashboardSummary.today?.escalations || 0}</p>
                  <p className="text-xs text-slate-400">
                    {t('reports.cards.vs_yesterday').replace('yesterday', (dashboardSummary.yesterday?.escalations || 0) + ' ' + t('common.yesterday'))}
                  </p>
                </div>
              </div>
              <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                <div
                  className="h-full bg-red-500 rounded-full transition-all duration-500"
                  style={{ width: `${Math.min(100, ((dashboardSummary.today?.escalations || 0) / 10) * 100)}%` }}
                />
              </div>
            </GlassCard>

            {/* Today's Sales */}
            <GlassCard className="p-6 border-l-4 border-l-green-500 bg-green-500/5">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-green-500/20 rounded-lg">
                    <DollarSign className="w-6 h-6 text-green-500" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-white">{t('reports.cards.sales')}</h3>
                    <p className="text-xs text-green-300">{t('reports.cards.sales_desc')}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-3xl font-bold text-white">{formatCurrency(dashboardSummary.today?.revenue || 0)}</p>
                  <p className="text-xs text-slate-400">
                    {dashboardSummary.yesterday?.revenue
                      ? `${((dashboardSummary.today?.revenue - dashboardSummary.yesterday?.revenue) / dashboardSummary.yesterday?.revenue * 100).toFixed(1)}%`
                      : '+100%'} {t('reports.cards.vs_yesterday')}
                  </p>
                </div>
              </div>
              <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                <div
                  className="h-full bg-green-500 rounded-full transition-all duration-500"
                  style={{ width: '60%' }}
                />
              </div>
            </GlassCard>

            {/* Weekly Summary */}
            <GlassCard className="p-6 lg:col-span-2">
              <h3 className="font-semibold text-white mb-4">{t('reports.cards.performance')}</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 bg-white/5 rounded-xl">
                  <p className="text-slate-400 text-xs mb-1">{t('reports.cards.week_revenue')}</p>
                  <p className="text-xl font-bold text-white">{formatCurrency(dashboardSummary.this_week?.revenue || 0)}</p>
                </div>
                <div className="p-4 bg-white/5 rounded-xl">
                  <p className="text-slate-400 text-xs mb-1">{t('reports.cards.last_week_revenue')}</p>
                  <p className="text-xl font-bold text-slate-300">{formatCurrency(dashboardSummary.last_week?.revenue || 0)}</p>
                </div>
                <div className="p-4 bg-white/5 rounded-xl">
                  <p className="text-slate-400 text-xs mb-1">{t('reports.cards.month_revenue')}</p>
                  <p className="text-xl font-bold text-purple-400">{formatCurrency(dashboardSummary.this_month?.revenue || 0)}</p>
                </div>
                <div className="p-4 bg-white/5 rounded-xl">
                  <p className="text-slate-400 text-xs mb-1">{t('reports.cards.month_escalations')}</p>
                  <p className="text-xl font-bold text-red-400">{dashboardSummary.this_month?.escalations || 0}</p>
                </div>
              </div>
            </GlassCard>

          </motion.div>
        )}

        {/* Report Type Selection */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
          {REPORT_TYPES.map((type, index) => (
            <motion.div
              key={type.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setSelectedReportType(type.id)}
              className="cursor-pointer"
            >
              <GlassCard className={`relative overflow-hidden transition-all ${selectedReportType === type.id
                ? 'ring-2 ring-purple-500 shadow-lg shadow-purple-500/50'
                : 'hover:ring-1 hover:ring-white/20'
                }`}>
                <div className={`absolute inset-0 bg-gradient-to-br ${type.color} opacity-${selectedReportType === type.id ? '20' : '10'} transition-opacity`} />
                <div className="relative p-4">
                  <type.icon className={`w-8 h-8 mb-3 ${selectedReportType === type.id ? 'text-purple-400' : 'text-slate-400'}`} />
                  <h3 className="font-semibold text-white mb-1">{t(`reports.types.${type.id}`)}</h3>
                  <p className="text-xs text-slate-400">{t(`reports.types.${type.id}_desc`)}</p>
                </div>
              </GlassCard>
            </motion.div>
          ))}
        </div>

        {/* Report Controls */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="mb-8"
        >
          <GlassCard className="p-4">
            <div className="flex flex-col lg:flex-row items-center justify-between gap-4">
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <Calendar className="w-5 h-5 text-slate-400" />
                  <select
                    value={dateRange}
                    onChange={(e) => setDateRange(e.target.value)}
                    className="px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500/50 transition-all"
                  >
                    <option value="last_7_days">{t('reports.controls.ranges.last_7')}</option>
                    <option value="last_30_days">{t('reports.controls.ranges.last_30')}</option>
                    <option value="last_month">{t('reports.controls.ranges.last_month')}</option>
                  </select>
                </div>
              </div>

              <Button
                onClick={handleGenerateReport}
                disabled={generatingReport || !currentProject}
                variant="gradient"
                isLoading={generatingReport}
                loadingText={t('reports.controls.generating')}
                leftIcon={Sparkles}
              >
                {t('reports.controls.generate')}
              </Button>
            </div>
          </GlassCard>
        </motion.div>

        {/* Report Content */}
        {reportData ? (
          <div className="space-y-8">
            {/* Summary Cards */}
            {reportData.summary && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {Object.entries(reportData.summary).map(([key, value], index) => (
                  <motion.div
                    key={key}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.6 + index * 0.1 }}
                  >
                    <GlassCard className="p-6 hover:scale-105 transition-transform">
                      <p className="text-slate-400 text-sm mb-2 capitalize">
                        {t(`reports.summary.${key}`) || key.replace(/_/g, ' ')}
                      </p>
                      <p className="text-3xl font-bold text-white">
                        {typeof value === 'number'
                          ? key.toLowerCase().includes('rate') || key.toLowerCase().includes('percentage')
                            ? `${value.toFixed(1)}%`
                            : key.toLowerCase().includes('revenue') || key.toLowerCase().includes('cost') || key.toLowerCase().includes('savings')
                              ? formatCurrency(value)
                              : formatNumber(value)
                          : value}
                      </p>
                    </GlassCard>
                  </motion.div>
                ))}
              </div>
            )}

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Revenue Chart */}
              {reportData.revenue_by_day && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.8 }}
                >
                  <GlassCard className="p-6">
                    <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                      <TrendingUp className="w-5 h-5 text-green-400" />
                      {t('reports.charts.revenue')}
                    </h3>
                    <ResponsiveContainer width="100%" height={300}>
                      <AreaChart data={Object.entries(reportData.revenue_by_day).map(([date, revenue]) => ({
                        date: new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
                        revenue
                      }))}>
                        <defs>
                          <linearGradient id="revenueGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8} />
                            <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
                        <XAxis dataKey="date" stroke="#94a3b8" />
                        <YAxis stroke="#94a3b8" />
                        <Tooltip
                          contentStyle={{
                            backgroundColor: 'rgba(15, 23, 42, 0.9)',
                            border: '1px solid rgba(255,255,255,0.1)',
                            borderRadius: '0.5rem',
                            color: '#fff'
                          }}
                        />
                        <Area
                          type="monotone"
                          dataKey="revenue"
                          stroke="#8b5cf6"
                          fillOpacity={1}
                          fill="url(#revenueGradient)"
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </GlassCard>
                </motion.div>
              )}

              {/* Status Breakdown */}
              {reportData.status_breakdown && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.9 }}
                >
                  <GlassCard className="p-6">
                    <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                      <PieChart className="w-5 h-5 text-blue-400" />
                      {t('reports.charts.status')}
                    </h3>
                    <ResponsiveContainer width="100%" height={300}>
                      <RechartsPieChart>
                        <Pie
                          data={Object.entries(reportData.status_breakdown).map(([status, count]) => ({
                            name: status,
                            value: count
                          }))}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                          outerRadius={100}
                          fill="#8884d8"
                          dataKey="value"
                        >
                          {Object.keys(reportData.status_breakdown).map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip
                          contentStyle={{
                            backgroundColor: 'rgba(15, 23, 42, 0.9)',
                            border: '1px solid rgba(255,255,255,0.1)',
                            borderRadius: '0.5rem',
                            color: '#fff'
                          }}
                        />
                      </RechartsPieChart>
                    </ResponsiveContainer>
                  </GlassCard>
                </motion.div>
              )}

              {/* Channel Usage */}
              {reportData.channel_usage && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 1.0 }}
                >
                  <GlassCard className="p-6">
                    <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                      <MessageSquare className="w-5 h-5 text-purple-400" />
                      {t('reports.charts.channel')}
                    </h3>
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={Object.entries(reportData.channel_usage).map(([channel, count]) => ({
                        channel: channel.charAt(0).toUpperCase() + channel.slice(1),
                        messages: count
                      }))}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
                        <XAxis dataKey="channel" stroke="#94a3b8" />
                        <YAxis stroke="#94a3b8" />
                        <Tooltip
                          contentStyle={{
                            backgroundColor: 'rgba(15, 23, 42, 0.9)',
                            border: '1px solid rgba(255,255,255,0.1)',
                            borderRadius: '0.5rem',
                            color: '#fff'
                          }}
                        />
                        <Bar dataKey="messages" fill="#8b5cf6" radius={[8, 8, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </GlassCard>
                </motion.div>
              )}

              {/* AI Performance */}
              {reportData.ai_performance && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 1.1 }}
                >
                  <GlassCard className="p-6">
                    <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                      <Brain className="w-5 h-5 text-pink-400" />
                      {t('reports.charts.ai')}
                    </h3>
                    <div className="space-y-4">
                      {Object.entries(reportData.ai_performance).map(([key, value]) => (
                        <div key={key} className="flex items-center justify-between">
                          <span className="text-slate-400 capitalize">{key.replace(/_/g, ' ')}</span>
                          <span className="text-white font-semibold">
                            {typeof value === 'number'
                              ? key.toLowerCase().includes('rate')
                                ? `${value.toFixed(1)}%`
                                : formatNumber(value)
                              : value}
                          </span>
                        </div>
                      ))}
                    </div>
                  </GlassCard>
                </motion.div>
              )}
            </div>

            {/* AI Insights */}
            {reportData.ai_insights && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1.2 }}
              >
                <GlassCard className="p-6">
                  <h3 className="text-2xl font-semibold text-white mb-6 flex items-center gap-3">
                    <Sparkles className="w-6 h-6 text-yellow-400" />
                    {t('reports.insights.title')}
                  </h3>

                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {reportData.ai_insights.trends && (
                      <div className="space-y-3">
                        <h4 className="font-semibold text-purple-400 flex items-center gap-2">
                          <TrendingUp className="w-5 h-5" />
                          {t('reports.insights.trends')}
                        </h4>
                        <ul className="space-y-2">
                          {(Array.isArray(reportData.ai_insights.trends)
                            ? reportData.ai_insights.trends
                            : [reportData.ai_insights.trends]
                          ).map((trend, index) => (
                            <li key={index} className="text-slate-300 pl-4 border-l-2 border-purple-500/50">
                              {trend}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {reportData.ai_insights.recommendations && (
                      <div className="space-y-3">
                        <h4 className="font-semibold text-blue-400 flex items-center gap-2">
                          <Target className="w-5 h-5" />
                          {t('reports.insights.recommendations')}
                        </h4>
                        <ul className="space-y-2">
                          {(Array.isArray(reportData.ai_insights.recommendations)
                            ? reportData.ai_insights.recommendations
                            : [reportData.ai_insights.recommendations]
                          ).map((rec, index) => (
                            <li key={index} className="text-slate-300 pl-4 border-l-2 border-blue-500/50">
                              {rec}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>

                  {reportData.ai_insights.summary && (
                    <div className="mt-6 p-4 bg-white/5 rounded-lg border border-white/10">
                      <p className="text-slate-300 leading-relaxed">{reportData.ai_insights.summary}</p>
                    </div>
                  )}
                </GlassCard>
              </motion.div>
            )}
          </div>
        ) : (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
          >
            <GlassCard className="p-12">
              <div className="text-center">
                <BarChart3 className="w-20 h-20 text-slate-400 mx-auto mb-4 opacity-20" />
                <h3 className="text-2xl font-semibold text-white mb-2">{t('reports.empty.title')}</h3>
                <p className="text-slate-400 mb-6">
                  {t('reports.empty.desc')}
                </p>
                <Button
                  onClick={handleGenerateReport}
                  disabled={generatingReport}
                  variant="gradient"
                  size="lg"
                  className="mx-auto"
                  leftIcon={Sparkles}
                  isLoading={generatingReport}
                >
                  {t('reports.empty.button')}
                </Button>
              </div>
            </GlassCard>
          </motion.div>
        )}
      </div>
    </div>
  );
}
