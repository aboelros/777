/**
 * Status indicator badge component.
 */

import React from 'react';

export default function Badge({ children, variant = 'neutral', className = '' }) {
  const getStyles = () => {
    switch (variant) {
      case 'success':
        return {
          background: 'rgba(16, 185, 129, 0.15)',
          color: '#10B981',
          border: '1px solid rgba(16, 185, 129, 0.3)',
        };
      case 'danger':
        return {
          background: 'rgba(239, 68, 68, 0.15)',
          color: '#EF4444',
          border: '1px solid rgba(239, 68, 68, 0.3)',
        };
      case 'warning':
        return {
          background: 'rgba(245, 158, 11, 0.15)',
          color: '#F59E0B',
          border: '1px solid rgba(245, 158, 11, 0.3)',
        };
      case 'primary':
        return {
          background: 'rgba(99, 102, 241, 0.15)',
          color: '#818CF8',
          border: '1px solid rgba(99, 102, 241, 0.3)',
        };
      case 'neutral':
      default:
        return {
          background: 'rgba(255, 255, 255, 0.08)',
          color: 'var(--text-secondary)',
          border: '1px solid var(--border)',
        };
    }
  };

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        padding: '0.2rem 0.6rem',
        borderRadius: '9999px',
        fontSize: '0.75rem',
        fontWeight: 600,
        letterSpacing: '0.02em',
        textTransform: 'uppercase',
        ...getStyles(),
      }}
      className={className}
    >
      {children}
    </span>
  );
}
