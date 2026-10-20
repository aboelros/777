import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

/**
 * Standardized Automio Surface Card Component
 */
export default function Card({
  children,
  className = '',
  hover = false,
  glow = false,
  padding = 'p-6',
  delay = 0,
  animate = true,
  ...props
}) {
  const Component = animate ? motion.div : 'div';
  const motionProps = animate ? {
    initial: { opacity: 0, y: 10 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.35, delay, ease: [0.16, 1, 0.3, 1] },
    whileHover: hover ? { y: -2, transition: { duration: 0.2 } } : {},
  } : {};

  return (
    <Component
      className={cn(
        'rounded-2xl bg-[#0c1326]/80 backdrop-blur-xl border border-white/10 border-t-white/20 shadow-[inset_0_1px_1px_rgba(255,255,255,0.15),0_8px_30px_rgba(0,0,0,0.4)] relative overflow-hidden transition-all duration-250',
        padding,
        hover && 'hover:border-sky-400/40 hover:border-t-sky-400/70 hover:shadow-[0_16px_40px_rgba(0,0,0,0.5),0_0_25px_rgba(56,189,248,0.2)] cursor-pointer',
        glow && 'border-sky-400/50 shadow-[0_0_25px_rgba(56,189,248,0.3)]',
        className
      )}
      {...motionProps}
      {...props}
    >
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/25 to-transparent pointer-events-none" />
      {children}
    </Component>
  );
}
