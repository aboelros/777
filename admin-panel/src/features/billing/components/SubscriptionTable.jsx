/**
 * Subscription table displaying merchant tiers, limits, and manual override actions.
 */

import React from 'react';
import Badge from '@/components/ui/Badge';
import Button from '@/components/ui/Button';
import { Sliders } from 'lucide-react';

export default function SubscriptionTable({ subscriptions = [], loading = false, onOverride }) {
  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: '3rem' }}>
        <div className="spinner" style={{ width: '32px', height: '32px' }} />
      </div>
    );
  }

  if (subscriptions.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
        No subscription records found.
      </div>
    );
  }

  const getTierVariant = (tier) => {
    switch (tier?.toLowerCase()) {
      case 'enterprise':
      case 'scale':
        return 'primary';
      case 'growth':
      case 'professional':
        return 'success';
      case 'starter':
        return 'warning';
      default:
        return 'neutral';
    }
  };

  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
        <thead>
          <tr style={{ borderBottom: '1px solid var(--border)', background: 'rgba(255, 255, 255, 0.02)' }}>
            <th style={{ padding: '0.85rem 1.5rem', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Merchant</th>
            <th style={{ padding: '0.85rem 1.5rem', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Current Plan</th>
            <th style={{ padding: '0.85rem 1.5rem', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Status</th>
            <th style={{ padding: '0.85rem 1.5rem', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Monthly Limits</th>
            <th style={{ padding: '0.85rem 1.5rem', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Revenue</th>
            <th style={{ padding: '0.85rem 1.5rem', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', textAlign: 'right' }}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {subscriptions.map((s) => (
            <tr key={s.id} style={{ borderBottom: '1px solid var(--border)' }}>
              <td style={{ padding: '1rem 1.5rem' }}>
                <div style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: '0.875rem' }}>
                  {s.user_name || 'Merchant'}
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{s.user_email}</div>
              </td>
              <td style={{ padding: '1rem 1.5rem' }}>
                <Badge variant={getTierVariant(s.tier)}>{s.tier || 'Free'}</Badge>
              </td>
              <td style={{ padding: '1rem 1.5rem' }}>
                <Badge variant={s.status === 'active' ? 'success' : 'danger'}>{s.status || 'Active'}</Badge>
              </td>
              <td style={{ padding: '1rem 1.5rem' }}>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                  💬 {s.limit_messages?.toLocaleString() || 100} msgs • 🛒 {s.limit_orders || 10} orders
                </div>
              </td>
              <td style={{ padding: '1rem 1.5rem', fontSize: '0.85rem', fontWeight: 600, color: '#10B981' }}>
                ${(s.total_paid || 0).toFixed(2)}
              </td>
              <td style={{ padding: '1rem 1.5rem', textAlign: 'right' }}>
                <Button variant="secondary" size="sm" icon={Sliders} onClick={() => onOverride(s)}>
                  Override
                </Button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
