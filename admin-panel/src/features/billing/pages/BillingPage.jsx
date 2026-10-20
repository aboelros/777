/**
 * Billing and SaaS tier revenue management page.
 */

import React, { useState } from 'react';
import Card from '@/components/ui/Card';
import MetricCard from '@/features/dashboard/components/MetricCard';
import { CreditCard, DollarSign, Users, Award } from 'lucide-react';
import { useSubscriptions } from '../hooks/useSubscriptions';
import SubscriptionTable from '../components/SubscriptionTable';
import TierModal from '../components/TierModal';

export default function BillingPage() {
  const { subscriptions, total, loading, error, overrideLimits } = useSubscriptions();
  const [modalState, setModalState] = useState({ isOpen: false, subscription: null });

  const totalPaidRevenue = subscriptions.reduce((acc, curr) => acc + (curr.total_paid || 0), 0);
  const paidAccountsCount = subscriptions.filter((s) => s.tier && s.tier.toLowerCase() !== 'free').length;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--text-primary)' }}>
          Billing & Subscription Controls
        </h1>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
          Monitor SaaS recurring revenue, manage plan tiers, and grant custom operational quotas
        </p>
      </div>

      {error && (
        <div style={{ padding: '1rem', background: 'rgba(239, 68, 68, 0.1)', color: 'var(--danger)', borderRadius: 'var(--radius-md)' }}>
          {error}
        </div>
      )}

      {/* Revenue Summary Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.25rem' }}>
        <MetricCard
          title="Total Paid Volume"
          value={`$${totalPaidRevenue.toLocaleString('en-US', { minimumFractionDigits: 2 })}`}
          subtitle="Direct processed subscription fees"
          icon={DollarSign}
          color="#10B981"
          bg="rgba(16, 185, 129, 0.15)"
        />
        <MetricCard
          title="Paid Merchants"
          value={paidAccountsCount}
          subtitle={`Out of ${total} total registered accounts`}
          icon={Award}
          color="#6366F1"
          bg="rgba(99, 102, 241, 0.15)"
        />
        <MetricCard
          title="Free Tier Merchants"
          value={total - paidAccountsCount}
          subtitle="On default platform quotas"
          icon={Users}
          color="#0EA5E9"
          bg="rgba(14, 165, 233, 0.15)"
        />
      </div>

      <Card title="Active Merchant Plans" subtitle="Manual override available for all registered accounts" noPadding>
        <SubscriptionTable
          subscriptions={subscriptions}
          loading={loading}
          onOverride={(s) => setModalState({ isOpen: true, subscription: s })}
        />
      </Card>

      <TierModal
        isOpen={modalState.isOpen}
        onClose={() => setModalState({ isOpen: false, subscription: null })}
        subscription={modalState.subscription}
        onSave={overrideLimits}
      />
    </div>
  );
}
