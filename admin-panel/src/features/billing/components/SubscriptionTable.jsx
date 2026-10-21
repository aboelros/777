/**
 * Subscription table displaying merchant tiers, limits, and manual override actions.
 * Fully responsive with mobile horizontal touch scrolling.
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
        return 'outline';
    }
  };

  return (
    <div className="table-responsive-container">
      <table style={{ width: '100%', minWidth: '680px', borderCollapse: 'collapse', textAlign: 'left' }}>
        <thead>
          <tr style={{ borderBottom: '1px solid var(--border)', background: 'rgba(255, 255, 255, 0.02)' }}>
            <th style={{ padding: '0.85rem 1.25rem', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Merchant</th>
            <th style={{ padding: '0.85rem 1.25rem', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Current Plan</th>
            <th style={{ padding: '0.85rem 1.25rem', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Status</th>
            <th style={{ padding: '0.85rem 1.25rem', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Monthly Limits</th>
            <th style={{ padding: '0.85rem 1.25rem', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Revenue</th>
            <th style={{ padding: '0.85rem 1.25rem', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', textAlign: 'right' }}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {subscriptions.map((s) => (
            <tr key={s.id} style={{ borderBottom: '1px solid var(--border)' }}>
              <td style={{ padding: '0.9rem 1.25rem' }}>
                <div style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: '0.875rem' }}>
                  {s.user_name || 'Merchant'}
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  {s.user_email}
                </div>
              </td>
              <td style={{ padding: '0.9rem 1.25rem' }}>
                <Badge variant={getTierVariant(s.plan_type)}>
                  {(s.plan_type || 'FREE').toUpperCase()}
                </Badge>
              </td>
              <td style={{ padding: '0.9rem 1.25rem' }}>
                <Badge variant={s.is_active ? 'success' : 'danger'}>
                  {s.is_active ? 'Active' : 'Cancelled'}
                </Badge>
              </td>
              <td style={{ padding: '0.9rem 1.25rem', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                {s.order_limit ? `${s.order_limit.toLocaleString()} orders` : 'Unlimited'}
              </td>
              <td style={{ padding: '0.9rem 1.25rem', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                ${s.price_monthly || 0}/mo
              </td>
              <td style={{ padding: '0.9rem 1.25rem', textAlign: 'right' }}>
                <Button variant="secondary" size="sm" onClick={() => onOverride?.(s)}>
                  <Sliders size={14} style={{ marginRight: '0.35rem' }} />
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
