import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

/**
 * Standardized Automio Glass Panel / Elevated Card Component
 */
export default function GlassCard({
  children,
  className,
  hover = true,
  animate = true,
  pulse = false,
  delay = 0,
  glow = false,
  ...props
}) {
  const Component = animate ? motion.div : 'div';

  const pulseClass = pulse ? 'ring-1 ring-brand-accent/40 shadow-brand-glow' : '';
  const glowClass = glow ? 'shadow-brand-glow border-brand-accent/30' : '';

  const motionProps = animate ? {
    initial: { opacity: 0, y: 12 },
    animate: { opacity: 1, y: 0 },
    transition: {
      duration: 0.35,
      delay,
      ease: [0.16, 1, 0.3, 1]
    },
    whileHover: hover ? { y: -2, transition: { duration: 0.2 } } : {},
  } : {};

  return (
    <Component
      className={cn('glass-card', pulseClass, glowClass, className)}
      {...motionProps}
      {...props}
    >
      {/* Top specular liquid reflection */}
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/30 to-transparent pointer-events-none" />
      {/* Subtle liquid chromatic corner glow */}
      <div className="absolute -top-12 -right-12 w-28 h-28 bg-sky-500/8 rounded-full blur-2xl pointer-events-none group-hover:bg-sky-500/20 transition-all duration-500" />
      {/* Content Container */}
      <div className={cn('relative z-10', className?.includes('h-full') && 'h-full', className?.includes('flex') && 'flex flex-col min-h-0')}>
        {children}
      </div>
    </Component>
  );
}
