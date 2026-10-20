/**
 * Metric card displaying KPI numerical counter, icon, and contextual trend.
 */

import React from 'react';
import Card from '@/components/ui/Card';

export default function MetricCard({ title, value, icon: Icon, color, bg, subtitle }) {
  return (
    <Card noPadding style={{ padding: '1.5rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <p style={{ fontSize: '0.85rem', fontWeight: 500, color: 'var(--text-muted)', marginBottom: '0.35rem' }}>
            {title}
          </p>
          <h3 style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--text-primary)' }}>
            {typeof value === 'number' ? value.toLocaleString() : value}
          </h3>
          {subtitle && (
            <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.35rem' }}>
              {subtitle}
            </p>
          )}
        </div>
        <div
          style={{
            width: '48px',
            height: '48px',
            borderRadius: '12px',
            background: bg || 'rgba(99, 102, 241, 0.15)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: color || 'var(--primary)',
          }}
        >
          {Icon && <Icon size={24} />}
        </div>
      </div>
    </Card>
  );
}
