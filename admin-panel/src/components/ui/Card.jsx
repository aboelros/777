/**
 * Card surface container with optional header, action slot, and footer.
 */

import React from 'react';

export default function Card({
  title,
  subtitle,
  action,
  children,
  className = '',
  noPadding = false,
  style = {},
}) {
  return (
    <div
      style={{
        background: 'var(--bg-surface)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius-lg)',
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.25)',
        overflow: 'hidden',
        ...style,
      }}
      className={className}
    >
      {(title || action) && (
        <div
          style={{
            padding: '1.25rem 1.5rem',
            borderBottom: '1px solid var(--border)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <div>
            {title && <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-primary)' }}>{title}</h3>}
            {subtitle && <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>{subtitle}</p>}
          </div>
          {action && <div>{action}</div>}
        </div>
      )}
      <div style={{ padding: noPadding ? 0 : '1.5rem' }}>{children}</div>
    </div>
  );
}
