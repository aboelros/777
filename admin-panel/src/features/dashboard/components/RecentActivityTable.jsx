/**
 * Recent platform activity table displaying live events and transactions.
 */

import React from 'react';
import Card from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';

export default function RecentActivityTable({ activities = [] }) {
  const sampleActivities = [
    { type: 'USER_REGISTER', detail: 'New merchant account registered', user: 'store@boutique.com', time: '5m ago' },
    { type: 'ORDER_SYNC', detail: 'Shopify order #1084 ingested ($148.00)', user: 'Fashion Hub', time: '12m ago' },
    { type: 'AI_REPLY', detail: 'WhatsApp conversation completed autonomously', user: 'Gourmet Express', time: '18m ago' },
    { type: 'TIER_UPGRADE', detail: 'Subscription upgraded to Professional tier', user: 'PharmaDirect', time: '34m ago' },
    { type: 'WEBHOOK_DELIVERY', detail: 'Meta Instagram webhook dispatched (200 OK)', user: 'Electronics Lab', time: '45m ago' },
  ];

  const displayList = activities.length > 0 ? activities : sampleActivities;

  return (
    <Card title="Live Platform Activity" subtitle="Real-time operational events across all tenants" noPadding>
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border)', background: 'rgba(255, 255, 255, 0.02)' }}>
              <th style={{ padding: '0.85rem 1.5rem', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Event</th>
              <th style={{ padding: '0.85rem 1.5rem', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Details</th>
              <th style={{ padding: '0.85rem 1.5rem', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Source</th>
              <th style={{ padding: '0.85rem 1.5rem', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Time</th>
            </tr>
          </thead>
          <tbody>
            {displayList.map((item, idx) => (
              <tr key={idx} style={{ borderBottom: '1px solid var(--border)' }}>
                <td style={{ padding: '1rem 1.5rem' }}>
                  <Badge variant="primary">{item.type || item.action}</Badge>
                </td>
                <td style={{ padding: '1rem 1.5rem', fontSize: '0.875rem', color: 'var(--text-primary)' }}>
                  {item.detail || item.details}
                </td>
                <td style={{ padding: '1rem 1.5rem', fontSize: '0.825rem', color: 'var(--text-secondary)' }}>
                  {item.user || item.performed_by}
                </td>
                <td style={{ padding: '1rem 1.5rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  {item.time || item.timestamp?.slice(11, 19)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}
