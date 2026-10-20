/**
 * Administrative action audit log table showing historical operations.
 */

import React from 'react';
import Card from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';

export default function AuditLogsTable({ logs = [] }) {
  if (logs.length === 0) {
    return (
      <Card title="Administrative Audit Trail" subtitle="Chronological record of privileged system actions">
        <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
          No privileged administrative events recorded yet.
        </div>
      </Card>
    );
  }

  return (
    <Card title="Administrative Audit Trail" subtitle="Immutable chronological log of privileged operations" noPadding>
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border)', background: 'rgba(255, 255, 255, 0.02)' }}>
              <th style={{ padding: '0.85rem 1.5rem', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Action</th>
              <th style={{ padding: '0.85rem 1.5rem', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Administrator</th>
              <th style={{ padding: '0.85rem 1.5rem', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Details</th>
              <th style={{ padding: '0.85rem 1.5rem', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Timestamp</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((item, idx) => (
              <tr key={item.id || idx} style={{ borderBottom: '1px solid var(--border)' }}>
                <td style={{ padding: '1rem 1.5rem' }}>
                  <Badge variant="primary">{item.action}</Badge>
                </td>
                <td style={{ padding: '1rem 1.5rem', fontSize: '0.85rem', fontWeight: 500, color: 'var(--text-primary)' }}>
                  {item.performed_by}
                </td>
                <td style={{ padding: '1rem 1.5rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                  {item.details}
                </td>
                <td style={{ padding: '1rem 1.5rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  {item.timestamp ? new Date(item.timestamp).toLocaleString() : 'N/A'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}
