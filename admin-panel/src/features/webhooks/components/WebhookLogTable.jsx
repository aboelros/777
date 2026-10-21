/**
 * Webhook delivery log table displaying status codes, timestamps, and payload previews.
 * Fully responsive with mobile horizontal touch scrolling.
 */

import React from 'react';
import Badge from '@/components/ui/Badge';
import Button from '@/components/ui/Button';
import { RefreshCw, Eye } from 'lucide-react';

export default function WebhookLogTable({ logs = [], loading = false, onInspect, onRetry }) {
  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: '3rem' }}>
        <div className="spinner" style={{ width: '32px', height: '32px' }} />
      </div>
    );
  }

  if (logs.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
        No webhook deliveries logged in the active buffer.
      </div>
    );
  }

  const getStatusVariant = (status, code) => {
    if (status === 'success' || code === '200') return 'success';
    if (status === 'pending') return 'warning';
    return 'danger';
  };

  return (
    <div className="table-responsive-container">
      <table style={{ width: '100%', minWidth: '650px', borderCollapse: 'collapse', textAlign: 'left' }}>
        <thead>
          <tr style={{ borderBottom: '1px solid var(--border)', background: 'rgba(255, 255, 255, 0.02)' }}>
            <th style={{ padding: '0.85rem 1.25rem', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Event Type</th>
            <th style={{ padding: '0.85rem 1.25rem', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Status</th>
            <th style={{ padding: '0.85rem 1.25rem', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>HTTP Code</th>
            <th style={{ padding: '0.85rem 1.25rem', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Response Preview</th>
            <th style={{ padding: '0.85rem 1.25rem', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Logged At</th>
            <th style={{ padding: '0.85rem 1.25rem', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', textAlign: 'right' }}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log) => (
            <tr key={log.id} style={{ borderBottom: '1px solid var(--border)' }}>
              <td style={{ padding: '0.9rem 1.25rem', fontWeight: 600, color: 'var(--text-primary)', fontSize: '0.85rem' }}>
                {log.event_type}
              </td>
              <td style={{ padding: '0.9rem 1.25rem' }}>
                <Badge variant={getStatusVariant(log.status, log.status_code)}>{log.status}</Badge>
              </td>
              <td style={{ padding: '0.9rem 1.25rem', fontFamily: 'monospace', fontSize: '0.8rem' }}>
                {log.status_code || '---'}
              </td>
              <td style={{ padding: '0.9rem 1.25rem', fontSize: '0.8rem', color: 'var(--text-muted)', maxWidth: '240px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {log.response_body || 'No response recorded'}
              </td>
              <td style={{ padding: '0.9rem 1.25rem', fontSize: '0.8rem', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
                {log.created_at ? new Date(log.created_at).toLocaleTimeString() : '---'}
              </td>
              <td style={{ padding: '0.9rem 1.25rem', textAlign: 'right' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '0.4rem' }}>
                  <Button variant="ghost" size="sm" onClick={() => onInspect?.(log)} title="Inspect Payload">
                    <Eye size={15} />
                  </Button>
                  <Button variant="ghost" size="sm" onClick={() => onRetry?.(log.id)} title="Retry Dispatch">
                    <RefreshCw size={15} />
                  </Button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
