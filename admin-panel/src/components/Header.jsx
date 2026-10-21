/**
 * Administrative header with live system indicators and quick controls.
 * Features responsive hamburger navigation trigger and touch-optimized controls.
 */

import React, { useEffect, useState } from 'react';
import { RefreshCw, ExternalLink, Menu } from 'lucide-react';
import { adminApi } from '@/lib/api';
import { useAdminStore } from '@/store/adminStore';
import Badge from '@/components/ui/Badge';
import LogoSymbol from '@/components/brand/LogoSymbol';

const MAIN_APP_URL =
  import.meta.env.VITE_MAIN_APP_URL ||
  (import.meta.env.PROD ? 'https://app.automio.online' : 'http://localhost:5173');

export default function Header() {
  const { systemHealth, setSystemHealth, toggleMobileNav } = useAdminStore();
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
        background: 'rgba(15, 23, 42, 0.85)',
        backdropFilter: 'blur(16px)',
        WebkitBackdropFilter: 'blur(16px)',
        borderBottom: '1px solid var(--border)',
        position: 'sticky',
        top: 0,
        zIndex: 40,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 1.25rem',
        boxSizing: 'border-box',
        width: '100%',
      }}
    >
      {/* Left Section: Mobile Menu Trigger + Brand/Pill */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
        <button
          onClick={toggleMobileNav}
          className="mobile-only"
          style={{
            background: 'rgba(255, 255, 255, 0.05)',
            border: '1px solid var(--border)',
            borderRadius: 'var(--radius-md)',
            color: 'var(--text-primary)',
            minWidth: 'var(--touch-target-min)',
            minHeight: 'var(--touch-target-min)',
            display: 'none',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer',
          }}
          aria-label="Open navigation menu"
        >
          <Menu size={20} />
        </button>

        {/* Brand symbol shown on mobile when sidebar is closed */}
        <div className="mobile-only" style={{ display: 'none', alignItems: 'center', gap: '0.5rem' }}>
          <LogoSymbol size={28} />
          <span style={{ fontSize: '0.9rem', fontWeight: 700, color: '#FFFFFF' }}>
            AUTO<span style={{ color: 'var(--primary)' }}>MIO</span>
          </span>
        </div>

        {/* Desktop title pills */}
        <div className="desktop-only" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Badge variant="primary">Mission Control</Badge>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Environment: <strong style={{ color: 'var(--text-secondary)' }}>Production</strong>
          </span>
        </div>
      </div>

      {/* Right Section: Telemetry Indicators + Quick Actions */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        {/* Health Indicators (Desktop) */}
        <div className="desktop-only" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Badge variant={systemHealth?.database?.status === 'healthy' ? 'success' : 'danger'}>
            DB: {systemHealth?.database?.latency_ms || 0}ms
          </Badge>
          <Badge variant={systemHealth?.ai_engine?.status === 'healthy' ? 'success' : 'warning'}>
            AI: {systemHealth?.ai_engine?.primary_model || 'active'}
          </Badge>
        </div>

        {/* Compact Status Indicator (Mobile) */}
        <div className="mobile-only" style={{ display: 'none', alignItems: 'center' }}>
          <Badge variant={systemHealth?.database?.status === 'healthy' ? 'success' : 'warning'}>
            ● Live
          </Badge>
        </div>

        {/* Refresh Telemetry */}
        <button
          onClick={fetchHealth}
          disabled={isRefreshing}
          style={{
            background: 'rgba(255, 255, 255, 0.05)',
            border: '1px solid var(--border)',
            borderRadius: 'var(--radius-md)',
            color: 'var(--text-secondary)',
            minWidth: 'var(--touch-target-min)',
            minHeight: 'var(--touch-target-min)',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'all 0.2s ease',
          }}
          title="Refresh telemetry"
          aria-label="Refresh telemetry"
        >
          <RefreshCw
            size={16}
            style={{ animation: isRefreshing ? 'spin 1s linear infinite' : 'none' }}
          />
        </button>

        {/* Link to Main App */}
        <a
          href={MAIN_APP_URL}
          target="_blank"
          rel="noopener noreferrer"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            fontSize: '0.8rem',
            fontWeight: 600,
            color: 'var(--primary)',
            textDecoration: 'none',
            minHeight: 'var(--touch-target-min)',
            padding: '0 0.85rem',
            background: 'var(--primary-light)',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--border-brand)',
            transition: 'all 0.2s ease',
            whiteSpace: 'nowrap',
          }}
        >
          <span className="desktop-only">App</span>
          <ExternalLink size={14} />
        </a>
      </div>
    </header>
  );
}
