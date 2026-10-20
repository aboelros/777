import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

/**
 * Standardized Automio Shimmer Skeleton Loader
 */
export default function SkeletonLoader({ type = 'card', count = 1, className = '' }) {
  const renderSkeleton = () => {
    switch (type) {
      case 'card':
        return (
          <div className={cn("p-6 rounded-2xl bg-surface-card border border-border/50", className)}>
            <div className="flex items-start justify-between mb-4">
              <div className="w-10 h-10 rounded-xl skeleton-shimmer" />
              <div className="w-16 h-5 rounded-lg skeleton-shimmer" />
            </div>
            <div className="space-y-3">
              <div className="h-4 skeleton-shimmer w-1/3" />
              <div className="h-7 skeleton-shimmer w-2/3" />
              <div className="h-3 skeleton-shimmer w-1/2" />
            </div>
          </div>
        );

      case 'table-row':
        return (
          <div className={cn("flex items-center gap-4 p-4 rounded-xl border border-border/30 bg-surface-card/40", className)}>
            <div className="w-9 h-9 rounded-lg skeleton-shimmer flex-shrink-0" />
            <div className="flex-1 space-y-2">
              <div className="h-4 skeleton-shimmer w-1/4" />
              <div className="h-3 skeleton-shimmer w-1/3" />
            </div>
            <div className="w-20 h-6 rounded-lg skeleton-shimmer" />
          </div>
        );

      case 'chart':
        return (
          <div className={cn("p-6 rounded-2xl bg-surface-card border border-border/50", className)}>
            <div className="flex items-center justify-between mb-6">
              <div className="space-y-2">
                <div className="h-5 skeleton-shimmer w-32" />
                <div className="h-3 skeleton-shimmer w-24" />
              </div>
              <div className="w-8 h-8 rounded-lg skeleton-shimmer" />
            </div>
            <div className="h-[260px] skeleton-shimmer rounded-xl" />
          </div>
        );

      case 'text':
        return (
          <div className={cn("space-y-2.5", className)}>
            <div className="h-4 skeleton-shimmer w-full" />
            <div className="h-4 skeleton-shimmer w-5/6" />
            <div className="h-4 skeleton-shimmer w-4/6" />
          </div>
        );

      default:
        return (
          <div className={cn("h-16 skeleton-shimmer rounded-xl", className)} />
        );
    }
  };

  return (
    <div className="space-y-4 w-full">
      {Array.from({ length: count }).map((_, index) => (
        <motion.div
          key={index}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: index * 0.08 }}
        >
          {renderSkeleton()}
        </motion.div>
      ))}
    </div>
  );
}
