import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { LogoSymbol } from '@/components/brand/Logo';

/**
 * Standardized Automio Loading Indicator
 */
export default function LoadingSpinner({ size = 'md', text = 'Loading...', className = '' }) {
  const sizeClasses = {
    sm: 'w-5 h-5',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
    xl: 'w-16 h-16'
  };

  return (
    <div className={cn('flex flex-col items-center justify-center gap-3', className)} role="status" aria-live="polite">
      <div className={cn('relative', sizeClasses[size])}>
        {/* Outer ring */}
        <motion.div
          className="absolute inset-0 border-2 border-brand-accent/20 rounded-full"
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
        />
        {/* Active arc */}
        <motion.div
          className="absolute inset-0 border-2 border-transparent border-t-brand-accent rounded-full"
          animate={{ rotate: 360 }}
          transition={{ duration: 0.75, repeat: Infinity, ease: 'linear' }}
        />
      </div>
      {text && (
        <p className="text-xs text-muted font-medium tracking-wide">
          {text}
        </p>
      )}
    </div>
  );
}

export function PageLoader({ text = 'Initializing Automio...' }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-surface-main">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="flex flex-col items-center gap-5 text-center"
      >
        <LogoSymbol size={44} className="animate-pulse" />
        <LoadingSpinner size="md" text={text} />
      </motion.div>
    </div>
  );
}

export function CardLoader({ text = 'Loading data...' }) {
  return (
    <div className="flex items-center justify-center p-12">
      <LoadingSpinner size="md" text={text} />
    </div>
  );
}
