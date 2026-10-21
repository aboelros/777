/**
 * Global platform settings page.
 */

import React from 'react';
import { usePlatformSettings } from '../hooks/usePlatformSettings';
import PlatformTogglesForm from '../components/PlatformTogglesForm';

export default function SettingsPage() {
  const { settings, loading, error, updateSettings } = usePlatformSettings();

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', width: '100%', minWidth: 0 }}>
      <div>
        <h1 style={{ fontSize: '1.65rem', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
          Platform Configuration & Toggles
        </h1>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
          Global operational gates, public signups, free tier limits, and system maintenance
        </p>
      </div>

      {error && (
        <div style={{ padding: '1rem', background: 'rgba(239, 68, 68, 0.1)', color: 'var(--danger)', borderRadius: 'var(--radius-md)' }}>
          {error}
        </div>
      )}

      {loading && !settings ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: '3rem' }}>
          <div className="spinner" style={{ width: '32px', height: '32px' }} />
        </div>
      ) : (
        <PlatformTogglesForm settings={settings} onSave={updateSettings} />
      )}
    </div>
  );
}
