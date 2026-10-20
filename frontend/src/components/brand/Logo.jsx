import React from 'react';
import PropTypes from 'prop-types';
import { cn } from '@/lib/utils';
import LogoSymbol from '@/components/brand/LogoSymbol';

/**
 * Master Automio Logo with Typographic Lockup
 * Fuses the neuro-prism mark with high-contrast lettering and live status telemetry.
 */
export const Logo = ({
  className = '',
  size = 36,
  variant = 'full', // 'full' | 'compact' | 'symbol'
  theme = 'dark',   // 'dark' | 'light'
  subtitle = 'AI SALES PLATFORM',
  showStatusDot = true
}) => {
  const isLight = theme === 'light';

  if (variant === 'symbol') {
    return (
      <div className={cn('inline-flex items-center justify-center', className)}>
        <LogoSymbol size={size} />
        <span className="sr-only">Automio</span>
      </div>
    );
  }

  return (
    <div className={cn('inline-flex items-center gap-3 select-none group', className)}>
      <LogoSymbol size={size} />

      <div className="flex flex-col justify-center leading-none">
        {/* Main Brand Wordmark */}
        <div className="flex items-center font-bold tracking-[0.04em] font-sans">
          <span
            className={cn(
              'text-[19px] tracking-[0.04em] transition-colors',
              isLight ? 'text-slate-900' : 'text-white'
            )}
          >
            AUTO
          </span>
          <span className="text-[19px] tracking-[0.04em] bg-gradient-to-r from-sky-400 to-blue-400 bg-clip-text text-transparent group-hover:from-sky-300 group-hover:to-blue-300 transition-all drop-shadow-[0_0_12px_rgba(56,189,248,0.35)]">
            MIO
          </span>
        </div>

        {/* Category Subtitle & Live Status Indicator */}
        {variant === 'full' && (
          <div className="flex items-center gap-1.5 mt-1">
            {showStatusDot && (
              <span className="relative flex h-1.5 w-1.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-emerald-400" />
              </span>
            )}
            <span
              className={cn(
                'text-[8.5px] font-semibold tracking-[0.22em] uppercase',
                isLight ? 'text-slate-500' : 'text-slate-400'
              )}
            >
              {subtitle}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

Logo.propTypes = {
  className: PropTypes.string,
  size: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  variant: PropTypes.oneOf(['full', 'compact', 'symbol']),
  theme: PropTypes.oneOf(['dark', 'light']),
  subtitle: PropTypes.string,
  showStatusDot: PropTypes.bool
};

export { LogoSymbol };
export default Logo;
