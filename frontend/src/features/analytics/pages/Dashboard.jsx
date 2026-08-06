import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import {
  TrendingUp,
  ShoppingCart,
  MessageSquare,
  DollarSign,
  Activity,
  Users,
  Bot,
  Zap,
  Package,
  Hash,
  TrendingDown,
  AlertCircle
} from 'lucide-react';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import GlassCard from '../../../components/ui/GlassCard';
import SmartSignals from '../../../components/SmartSignals';
import ApiErrorState from '../../../components/ApiErrorState';
import SkeletonLoader from '../../../components/ui/SkeletonLoader';
import api from '../../../services/api';
import { useProjectStore } from '../../../store/projectStore';
import { useTranslation } from '../../../lib/translations';

export default function Dashboard() {
  const { currentProject } = useProjectStore();
  const { t, language } = useTranslation();

  // DEMO MODE: Use fake data for advertising/showcase
  const USE_DEMO_DATA = false;

  // Fetch real data
  const { data: ordersData, isLoading: ordersLoading, error: ordersError, refetch: refetchOrders } = useQuery({
    queryKey: ['dashboard-orders', currentProject?.id],
    queryFn: async () => {
      const response = await api.orders.list(currentProject.id, { limit: 100 });
      return response;
    },
    enabled: !!currentProject?.id,
    retry: 1,
  });

  const { data: messagesData, isLoading: messagesLoading, error: messagesError, refetch: refetchMessages } = useQuery({
    queryKey: ['dashboard-messages', currentProject?.id],
    queryFn: async () => {
      // Fetch recent conversations as a proxy for messages
      const response = await api.messages.getConversations(currentProject.id, { limit: 100 });
      // The API returns an array directly, not { conversations: [] }
      return { messages: Array.isArray(response) ? response : [] };
    },
    enabled: !!currentProject?.id,
    retry: 1,
  });

  const { data: productsData, isLoading: productsLoading, error: productsError, refetch: refetchProducts } = useQuery({
    queryKey: ['dashboard-products', currentProject?.id],
    queryFn: async () => {
      const response = await api.products.list(currentProject.id);
      return response;
    },
    enabled: !!currentProject?.id,
    retry: 1,
  });

  // Fetch dashboard summary (includes social stats and comparisons)
  const { data: summaryData, isLoading: summaryLoading, error: summaryError, refetch: refetchSummary } = useQuery({
    queryKey: ['dashboard-summary', currentProject?.id],
    queryFn: async () => {
      return await api.reports.getDashboardSummary(currentProject.id);
    },
    enabled: !!currentProject?.id,
    refetchInterval: 60000, // Refresh every minute
    retry: 1,
  });

  const { data: integrationsData, isLoading: integrationsLoading, error: integrationsError, refetch: refetchIntegrations } = useQuery({
    queryKey: ['dashboard-integrations', currentProject?.id],
    queryFn: async () => {
      return await api.integrations.list(currentProject.id);
    },
    enabled: !!currentProject,
    retry: 1,
  });

  // Calculate stats from real or demo data
  let orders, messages, products, totalRevenue, totalOrders, totalMessages, unreadMessages, totalProducts, activeIntegrations;

  if (USE_DEMO_DATA) {
    // ... stats for demo mode
    totalRevenue = 147832.50;
    totalOrders = 1247;
    totalMessages = 3892;
    unreadMessages = 47;
    totalProducts = 156;
    activeIntegrations = 8;
  } else {
    // Real data
    orders = ordersData?.orders || [];
    messages = messagesData?.messages || [];
    products = productsData?.products || [];

    totalRevenue = summaryData?.today?.revenue || orders.reduce((sum, order) => sum + (parseFloat(order.total) || 0), 0);
    totalOrders = summaryData?.today?.orders || orders.length;
    totalMessages = summaryData?.today?.messages || messages.length;
    unreadMessages = messages.filter(m => !m.is_read).length;
    totalProducts = products.length;
    activeIntegrations = integrationsData?.integrations?.filter(i => i.is_active).length || 0;
  }

  // Group orders by day for chart
  const last7Days = [...Array(7)].map((_, i) => {
    const date = new Date();
    date.setDate(date.getDate() - (6 - i));
    return date.toISOString().split('T')[0];
  });

  const salesData = USE_DEMO_DATA ? [
    { date: 'Mon', revenue: 18420, orders: 163 },
    { date: 'Tue', revenue: 22350, orders: 198 },
    { date: 'Wed', revenue: 19780, orders: 174 },
    { date: 'Thu', revenue: 24560, orders: 215 },
    { date: 'Fri', revenue: 28940, orders: 248 },
    { date: 'Sat', revenue: 21820, orders: 192 },
    { date: 'Sun', revenue: 25130, orders: 221 },
  ] : last7Days.map(date => {
    const dayOrders = orders.filter(o => o.created_at?.startsWith(date));
    const dayRevenue = dayOrders.reduce((sum, o) => sum + (parseFloat(o.total) || 0), 0);
    return {
      date: new Date(date).toLocaleDateString(language === 'ar' ? 'ar-EG' : 'en-US', { weekday: 'short' }),
      revenue: Math.round(dayRevenue),
      orders: dayOrders.length,
    };
  });

  // Group messages by day
  const messageData = USE_DEMO_DATA ? [
    { date: 'Mon', messages: 487, unread: 12 },
    { date: 'Tue', messages: 563, unread: 8 },
    { date: 'Wed', messages: 521, unread: 15 },
    { date: 'Thu', messages: 612, unread: 9 },
    { date: 'Fri', messages: 689, unread: 11 },
    { date: 'Sat', messages: 548, unread: 6 },
    { date: 'Sun', messages: 602, unread: 7 },
  ] : last7Days.map(date => {
    const dayMessages = messages.filter(m => m.created_at?.startsWith(date));
    return {
      date: new Date(date).toLocaleDateString(language === 'ar' ? 'ar-EG' : 'en-US', { weekday: 'short' }),
      messages: dayMessages.length,
      unread: dayMessages.filter(m => !m.is_read).length,
    };
  });

  const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'k';
    return num;
  };

  const stats = [
    {
      label: t('dashboard.total_revenue'),
      value: USE_DEMO_DATA ? '$147,832' : `$${totalRevenue.toFixed(2)}`,
      change: '+245%',
      icon: DollarSign,
      color: 'from-accent-500 to-cyan-600',
      trend: 'up',
    },
    {
      label: t('dashboard.total_orders'),
      value: USE_DEMO_DATA ? '1,247' : totalOrders.toString(),
      change: '+189%',
      icon: ShoppingCart,
      color: 'from-gray-700 to-gray-600',
      trend: 'up',
    },
    {
      label: t('dashboard.messages'),
      value: USE_DEMO_DATA ? '3,892' : totalMessages.toString(),
      subValue: USE_DEMO_DATA ? `47 ${t('dashboard.unread')}` : `${unreadMessages} ${t('dashboard.unread')}`,
      icon: MessageSquare,
      color: 'from-zinc-800 to-zinc-900',
      trend: 'up',
      change: '+312%',
    },
    {
      label: t('dashboard.products'),
      value: USE_DEMO_DATA ? '156' : totalProducts.toString(),
      subValue: USE_DEMO_DATA ? `142 ${t('dashboard.in_stock')}` : `${products.filter(p => p.in_stock).length} ${t('dashboard.in_stock')}`,
      icon: Package,
      color: 'from-orange-500 to-red-600',
      trend: 'up',
      change: '+78%',
    },
    {
      label: t('dashboard.meta_engagement'),
      value: USE_DEMO_DATA
        ? '2.5k'
        : summaryData?.social_engagement?.facebook?.fans
          ? formatNumber(summaryData.social_engagement.facebook.fans)
          : summaryData?.social_engagement?.instagram?.followers
            ? formatNumber(summaryData.social_engagement.instagram.followers)
            : '0',
      subValue: USE_DEMO_DATA
        ? 'Facebook & Instagram'
        : summaryData?.social_engagement?.facebook
          ? `${summaryData.social_engagement.facebook.name} (FB)`
          : summaryData?.social_engagement?.instagram
            ? `${summaryData.social_engagement.instagram.username} (IG)`
            : t('dashboard.no_social'),
      icon: Hash,
      color: 'from-sky-500 to-rose-600',
      trend: 'up',
      change: '+12%',
    },
    {
      label: t('dashboard.active_integrations'),
      value: USE_DEMO_DATA ? '8' : activeIntegrations.toString(),
      subValue: USE_DEMO_DATA ? t('dashboard.operational') : `${activeIntegrations} ${t('dashboard.active_count')}`,
      icon: Zap,
      color: 'from-cyan-500 to-blue-600',
      trend: 'up',
      change: '+300%',
      pulse: true,
    },
  ];



  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-4xl font-bold text-white mb-2">{t('dashboard.title')}</h1>
          <p className="text-gray-400 font-light tracking-wide">{t('dashboard.welcome_subtitle')}</p>
        </div>
        <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/5 text-xs font-mono text-accent-primary">
          <div className="w-2 h-2 rounded-full bg-accent-primary animate-pulse" />
          LIVE SYSTEM
        </div>
      </motion.div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {summaryLoading ? (
          Array.from({ length: 6 }).map((_, i) => (
            <SkeletonLoader key={i} type="card" />
          ))
        ) : summaryError ? (
          <div className="col-span-full">
            <ApiErrorState error={summaryError} onRetry={refetchSummary} />
          </div>
        ) : (
          stats.map((stat, index) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <GlassCard className="p-6 relative group overflow-hidden h-full">
                {/* Hover Glow */}
                <div className="absolute -inset-0.5 bg-gradient-to-br from-accent-primary/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 blur-xl" />

                <div className="relative z-10">
                  <div className="flex items-start justify-between mb-4">
                    <div className={`p-3 rounded-xl bg-gradient-to-br from-white/5 to-white/0 border border-white/10 group-hover:border-accent-primary/30 transition-colors`}>
                      <stat.icon className="w-6 h-6 text-gray-300 group-hover:text-accent-primary transition-colors" />
                    </div>
                    {stat.change && (
                      <div className={`flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-medium ${stat.trend === 'up' ? 'bg-green-500/10 text-green-400 border border-green-500/20' :
                        stat.trend === 'down' ? 'bg-red-500/10 text-red-400 border border-red-500/20' :
                          'bg-gray-500/10 text-gray-400'
                        }`}>
                        {stat.trend === 'up' ? <TrendingUp className="w-3 h-3" /> :
                          stat.trend === 'down' ? <TrendingDown className="w-3 h-3" /> : null}
                        {stat.change}
                      </div>
                    )}
                  </div>

                  <p className="text-gray-500 text-xs uppercase tracking-widest font-bold mb-1">{stat.label}</p>
                  <div className="flex items-baseline gap-2">
                    <p className="text-3xl font-bold text-white font-mono">{stat.value}</p>
                  </div>
                  {stat.subValue && (
                    <p className="text-xs text-gray-500 mt-2 pl-1 border-l-2 border-accent-primary/20">
                      {stat.subValue}
                    </p>
                  )}
                </div>

                {/* Sparkline Overlay */}
                {(stat.label.includes('Revenue') || stat.label.includes('Orders') || stat.label.includes('Messages')) && (
                  <div className="absolute bottom-0 left-0 right-0 h-24 opacity-10 group-hover:opacity-20 transition-opacity pointer-events-none">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={stat.label.includes('Revenue') ? salesData : stat.label.includes('Messages') ? messageData : salesData}>
                        <defs>
                          <linearGradient id={`grad-${index}`} x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor="#0ea5e9" stopOpacity={0.5} />
                            <stop offset="100%" stopColor="#0ea5e9" stopOpacity={0} />
                          </linearGradient>
                        </defs>
                        <Area
                          type="monotone"
                          dataKey={stat.label.includes('Revenue') ? 'revenue' : stat.label.includes('Messages') ? 'messages' : 'orders'}
                          stroke="#0ea5e9"
                          strokeWidth={2}
                          fill={`url(#grad-${index})`}
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                )}
              </GlassCard>
            </motion.div>
          )))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Revenue Chart */}
        <GlassCard className="p-8">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h3 className="text-xl font-bold text-white mb-1">{t('dashboard.revenue_overview')}</h3>
              <p className="text-xs text-gray-500 uppercase tracking-widest">{t('dashboard.last_7_days')}</p>
            </div>
            <div className="p-2 rounded-lg bg-accent-primary/10">
              <Activity className="w-5 h-5 text-accent-primary" />
            </div>
          </div>
          <div className="h-[350px]">
            {ordersLoading ? (
              <SkeletonLoader type="chart" />
            ) : ordersError ? (
              <ApiErrorState error={ordersError} onRetry={refetchOrders} compact />
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={salesData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.2} />
                      <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} opacity={0.3} />
                  <XAxis
                    dataKey="date"
                    stroke="#525252"
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                    dy={10}
                  />
                  <YAxis
                    stroke="#525252"
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                    tickFormatter={(value) => `$${value}`}
                    dx={-10}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#0a0a0a',
                      border: '1px solid rgba(14, 165, 233, 0.2)',
                      borderRadius: '8px',
                      boxShadow: '0 4px 20px rgba(0,0,0,0.5)',
                      color: '#fff'
                    }}
                    itemStyle={{ color: '#0ea5e9' }}
                  />
                  <Area
                    type="monotone"
                    dataKey="revenue"
                    stroke="#0ea5e9"
                    fillOpacity={1}
                    fill="url(#colorRevenue)"
                    strokeWidth={2}
                  />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </div>
        </GlassCard>

        {/* Messages Chart */}
        <GlassCard className="p-8">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h3 className="text-xl font-bold text-white mb-1">{t('dashboard.message_activity')}</h3>
              <p className="text-xs text-gray-500 uppercase tracking-widest">{t('dashboard.last_7_days')}</p>
            </div>
            <div className="p-2 rounded-lg bg-accent-primary/10">
              <MessageSquare className="w-5 h-5 text-accent-primary" />
            </div>
          </div>
          <div className="h-[350px]">
            {messagesLoading ? (
              <SkeletonLoader type="chart" />
            ) : messagesError ? (
              <ApiErrorState error={messagesError} onRetry={refetchMessages} compact />
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={messageData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} opacity={0.3} />
                  <XAxis
                    dataKey="date"
                    stroke="#525252"
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                    dy={10}
                  />
                  <YAxis
                    stroke="#525252"
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                    dx={-10}
                  />
                  <Tooltip
                    cursor={{ fill: 'rgba(255,255,255,0.03)' }}
                    contentStyle={{
                      backgroundColor: '#0a0a0a',
                      border: '1px solid rgba(14, 165, 233, 0.2)',
                      borderRadius: '8px',
                      boxShadow: '0 4px 20px rgba(0,0,0,0.5)',
                      color: '#fff'
                    }}
                  />
                  <Bar
                    dataKey="messages"
                    fill="#0ea5e9"
                    radius={[4, 4, 0, 0]}
                    barSize={40}
                    opacity={0.8}
                    activeBar={{ opacity: 1, fill: '#38bdf8' }}
                  />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </GlassCard>

        {/* Proactive Intelligence Feed - NEW */}
        <div className="h-[340px] lg:col-span-2">
          <SmartSignals />
        </div>
      </div>

      {/* Platform Stats Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <GlassCard className="p-8">
          <h3 className="text-xl font-bold text-white mb-6">{t('dashboard.integration_status')}</h3>
          <div className="space-y-3">
            {(USE_DEMO_DATA ? [
              { id: 1, provider: 'shopify', is_active: true },
              { id: 2, provider: 'whatsapp', is_active: true },
              { id: 3, provider: 'instagram', is_active: true },
              { id: 4, provider: 'telegram', is_active: true },
              { id: 5, provider: 'facebook', is_active: true },
              { id: 6, provider: 'twitter', is_active: true },
              { id: 7, provider: 'woocommerce', is_active: false },
              { id: 8, provider: 'stripe', is_active: true },
            ] : integrationsData?.integrations?.slice(0, 5) || []).map((integration, index) => (
              <motion.div
                key={integration.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className="flex items-center justify-between p-4 rounded-xl bg-white/5 border border-white/5 hover:border-accent-primary/20 transition-all group"
              >
                <div className="flex items-center gap-4">
                  <div className={`w-2 h-2 rounded-full shadow-[0_0_10px_currentColor] ${integration.is_active ? 'bg-green-500 text-green-500' : 'bg-gray-500 text-gray-500'
                    }`} />
                  <span className="font-medium capitalize text-gray-200 group-hover:text-white transition-colors">{integration.provider}</span>
                </div>
                <span className={`text-[10px] uppercase font-bold tracking-wider px-3 py-1 rounded-full ${integration.is_active
                  ? 'bg-green-500/10 text-green-400 border border-green-500/20'
                  : 'bg-gray-500/10 text-gray-400 border border-gray-500/20'
                  }`}>
                  {integration.is_active ? t('common.active') : t('common.inactive')}
                </span>
              </motion.div>
            ))}
            {(!integrationsData?.integrations || integrationsData.integrations.length === 0) && !USE_DEMO_DATA && (
              <div className="p-8 text-center text-gray-500 border border-dashed border-gray-800 rounded-xl">
                No integrations active
              </div>
            )}
          </div>
        </GlassCard>

        <GlassCard className="p-8">
          <h3 className="text-xl font-bold text-white mb-6">{t('dashboard.product_inventory')}</h3>
          <div className="space-y-6">
            <div className="flex items-center justify-between p-4 rounded-xl bg-white/5">
              <span className="text-gray-400 font-medium">{t('dashboard.products')}</span>
              <span className="text-3xl font-bold text-white font-mono">{totalProducts}</span>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 rounded-xl bg-green-500/5 border border-green-500/10">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-green-400/80">{t('dashboard.in_stock')}</span>
                  <Package className="w-4 h-4 text-green-500" />
                </div>
                <span className="text-2xl font-bold text-green-400 font-mono">
                  {products.filter(p => p.in_stock).length}
                </span>
              </div>

              <div className="p-4 rounded-xl bg-red-500/5 border border-red-500/10">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-red-400/80">{t('dashboard.out_of_stock')}</span>
                  <AlertCircle className="w-4 h-4 text-red-500" />
                </div>
                <span className="text-2xl font-bold text-red-400 font-mono">
                  {products.filter(p => !p.in_stock).length}
                </span>
              </div>
            </div>

            <div className="relative pt-2">
              <div className="flex justify-between text-xs text-gray-500 mb-2 font-mono uppercase tracking-wide">
                <span>Inventory Health</span>
                <span>
                  {totalProducts > 0
                    ? Math.round((products.filter(p => p.in_stock).length / totalProducts) * 100)
                    : 0}%
                </span>
              </div>
              <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{
                    width: totalProducts > 0
                      ? `${(products.filter(p => p.in_stock).length / totalProducts) * 100}%`
                      : '0%'
                  }}
                  className="h-full bg-gradient-to-r from-green-500 to-emerald-600 shadow-[0_0_10px_rgba(16,185,129,0.5)]"
                />
              </div>
            </div>
          </div>
        </GlassCard>
      </div>
    </div>
  );
}
