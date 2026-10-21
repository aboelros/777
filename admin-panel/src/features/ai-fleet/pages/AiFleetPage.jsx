/**
 * AI fleet telemetry and autonomous bot control center.
 */

import React from 'react';
import { useAiTelemetry } from '../hooks/useAiTelemetry';
import AiTelemetryCard from '../components/AiTelemetryCard';
import ModelConfigForm from '../components/ModelConfigForm';

export default function AiFleetPage() {
  const { telemetry, loading, error, refetch } = useAiTelemetry();

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', width: '100%', minWidth: 0 }}>
      <div>
        <h1 style={{ fontSize: '1.65rem', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
          AI Model Fleet & Telemetry
        </h1>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
          Real-time inference speed, model candidate health, token consumption, and global parameters
        </p>
      </div>

      {error && (
        <div style={{ padding: '1rem', background: 'rgba(239, 68, 68, 0.1)', color: 'var(--danger)', borderRadius: 'var(--radius-md)' }}>
          {error}
        </div>
      )}

      {loading && !telemetry ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: '3rem' }}>
          <div className="spinner" style={{ width: '32px', height: '32px' }} />
        </div>
      ) : (
        <>
          <AiTelemetryCard telemetry={telemetry} />
          <ModelConfigForm telemetry={telemetry} onUpdated={refetch} />
        </>
      )}
    </div>
  );
}
