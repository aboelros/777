/**
 * Form input component with optional label, helper text, and icon.
 */

import React from 'react';

export default function Input({
  label,
  error,
  icon: Icon,
  type = 'text',
  className = '',
  id,
  ...props
}) {
  const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', width: '100%' }}>
      {label && (
        <label
          htmlFor={inputId}
          style={{ fontSize: '0.85rem', fontWeight: 500, color: 'var(--text-secondary)' }}
        >
          {label}
        </label>
      )}
      <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
        {Icon && (
          <div
            style={{
              position: 'absolute',
              left: '1rem',
              color: 'var(--text-muted)',
              display: 'flex',
              alignItems: 'center',
              pointerEvents: 'none',
            }}
          >
            <Icon size={18} />
          </div>
        )}
        <input
          id={inputId}
          type={type}
          style={{
            width: '100%',
            padding: '0.65rem 1rem',
            paddingLeft: Icon ? '2.75rem' : '1rem',
            background: 'var(--bg-base)',
            border: error ? '1px solid var(--danger)' : '1px solid var(--border)',
            borderRadius: 'var(--radius-md)',
            color: 'var(--text-primary)',
            fontSize: '0.875rem',
            outline: 'none',
            transition: 'border-color 0.2s ease',
          }}
          className={className}
          {...props}
        />
      </div>
      {error && <span style={{ fontSize: '0.75rem', color: 'var(--danger)' }}>{error}</span>}
    </div>
  );
}
