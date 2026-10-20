/**
 * Collapsible administrative sidebar navigation.
 */

import React from 'react';
import { NavLink } from 'react-router-dom';
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
  ShieldCheck,
  ExternalLink,
} from 'lucide-react';
import { useAdminStore } from '@/store/adminStore';

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
  const { logout, user } = useAdminStore();

  return (
    <aside
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
        zIndex: 50,
      }}
    >
      {/* Brand Header */}
      <div
        style={{
          padding: '1.25rem 1.5rem',
          borderBottom: '1px solid var(--border)',
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem',
        }}
      >
        <div
          style={{
            width: '36px',
            height: '36px',
            borderRadius: '10px',
            background: 'linear-gradient(135deg, #6366F1 0%, #4F46E5 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            boxShadow: '0 4px 12px rgba(99, 102, 241, 0.4)',
          }}
        >
          <ShieldCheck size={20} />
        </div>
        <div>
          <h2 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-primary)' }}>
            Admin Commander
          </h2>
          <span style={{ fontSize: '0.7rem', color: '#10B981', fontWeight: 600 }}>
            ● ROOT PRIVILEGES
          </span>
        </div>
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
            letterSpacing: '0.05em',
            paddingLeft: '0.75rem',
            marginBottom: '0.5rem',
          }}
        >
          Operations
        </div>

        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            style={({ isActive }) => ({
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
              padding: '0.65rem 0.85rem',
              borderRadius: 'var(--radius-md)',
              textDecoration: 'none',
              fontSize: '0.85rem',
              fontWeight: isActive ? 600 : 500,
              color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)',
              background: isActive ? 'var(--primary-light)' : 'transparent',
              border: isActive ? '1px solid rgba(99, 102, 241, 0.3)' : '1px solid transparent',
              transition: 'all 0.15s ease',
            })}
          >
            <item.icon size={18} style={{ color: 'var(--primary)' }} />
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
        }}
      >
        <div style={{ padding: '0.25rem 0.5rem' }}>
          <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-primary)' }}>
            {user?.name || 'Administrator'}
          </div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', overflow: 'hidden', textOverflow: 'ellipsis' }}>
            {user?.email || 'admin@platform.local'}
          </div>
        </div>

        <button
          onClick={logout}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.6rem',
            padding: '0.6rem 0.75rem',
            width: '100%',
            borderRadius: 'var(--radius-md)',
            color: 'var(--danger)',
            background: 'transparent',
            border: 'none',
            cursor: 'pointer',
            fontSize: '0.825rem',
            fontWeight: 500,
            transition: 'background 0.2s ease',
          }}
          onMouseEnter={(e) => (e.currentTarget.style.background = 'rgba(239, 68, 68, 0.1)')}
          onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
        >
          <LogOut size={16} />
          <span>Sign Out</span>
        </button>
      </div>
    </aside>
  );
}
