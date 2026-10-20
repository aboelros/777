import React from 'react';
import PropTypes from 'prop-types';
import { motion } from 'framer-motion';
import { TrendingUp, PieChart as PieIcon } from 'lucide-react';
import {
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';
import GlassCard from '@/components/ui/GlassCard';

const CHART_COLORS = ['#0ea5e9', '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

/**
 * ReportCharts - Renders dynamic Area and Pie breakdown charts
 */
export default function ReportCharts({ reportData }) {
  if (!reportData) return null;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Revenue Trend Chart */}
      {reportData.revenue_by_day && (
        <motion.div initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }}>
          <GlassCard className="p-6">
            <h3 className="text-base font-semibold text-[var(--color-text-primary)] mb-4 flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-emerald-400" />
              Daily Revenue Velocity
            </h3>
            <div className="h-[280px]">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart
                  data={Object.entries(reportData.revenue_by_day).map(([date, revenue]) => ({
                    date: new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
                    revenue
                  }))}
                >
                  <defs>
                    <linearGradient id="reportRevGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                  <XAxis dataKey="date" stroke="#64748b" tick={{ fontSize: 11 }} />
                  <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'rgba(15, 23, 42, 0.9)',
                      borderColor: 'rgba(255,255,255,0.1)',
                      borderRadius: '0.75rem',
                      color: '#fff'
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="revenue"
                    stroke="#0ea5e9"
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#reportRevGradient)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </GlassCard>
        </motion.div>
      )}

      {/* Status Breakdown Pie Chart */}
      {reportData.status_breakdown && (
        <motion.div initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }}>
          <GlassCard className="p-6">
            <h3 className="text-base font-semibold text-[var(--color-text-primary)] mb-4 flex items-center gap-2">
              <PieIcon className="w-4 h-4 text-sky-400" />
              Distribution Status Breakdown
            </h3>
            <div className="h-[280px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={Object.entries(reportData.status_breakdown).map(([status, count]) => ({
                      name: status,
                      value: count
                    }))}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                    outerRadius={90}
                    dataKey="value"
                  >
                    {Object.keys(reportData.status_breakdown).map((_, idx) => (
                      <Cell key={`cell-${idx}`} fill={CHART_COLORS[idx % CHART_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'rgba(15, 23, 42, 0.9)',
                      borderColor: 'rgba(255,255,255,0.1)',
                      borderRadius: '0.75rem',
                      color: '#fff'
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </GlassCard>
        </motion.div>
      )}
    </div>
  );
}

ReportCharts.propTypes = {
  reportData: PropTypes.object
};
