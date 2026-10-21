/**
 * System diagnostics and security audit trail page.
 */

import React from 'react';
import Button from '@/components/ui/Button';
import { useSystemStatus } from '../hooks/useSystemStatus';
import ServiceStatusGrid from '../components/ServiceStatusGrid';
import AuditLogsTable from '../components/AuditLogsTable';

export default function SystemHealthPage() {
  const { health, auditLogs, loading, error, refetch } = useSystemStatus();

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', width: '100%', minWidth: 0 }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 style={{ fontSize: '1.65rem', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
            System Fleet Diagnostics
          </h1>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
            Infrastructure latency, connection statuses, and chronological security audit trail
          </p>
        </div>

        <Button variant="secondary" onClick={refetch}>
          Refresh Telemetry
        </Button>
      </div>

      {error && (
        <div style={{ padding: '1rem', background: 'rgba(239, 68, 68, 0.1)', color: 'var(--danger)', borderRadius: 'var(--radius-md)' }}>
          {error}
        </div>
      )}

      {loading && !health ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: '3rem' }}>
          <div className="spinner" style={{ width: '32px', height: '32px' }} />
        </div>
      ) : (
        <>
          <ServiceStatusGrid health={health} />
          <AuditLogsTable logs={auditLogs} />
        </>
      )}
    </div>
  );
}
