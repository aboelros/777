/**
 * Executive platform overview dashboard page.
 */

import React, { useState } from 'react';
import { Users, Store, ShoppingBag, MessageSquare, Bot, DollarSign } from 'lucide-react';
import { useDashboardMetrics } from '../hooks/useDashboardMetrics';
import MetricCard from '../components/MetricCard';
import SystemHealthWidget from '../components/SystemHealthWidget';
import RecentActivityTable from '../components/RecentActivityTable';
import Button from '@/components/ui/Button';

export default function DashboardPage() {
  const [timeframe, setTimeframe] = useState(30);
  const { metrics, health, loading, error, refetch } = useDashboardMetrics(timeframe);

  if (loading && !metrics) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '400px' }}>
        <div className="spinner" style={{ width: '40px', height: '40px' }} />
      </div>
    );
  }

  const statCards = [
    {
      title: 'Total Platform Users',
      value: metrics?.total_users || 0,
      subtitle: `${metrics?.active_users || 0} active accounts`,
      icon: Users,
      color: '#6366F1',
      bg: 'rgba(99, 102, 241, 0.15)',
    },
    {
      title: 'Connected Stores (Fleet)',
      value: metrics?.total_projects || 0,
      subtitle: 'Multi-tenant brand accounts',
      icon: Store,
      color: '#0EA5E9',
      bg: 'rgba(14, 165, 233, 0.15)',
    },
    {
      title: 'Processed Orders',
      value: metrics?.total_orders || 0,
      subtitle: `$${(metrics?.total_gmv || 0).toLocaleString()} Gross GMV`,
      icon: ShoppingBag,
      color: '#10B981',
      bg: 'rgba(16, 185, 129, 0.15)',
    },
    {
      title: 'Customer Conversations',
      value: metrics?.total_messages || 0,
      subtitle: `${metrics?.inbound_messages || 0} In / ${metrics?.outbound_messages || 0} AI Out`,
      icon: MessageSquare,
      color: '#F59E0B',
      bg: 'rgba(245, 158, 11, 0.15)',
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Page Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--text-primary)' }}>
            Operations Mission Control
          </h1>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
            System-wide operational metrics, health, and multi-tenant performance
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <select
            value={timeframe}
            onChange={(e) => setTimeframe(Number(e.target.value))}
            style={{
              padding: '0.5rem 1rem',
              background: 'var(--bg-surface)',
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius-md)',
              color: 'var(--text-primary)',
              fontSize: '0.85rem',
              outline: 'none',
              cursor: 'pointer',
            }}
          >
            <option value={7}>Last 7 Days</option>
            <option value={30}>Last 30 Days</option>
            <option value={90}>Last 90 Days</option>
          </select>
          <Button variant="secondary" size="md" onClick={refetch}>
            Refresh
          </Button>
        </div>
      </div>

      {error && (
        <div
          style={{
            padding: '1rem',
            background: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: 'var(--radius-md)',
            color: 'var(--danger)',
            fontSize: '0.875rem',
          }}
        >
          {error}
        </div>
      )}

      {/* KPI Cards Grid */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
          gap: '1.25rem',
        }}
      >
        {statCards.map((card, idx) => (
          <MetricCard key={idx} {...card} />
        ))}
      </div>

      {/* Fleet Health Widget */}
      <SystemHealthWidget health={health} />

      {/* Real-time Activity Table */}
      <RecentActivityTable />
    </div>
  );
}
