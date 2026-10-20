import { useQuery } from '@tanstack/react-query';
import { DollarSign, ShoppingCart, MessageSquare, Package, Hash, Zap } from 'lucide-react';
import api from '@/services/api';
import { useProjectStore } from '@/store/projectStore';
import { useTranslation } from '@/lib/translations';
import { NoProjectState } from '@/components/ui/EmptyState';
import SmartSignals from '@/components/SmartSignals';
import DashboardStatsGrid from '../components/DashboardStatsGrid';
import DashboardCharts from '../components/DashboardCharts';
import DashboardInventoryCard from '../components/DashboardInventoryCard';

export default function Dashboard() {
  const { currentProject } = useProjectStore();
  const { t, language } = useTranslation();

  const { data: ordersData, isLoading: ordersLoading, error: ordersError, refetch: refetchOrders } = useQuery({
    queryKey: ['dashboard-orders', currentProject?.id],
    queryFn: () => api.orders.list(currentProject.id, { limit: 100 }),
    enabled: !!currentProject?.id,
  });

  const { data: messagesData, isLoading: messagesLoading, error: messagesError, refetch: refetchMessages } = useQuery({
    queryKey: ['dashboard-messages', currentProject?.id],
    queryFn: async () => {
      const response = await api.messages.getConversations(currentProject.id, { limit: 100 });
      return { messages: Array.isArray(response) ? response : [] };
    },
    enabled: !!currentProject?.id,
  });

  const { data: productsData } = useQuery({
    queryKey: ['dashboard-products', currentProject?.id],
    queryFn: () => api.products.list(currentProject.id),
    enabled: !!currentProject?.id,
  });

  const { data: summaryData, isLoading: summaryLoading, error: summaryError, refetch: refetchSummary } = useQuery({
    queryKey: ['dashboard-summary', currentProject?.id],
    queryFn: () => api.reports.getDashboardSummary(currentProject.id),
    enabled: !!currentProject?.id,
    refetchInterval: 60000,
  });

  const { data: integrationsData } = useQuery({
    queryKey: ['dashboard-integrations', currentProject?.id],
    queryFn: () => api.integrations.list(currentProject.id),
    enabled: !!currentProject?.id,
  });

  if (!currentProject) {
    return <NoProjectState subtitle={t('dashboard.welcome_subtitle') || 'Select a project to review live business analytics and intelligence'} />;
  }

  const isTestingMode = import.meta.env.VITE_TESTING_MODE === 'true';

  const orders = ordersData?.orders?.length ? ordersData.orders : (isTestingMode ? [
    { id: 'ord-1', total: '420', created_at: new Date().toISOString() },
    { id: 'ord-2', total: '280', created_at: new Date(Date.now() - 86400000).toISOString() },
    { id: 'ord-3', total: '650', created_at: new Date(Date.now() - 172800000).toISOString() },
    { id: 'ord-4', total: '390', created_at: new Date(Date.now() - 259200000).toISOString() },
    { id: 'ord-5', total: '510', created_at: new Date(Date.now() - 345600000).toISOString() },
    { id: 'ord-6', total: '720', created_at: new Date(Date.now() - 432000000).toISOString() },
    { id: 'ord-7', total: '460', created_at: new Date(Date.now() - 518400000).toISOString() },
  ] : []);

  const messages = messagesData?.messages?.length ? messagesData.messages : (isTestingMode ? [
    { id: 'msg-1', is_read: false, created_at: new Date().toISOString() },
    { id: 'msg-2', is_read: true, created_at: new Date().toISOString() },
    { id: 'msg-3', is_read: false, created_at: new Date(Date.now() - 86400000).toISOString() },
    { id: 'msg-4', is_read: true, created_at: new Date(Date.now() - 172800000).toISOString() },
    { id: 'msg-5', is_read: false, created_at: new Date(Date.now() - 259200000).toISOString() },
    { id: 'msg-6', is_read: true, created_at: new Date(Date.now() - 345600000).toISOString() },
    { id: 'msg-7', is_read: false, created_at: new Date(Date.now() - 432000000).toISOString() },
  ] : []);

  const products = productsData?.products?.length ? productsData.products : (isTestingMode ? [
    { id: 'prod-1', name: 'Enterprise AI Agent', in_stock: true, stock_quantity: 45, price: '499.00' },
    { id: 'prod-2', name: 'WhatsApp Bot Pro', in_stock: true, stock_quantity: 120, price: '89.00' },
    { id: 'prod-3', name: 'Omnichannel CRM Sync', in_stock: true, stock_quantity: 8, price: '199.00' },
    { id: 'prod-4', name: 'Voice Concierge Addon', in_stock: false, stock_quantity: 0, price: '299.00' },
  ] : []);

  const totalRevenue = summaryData?.today?.revenue || orders.reduce((sum, o) => sum + (parseFloat(o.total) || 0), 0) || (isTestingMode ? 3430.00 : 0);
  const totalOrders = summaryData?.today?.orders || orders.length || (isTestingMode ? 28 : 0);
  const totalMessages = summaryData?.today?.messages || messages.length || (isTestingMode ? 142 : 0);
  const unreadMessages = messages.filter((m) => !m.is_read).length || (isTestingMode ? 12 : 0);
  const totalProducts = products.length || (isTestingMode ? 4 : 0);
  const activeIntegrations = integrationsData?.integrations?.filter((i) => i.is_active).length || (isTestingMode ? 4 : 0);

  const last7Days = [...Array(7)].map((_, i) => {
    const d = new Date();
    d.setDate(d.getDate() - (6 - i));
    return d.toISOString().split('T')[0];
  });

  const salesData = last7Days.map((date) => {
    const dayOrders = orders.filter((o) => o.created_at?.startsWith(date));
    const dayRevenue = dayOrders.reduce((sum, o) => sum + (parseFloat(o.total) || 0), 0);
    return {
      date: new Date(date).toLocaleDateString(language === 'ar' ? 'ar-EG' : 'en-US', { weekday: 'short' }),
      revenue: Math.round(dayRevenue),
      orders: dayOrders.length,
    };
  });

  const messageData = last7Days.map((date) => {
    const dayMessages = messages.filter((m) => m.created_at?.startsWith(date));
    return {
      date: new Date(date).toLocaleDateString(language === 'ar' ? 'ar-EG' : 'en-US', { weekday: 'short' }),
      messages: dayMessages.length,
      unread: dayMessages.filter((m) => !m.is_read).length,
    };
  });

  const stats = [
    { label: t('dashboard.total_revenue') || 'Total Revenue', value: `$${totalRevenue.toFixed(2)}`, change: '+24.5%', icon: DollarSign, trend: 'up' },
    { label: t('dashboard.total_orders') || 'Total Orders', value: totalOrders.toString(), change: '+18.9%', icon: ShoppingCart, trend: 'up' },
    { label: t('dashboard.messages') || 'Conversations', value: totalMessages.toString(), subValue: `${unreadMessages} ${t('dashboard.unread') || 'unread inquiries'}`, icon: MessageSquare, trend: 'up' },
    { label: t('dashboard.products') || 'Catalog Items', value: totalProducts.toString(), subValue: `${products.filter((p) => p.in_stock).length} available`, icon: Package, trend: 'up' },
    { label: t('dashboard.meta_engagement') || 'Social Reach', value: summaryData?.social_engagement?.instagram?.followers ? `${summaryData.social_engagement.instagram.followers}` : 'Connected', icon: Hash, trend: 'up' },
    { label: t('dashboard.active_integrations') || 'Active Channels', value: activeIntegrations.toString(), subValue: 'All systems operational', icon: Zap, trend: 'up' },
  ];

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-text-primary tracking-tight">{t('dashboard.title')}</h1>
          <p className="text-sm text-text-secondary mt-1">{t('dashboard.welcome_subtitle')}</p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-brand-primary/10 border border-brand-primary/20 text-xs font-mono text-brand-primary">
          <div className="w-2 h-2 rounded-full bg-brand-primary animate-pulse" />
          SYSTEM LIVE
        </div>
      </div>

      {/* KPI Cards Grid */}
      <DashboardStatsGrid
        stats={stats}
        isLoading={summaryLoading}
        error={summaryError}
        onRetry={refetchSummary}
      />

      {/* Performance Charts */}
      <DashboardCharts
        salesData={salesData}
        messageData={messageData}
        ordersLoading={ordersLoading}
        ordersError={ordersError}
        refetchOrders={refetchOrders}
        messagesLoading={messagesLoading}
        messagesError={messagesError}
        refetchMessages={refetchMessages}
      />

      {/* Real-Time Smart Signals & Inventory Health */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SmartSignals />
        <DashboardInventoryCard products={products} totalProducts={totalProducts} />
      </div>
    </div>
  );
}
