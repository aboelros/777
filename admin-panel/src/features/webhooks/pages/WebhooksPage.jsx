/**
 * Webhook event delivery logs and failure replay management page.
 */

import React, { useState } from 'react';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import { useWebhookLogs } from '../hooks/useWebhookLogs';
import WebhookLogTable from '../components/WebhookLogTable';
import WebhookPayloadModal from '../components/WebhookPayloadModal';

export default function WebhooksPage() {
  const [filter, setFilter] = useState('');
  const { logs, total, loading, error, refetch, retryWebhook } = useWebhookLogs(1, filter);
  const [inspectModal, setInspectModal] = useState({ isOpen: false, log: null });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', width: '100%', minWidth: 0 }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 style={{ fontSize: '1.65rem', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
            Webhook Observability & Logs
          </h1>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
            Inbound and outbound integration event dispatch log with automated replay
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            style={{
              padding: '0.5rem 1rem',
              background: 'var(--bg-surface)',
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius-md)',
              color: 'var(--text-primary)',
              fontSize: '0.85rem',
            }}
          >
            <option value="">All Delivery Statuses</option>
            <option value="success">Success (200)</option>
            <option value="failed">Failed / Error</option>
            <option value="pending">Pending</option>
          </select>
          <Button variant="secondary" size="md" onClick={refetch}>
            Refresh Logs
          </Button>
        </div>
      </div>

      {error && (
        <div style={{ padding: '1rem', background: 'rgba(239, 68, 68, 0.1)', color: 'var(--danger)', borderRadius: 'var(--radius-md)' }}>
          {error}
        </div>
      )}

      <Card title="Event Dispatch Log" subtitle={`Total logged events: ${total}`} noPadding>
        <WebhookLogTable
          logs={logs}
          loading={loading}
          onInspect={(l) => setInspectModal({ isOpen: true, log: l })}
          onRetry={retryWebhook}
        />
      </Card>

      <WebhookPayloadModal
        isOpen={inspectModal.isOpen}
        onClose={() => setInspectModal({ isOpen: false, log: null })}
        log={inspectModal.log}
        onRetry={retryWebhook}
      />
    </div>
  );
}
