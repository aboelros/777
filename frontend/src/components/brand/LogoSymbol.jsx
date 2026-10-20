import React from 'react';
import PropTypes from 'prop-types';
import { cn } from '@/lib/utils';

/**
 * Automind Enhanced Neuro-Prism Brand Mark Symbol
 * Geometric vector fusing "A" (Automation) and "M" (Mind) with a luminous cognitive core.
 */
export default function LogoSymbol({ size = 36, className = '', animated = true }) {
  const numericSize =
    typeof size === 'number'
      ? size
      : { sm: 28, md: 36, lg: 44, xl: 56 }[size] || 36;

  return (
    <div
      className={cn(
        'relative inline-flex items-center justify-center flex-shrink-0 group cursor-pointer select-none',
        className
      )}
      style={{ width: numericSize, height: numericSize }}
    >
      <div className="absolute inset-0 rounded-xl bg-sky-500/0 group-hover:bg-sky-500/25 blur-md transition-all duration-300 pointer-events-none" />

      <svg
        width={numericSize}
        height={numericSize}
        viewBox="0 0 40 40"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="w-full h-full relative z-10 transition-transform duration-300 ease-out group-hover:scale-105"
        aria-hidden="true"
      >
        <defs>
          <radialGradient id="am-squircle-bg" cx="50%" cy="25%" r="80%" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#0F1F38" />
            <stop offset="55%" stopColor="#080E1D" />
            <stop offset="100%" stopColor="#03060E" />
          </radialGradient>
          <linearGradient id="am-rim-border" x1="2" y1="2" x2="38" y2="38" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#38BDF8" stopOpacity="0.7" />
            <stop offset="35%" stopColor="#2563EB" stopOpacity="0.4" />
            <stop offset="70%" stopColor="#1E293B" stopOpacity="0.3" />
            <stop offset="100%" stopColor="#0284C7" stopOpacity="0.5" />
          </linearGradient>
          <linearGradient id="am-apex-grad" x1="12" y1="8" x2="28" y2="18" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#38BDF8" />
            <stop offset="45%" stopColor="#0EA5E9" />
            <stop offset="100%" stopColor="#2563EB" />
          </linearGradient>
          <linearGradient id="am-wing-left" x1="8" y1="19" x2="19" y2="31" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#0284C7" />
            <stop offset="60%" stopColor="#2563EB" />
            <stop offset="100%" stopColor="#1D4ED8" />
          </linearGradient>
          <linearGradient id="am-wing-right" x1="21" y1="19" x2="32" y2="31" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#38BDF8" />
            <stop offset="50%" stopColor="#2563EB" />
            <stop offset="100%" stopColor="#4F46E5" />
          </linearGradient>
          <linearGradient id="am-core-grad" x1="20" y1="16.5" x2="20" y2="25.5" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#FFFFFF" />
            <stop offset="40%" stopColor="#E0F2FE" />
            <stop offset="100%" stopColor="#38BDF8" />
          </linearGradient>
          <filter id="am-core-blur" x="12" y="14" width="16" height="16" filterUnits="userSpaceOnUse">
            <feGaussianBlur stdDeviation="1.5" />
          </filter>
        </defs>

        <rect x="2" y="2" width="36" height="36" rx="10" fill="url(#am-squircle-bg)" />
        <rect x="2" y="2" width="36" height="36" rx="10" stroke="url(#am-rim-border)" strokeWidth="1.2" />
        <path d="M6 10C6 6.68629 8.68629 4 12 4H28C31.3137 4 34 6.68629 34 10V14C34 14 26 12 20 12C14 12 6 14 6 14V10Z" fill="white" fillOpacity="0.04" />
        <circle cx="20" cy="21" r="4.5" fill="#38BDF8" fillOpacity="0.45" filter="url(#am-core-blur)" />
        <path d="M20 7.5L27.5 17H23L20 13.2L17 17H12.5L20 7.5Z" fill="url(#am-apex-grad)" />
        <path d="M12.5 18.5L17 18.5L18.5 23.5H16L12.5 31H8L12.5 18.5Z" fill="url(#am-wing-left)" />
        <path d="M27.5 18.5L23 18.5L21.5 23.5H24L27.5 31H32L27.5 18.5Z" fill="url(#am-wing-right)" />
        <path d="M14.5 27H25.5L24.5 28.5H15.5L14.5 27Z" fill="#38BDF8" fillOpacity="0.35" />
        <path d="M20 16.5L22.8 21L20 25.5L17.2 21Z" fill="url(#am-core-grad)" className={animated ? 'animate-pulse' : ''} />
      </svg>
    </div>
  );
}

LogoSymbol.propTypes = {
  size: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  className: PropTypes.string,
  animated: PropTypes.bool
};

export { LogoSymbol };
