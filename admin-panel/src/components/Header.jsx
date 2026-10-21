/**
 * Administrative header with live system indicators and quick controls.
 */

import React, { useEffect, useState } from 'react';
import { Activity, RefreshCw, ExternalLink, Shield } from 'lucide-react';
import { adminApi } from '@/lib/api';
import { useAdminStore } from '@/store/adminStore';
import Badge from '@/components/ui/Badge';

const MAIN_APP_URL = import.meta.env.VITE_MAIN_APP_URL || (import.meta.env.PROD ? 'https://app.automio.online' : 'http://localhost:5173');

export default function Header() {
  const { systemHealth, setSystemHealth } = useAdminStore();
  const [isRefreshing, setIsRefreshing] = useState(false);

  const fetchHealth = async () => {
    try {
      setIsRefreshing(true);
      const res = await adminApi.getHealth();
      setSystemHealth(res.data);
    } catch (err) {
      console.error('Failed to poll health:', err);
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchHealth();
    const interval = setInterval(fetchHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header
      style={{
        height: 'var(--header-height)',
        background: 'rgba(21, 26, 34, 0.85)',
        backdropFilter: 'blur(16px)',
        borderBottom: '1px solid var(--border)',
        position: 'sticky',
        top: 0,
        zIndex: 40,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 2rem',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <Badge variant="primary">Platform Control Center</Badge>
        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
          Environment: <strong style={{ color: 'var(--text-secondary)' }}>Production Ready</strong>
        </span>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
        {/* System Health Indicators */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Badge
            variant={systemHealth?.database?.status === 'healthy' ? 'success' : 'danger'}
          >
            DB: {systemHealth?.database?.latency_ms || 0}ms
          </Badge>
          <Badge
            variant={systemHealth?.ai_engine?.status === 'healthy' ? 'success' : 'warning'}
          >
            AI: {systemHealth?.ai_engine?.primary_model || 'active'}
          </Badge>
        </div>

        {/* Refresh Button */}
        <button
          onClick={fetchHealth}
          disabled={isRefreshing}
          style={{
            background: 'rgba(255, 255, 255, 0.05)',
            border: '1px solid var(--border)',
            borderRadius: 'var(--radius-md)',
            color: 'var(--text-secondary)',
            padding: '0.45rem',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
          }}
          title="Refresh telemetry"
        >
          <RefreshCw
            size={16}
            style={{ animation: isRefreshing ? 'spin 1s linear infinite' : 'none' }}
          />
        </button>

        {/* Link back to Main App */}
        <a
          href={MAIN_APP_URL}
          target="_blank"
          rel="noopener noreferrer"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            fontSize: '0.8rem',
            fontWeight: 500,
            color: 'var(--primary)',
            textDecoration: 'none',
            padding: '0.45rem 0.8rem',
            background: 'var(--primary-light)',
            borderRadius: 'var(--radius-md)',
            border: '1px solid rgba(99, 102, 241, 0.3)',
          }}
        >
          <span>Open Main App</span>
          <ExternalLink size={14} />
        </a>
      </div>
    </header>
  );
}
