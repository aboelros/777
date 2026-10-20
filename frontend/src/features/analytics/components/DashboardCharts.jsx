import { AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Activity, MessageSquare } from 'lucide-react';
import GlassCard from '@/components/ui/GlassCard';
import SkeletonLoader from '@/components/ui/SkeletonLoader';
import ApiErrorState from '@/components/ApiErrorState';
import { useTranslation } from '@/lib/translations';

export default function DashboardCharts({
  salesData,
  messageData,
  ordersLoading,
  ordersError,
  refetchOrders,
  messagesLoading,
  messagesError,
  refetchMessages,
}) {
  const { t } = useTranslation();

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Revenue Trajectory */}
      <GlassCard className="p-6 rounded-2xl border border-border">
        <div className="flex items-center justify-between mb-6 pb-2 border-b border-white/10">
          <div>
            <h3 className="text-lg font-bold text-white">
              {t('dashboard.revenue_overview') || 'Revenue Trajectory'}
            </h3>
            <p className="text-xs text-slate-400">{t('dashboard.last_7_days') || 'Last 7 Days Rolling'}</p>
          </div>
          <div className="p-2.5 rounded-xl bg-sky-500/15 border border-sky-400/30 text-sky-400 shadow-[0_0_12px_rgba(56,189,248,0.25)]">
            <Activity className="w-5 h-5" />
          </div>
        </div>

        <div className="h-[280px]">
          {ordersLoading ? (
            <SkeletonLoader type="chart" />
          ) : ordersError && import.meta.env.VITE_TESTING_MODE !== 'true' ? (
            <ApiErrorState error={ordersError} onRetry={refetchOrders} compact />
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={salesData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.45} />
                    <stop offset="50%" stopColor="#0ea5e9" stopOpacity={0.15} />
                    <stop offset="95%" stopColor="#2563eb" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" vertical={false} />
                <XAxis dataKey="date" stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} dy={8} />
                <YAxis stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} tickFormatter={(v) => `$${v}`} dx={-8} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'rgba(9, 15, 32, 0.92)',
                    border: '1px solid rgba(255, 255, 255, 0.15)',
                    backdropFilter: 'blur(20px)',
                    borderRadius: '14px',
                    boxShadow: '0 8px 32px rgba(0,0,0,0.5), 0 0 15px rgba(56,189,248,0.2)',
                    color: '#fff',
                    fontSize: '12px',
                  }}
                />
                <Area type="monotone" dataKey="revenue" stroke="#0ea5e9" fill="url(#colorRevenue)" strokeWidth={2.5} />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </div>
      </GlassCard>

      {/* Message Activity */}
      <GlassCard className="p-6 rounded-2xl border border-white/10 hover:border-sky-400/40 shadow-[0_8px_32px_rgba(0,0,0,0.45)]">
        <div className="flex items-center justify-between mb-6 pb-2 border-b border-white/10">
          <div>
            <h3 className="text-lg font-bold text-white">
              {t('dashboard.message_activity') || 'Conversational Traffic'}
            </h3>
            <p className="text-xs text-slate-400">{t('dashboard.last_7_days') || 'Last 7 Days Rolling'}</p>
          </div>
          <div className="p-2.5 rounded-xl bg-sky-500/15 border border-sky-400/30 text-sky-400 shadow-[0_0_12px_rgba(56,189,248,0.25)]">
            <MessageSquare className="w-5 h-5" />
          </div>
        </div>

        <div className="h-[280px]">
          {messagesLoading ? (
            <SkeletonLoader type="chart" />
          ) : messagesError && import.meta.env.VITE_TESTING_MODE !== 'true' ? (
            <ApiErrorState error={messagesError} onRetry={refetchMessages} compact />
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={messageData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="barLiquidGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#38bdf8" />
                    <stop offset="70%" stopColor="#0ea5e9" />
                    <stop offset="100%" stopColor="#2563eb" />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" vertical={false} />
                <XAxis dataKey="date" stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} dy={8} />
                <YAxis stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} dx={-8} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'rgba(9, 15, 32, 0.92)',
                    border: '1px solid rgba(255, 255, 255, 0.15)',
                    backdropFilter: 'blur(20px)',
                    borderRadius: '14px',
                    boxShadow: '0 8px 32px rgba(0,0,0,0.5), 0 0 15px rgba(56,189,248,0.2)',
                    color: '#fff',
                    fontSize: '12px',
                  }}
                />
                <Bar dataKey="messages" fill="url(#barLiquidGradient)" radius={[8, 8, 2, 2]} barSize={28} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </GlassCard>
    </div>
  );
}
