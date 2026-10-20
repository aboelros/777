import React from 'react';
import { cn } from '@/lib/utils';

/**
 * Standardized Automind Status & Metadata Badge Component
 */
export const Badge = ({
  children,
  variant = 'default',
  size = 'md',
  dot = false,
  className = '',
  ...props
}) => {
  const variants = {
    default: 'bg-white/[0.04] text-secondary border-white/10 backdrop-blur-md',
    brand: 'bg-sky-500/15 text-sky-300 border-sky-400/30 shadow-[0_0_12px_rgba(14,165,233,0.15)] backdrop-blur-md',
    success: 'bg-emerald-500/15 text-emerald-300 border-emerald-400/30 shadow-[0_0_12px_rgba(16,185,129,0.15)] backdrop-blur-md',
    warning: 'bg-amber-500/15 text-amber-300 border-amber-400/30 shadow-[0_0_12px_rgba(245,158,11,0.15)] backdrop-blur-md',
    danger: 'bg-rose-500/15 text-rose-300 border-rose-400/30 shadow-[0_0_12px_rgba(244,63,94,0.15)] backdrop-blur-md',
    info: 'bg-indigo-500/15 text-indigo-300 border-indigo-400/30 shadow-[0_0_12px_rgba(99,102,241,0.15)] backdrop-blur-md',
    neutral: 'bg-white/[0.04] text-slate-300 border-white/10 backdrop-blur-md',
    outline: 'bg-transparent text-secondary border-white/15 backdrop-blur-sm',
  };

  const dotColors = {
    default: 'bg-slate-400',
    brand: 'bg-sky-400',
    success: 'bg-emerald-400 shadow-[0_0_6px_rgba(16,185,129,0.5)]',
    warning: 'bg-amber-400 shadow-[0_0_6px_rgba(245,158,11,0.5)]',
    danger: 'bg-red-400 shadow-[0_0_6px_rgba(239,68,68,0.5)]',
    info: 'bg-sky-400 shadow-[0_0_6px_rgba(14,165,233,0.5)]',
    neutral: 'bg-slate-400',
    outline: 'bg-slate-400',
  };

  const sizes = {
    sm: 'text-[11px] px-2 py-0.5 gap-1.5 font-medium',
    md: 'text-xs px-2.5 py-1 gap-2 font-medium',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full border transition-colors select-none tracking-wide',
        variants[variant] || variants.default,
        sizes[size] || sizes.md,
        className
      )}
      {...props}
    >
      {dot && (
        <span
          className={cn('w-1.5 h-1.5 rounded-full flex-shrink-0', dotColors[variant] || dotColors.default)}
          aria-hidden="true"
        />
      )}
      {children}
    </span>
  );
};

export default Badge;
