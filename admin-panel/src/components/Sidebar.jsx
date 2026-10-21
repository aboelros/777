/**
 * Responsive administrative sidebar drawer navigation.
 * Switches between persistent desktop navigation and off-canvas mobile drawer.
 */

import React, { useEffect } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Users,
  Store,
  CreditCard,
  Bot,
  Webhook,
  Activity,
  Settings,
  LogOut,
  X,
} from 'lucide-react';
import { useAdminStore } from '@/store/adminStore';
import Logo from '@/components/brand/Logo';

const navItems = [
  { name: 'Overview', path: '/', icon: LayoutDashboard },
  { name: 'Users & RBAC', path: '/users', icon: Users },
  { name: 'Store Fleet', path: '/projects', icon: Store },
  { name: 'Billing & MRR', path: '/billing', icon: CreditCard },
  { name: 'AI Telemetry', path: '/ai-fleet', icon: Bot },
  { name: 'Webhooks', path: '/webhooks', icon: Webhook },
  { name: 'System Diagnostics', path: '/system', icon: Activity },
  { name: 'Platform Settings', path: '/settings', icon: Settings },
];

export default function Sidebar() {
  const { logout, user, mobileNavOpen, closeMobileNav } = useAdminStore();
  const location = useLocation();

  // Close mobile drawer on navigation
  useEffect(() => {
    closeMobileNav();
  }, [location.pathname, closeMobileNav]);

  return (
    <>
      {/* Mobile Backdrop Overlay */}
      {mobileNavOpen && (
        <div
          onClick={closeMobileNav}
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(2, 6, 23, 0.75)',
            backdropFilter: 'blur(8px)',
            WebkitBackdropFilter: 'blur(8px)',
            zIndex: 60,
            transition: 'opacity 0.2s ease',
          }}
          aria-hidden="true"
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`admin-sidebar ${mobileNavOpen ? 'open' : ''}`}
        style={{
          width: 'var(--sidebar-width)',
          height: '100vh',
          background: 'var(--bg-surface)',
          borderRight: '1px solid var(--border)',
          position: 'fixed',
          left: 0,
          top: 0,
          display: 'flex',
          flexDirection: 'column',
          zIndex: 70,
          transition: 'transform 0.25s cubic-bezier(0.16, 1, 0.3, 1)',
        }}
      >
        {/* Brand Header */}
        <div
          style={{
            padding: '1.25rem 1.25rem',
            borderBottom: '1px solid var(--border)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <Logo size={32} subtitle="ADMIN COMMANDER" />

          {/* Mobile Close Button */}
          <button
            onClick={closeMobileNav}
            className="mobile-only"
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--text-secondary)',
              cursor: 'pointer',
              padding: '0.4rem',
              borderRadius: 'var(--radius-sm)',
              display: 'none',
              alignItems: 'center',
              justifyContent: 'center',
            }}
            aria-label="Close menu"
          >
            <X size={20} />
          </button>
        </div>

        {/* Navigation List */}
        <div
          style={{
            padding: '1.25rem 0.75rem',
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            gap: '0.35rem',
            overflowY: 'auto',
          }}
        >
          <div
            style={{
              fontSize: '0.7rem',
              fontWeight: 700,
              color: 'var(--text-muted)',
              textTransform: 'uppercase',
              letterSpacing: '0.08em',
              paddingLeft: '0.75rem',
              marginBottom: '0.5rem',
            }}
          >
            Operations Core
          </div>

          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              style={({ isActive }) => ({
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                minHeight: 'var(--touch-target-min)',
                padding: '0.65rem 0.85rem',
                borderRadius: 'var(--radius-md)',
                textDecoration: 'none',
                fontSize: '0.85rem',
                fontWeight: isActive ? 600 : 500,
                color: isActive ? '#FFFFFF' : 'var(--text-secondary)',
                background: isActive ? 'var(--primary-light)' : 'transparent',
                border: isActive ? '1px solid var(--border-brand)' : '1px solid transparent',
                boxShadow: isActive ? '0 0 16px rgba(14, 165, 233, 0.15)' : 'none',
                transition: 'all 0.15s ease',
              })}
            >
              <item.icon size={18} style={{ color: 'var(--primary)', flexShrink: 0 }} />
              <span>{item.name}</span>
            </NavLink>
          ))}
        </div>

        {/* User Info & Footer Actions */}
        <div
          style={{
            padding: '1rem',
            borderTop: '1px solid var(--border)',
            display: 'flex',
            flexDirection: 'column',
            gap: '0.5rem',
            background: 'rgba(2, 6, 23, 0.4)',
          }}
        >
          <div style={{ padding: '0.25rem 0.5rem' }}>
            <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)' }}>
              {user?.name || 'Platform Administrator'}
            </div>
            <div style={{ fontSize: '0.725rem', color: 'var(--text-muted)', overflow: 'hidden', textOverflow: 'ellipsis' }}>
              {user?.email || 'admin@automio.online'}
            </div>
          </div>

          <button
            onClick={logout}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.6rem',
              minHeight: 'var(--touch-target-min)',
              padding: '0.6rem 0.75rem',
              width: '100%',
              borderRadius: 'var(--radius-md)',
              color: 'var(--danger)',
              background: 'transparent',
              border: 'none',
              cursor: 'pointer',
              fontSize: '0.85rem',
              fontWeight: 600,
              transition: 'background 0.2s ease',
            }}
            onMouseEnter={(e) => (e.currentTarget.style.background = 'rgba(244, 63, 94, 0.1)')}
            onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
          >
            <LogOut size={16} />
            <span>Sign Out</span>
          </button>
        </div>
      </aside>
    </>
  );
}
