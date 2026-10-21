/**
 * Master Automio Logo with Typographic Lockup for the Admin Commander.
 * Fuses the neuro-prism mark with high-contrast lettering and live status telemetry.
 */

import React from 'react';
import LogoSymbol from './LogoSymbol';

export default function Logo({
  size = 32,
  variant = 'full', // 'full' | 'compact' | 'symbol'
  subtitle = 'ADMIN COMMANDER',
  showStatusDot = true,
  className = '',
}) {
  if (variant === 'symbol') {
    return (
      <div style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center' }} className={className}>
        <LogoSymbol size={size} />
      </div>
    );
  }

  return (
    <div
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '0.75rem',
        userSelect: 'none',
      }}
      className={className}
    >
      <LogoSymbol size={size} />

      <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', lineHeight: 1 }}>
        {/* Main Brand Wordmark */}
        <div style={{ display: 'flex', alignItems: 'center', fontWeight: 800, letterSpacing: '0.04em' }}>
          <span style={{ fontSize: '1.1rem', color: '#FFFFFF', letterSpacing: '0.04em' }}>
            AUTO
          </span>
          <span
            style={{
              fontSize: '1.1rem',
              letterSpacing: '0.04em',
              background: 'linear-gradient(135deg, #38BDF8 0%, #0EA5E9 50%, #2563EB 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              filter: 'drop-shadow(0 0 10px rgba(56, 189, 248, 0.4))',
            }}
          >
            MIO
          </span>
        </div>

        {/* Category Subtitle & Live Status Indicator */}
        {variant === 'full' && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginTop: '0.3rem' }}>
            {showStatusDot && (
              <span
                style={{
                  display: 'inline-block',
                  width: '6px',
                  height: '6px',
                  borderRadius: '50%',
                  background: 'var(--success)',
                  boxShadow: '0 0 8px rgba(16, 185, 129, 0.6)',
                }}
              />
            )}
            <span
              style={{
                fontSize: '0.65rem',
                fontWeight: 700,
                letterSpacing: '0.15em',
                textTransform: 'uppercase',
                color: 'var(--primary)',
              }}
            >
              {subtitle}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}

export { LogoSymbol };
