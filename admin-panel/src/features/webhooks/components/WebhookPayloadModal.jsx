/**
 * Inspection modal for webhook delivery responses and raw payload data.
 */

import React from 'react';
import Modal from '@/components/ui/Modal';
import Badge from '@/components/ui/Badge';
import Button from '@/components/ui/Button';

export default function WebhookPayloadModal({ isOpen, onClose, log, onRetry }) {
  if (!log) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Webhook Event Inspector" maxWidth="650px">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <h4 style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--text-primary)' }}>
              {log.event_type}
            </h4>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>ID: {log.id}</span>
          </div>
          <Badge variant={log.status === 'success' ? 'success' : 'danger'}>{log.status}</Badge>
        </div>

        <div>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
            HTTP Response Body
          </span>
          <pre
            style={{
              marginTop: '0.4rem',
              padding: '1rem',
              background: 'var(--bg-base)',
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius-md)',
              fontSize: '0.8rem',
              color: 'var(--text-secondary)',
              maxHeight: '200px',
              overflowY: 'auto',
              whiteSpace: 'pre-wrap',
            }}
          >
            {log.response_body || 'No response body stored.'}
          </pre>
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', paddingTop: '1rem', borderTop: '1px solid var(--border)' }}>
          <Button variant="secondary" onClick={onClose}>
            Close
          </Button>
          {log.status !== 'success' && (
            <Button
              variant="primary"
              onClick={() => {
                onRetry(log.id);
                onClose();
              }}
            >
              Retry Dispatch
            </Button>
          )}
        </div>
      </div>
    </Modal>
  );
}
