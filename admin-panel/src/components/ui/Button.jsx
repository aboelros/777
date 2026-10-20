/**
 * Reusable Button component supporting primary, secondary, danger, and ghost variants.
 */

import React from 'react';

export default function Button({
  children,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  disabled = false,
  className = '',
  onClick,
  type = 'button',
  icon: Icon,
  ...props
}) {
  const getVariantStyles = () => {
    switch (variant) {
      case 'secondary':
        return {
          background: 'rgba(255, 255, 255, 0.08)',
          color: 'var(--text-primary)',
          border: '1px solid var(--border)',
        };
      case 'danger':
        return {
          background: 'rgba(239, 68, 68, 0.15)',
          color: 'var(--danger)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
        };
      case 'ghost':
        return {
          background: 'transparent',
          color: 'var(--text-secondary)',
          border: '1px solid transparent',
        };
      case 'primary':
      default:
        return {
          background: 'linear-gradient(135deg, #6366F1 0%, #4F46E5 100%)',
          color: '#ffffff',
          border: '1px solid rgba(99, 102, 241, 0.4)',
          boxShadow: '0 4px 14px rgba(99, 102, 241, 0.35)',
        };
    }
  };

  const getSizeStyles = () => {
    switch (size) {
      case 'sm':
        return { padding: '0.4rem 0.75rem', fontSize: '0.8rem', borderRadius: '6px' };
      case 'lg':
        return { padding: '0.75rem 1.5rem', fontSize: '1rem', borderRadius: '10px' };
      case 'md':
      default:
        return { padding: '0.55rem 1.1rem', fontSize: '0.875rem', borderRadius: '8px' };
    }
  };

  return (
    <button
      type={type}
      disabled={disabled || isLoading}
      onClick={onClick}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '0.5rem',
        fontWeight: 500,
        cursor: disabled || isLoading ? 'not-allowed' : 'pointer',
        opacity: disabled || isLoading ? 0.6 : 1,
        transition: 'all 0.2s ease',
        ...getVariantStyles(),
        ...getSizeStyles(),
      }}
      className={className}
      {...props}
    >
      {isLoading ? (
        <span
          className="spinner"
          style={{ width: '16px', height: '16px', borderWidth: '2px', borderColor: 'currentColor' }}
        />
      ) : (
        Icon && <Icon size={size === 'sm' ? 14 : 18} />
      )}
      {children}
    </button>
  );
}
