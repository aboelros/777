import React from 'react';
import { motion } from 'framer-motion';
import { Plus, FolderKanban, Inbox } from 'lucide-react';
import Button from './Button';
import { cn } from '@/lib/utils';

/**
 * Standardized Automio Empty State Component
 */
export default function EmptyState({
  icon: Icon = Inbox,
  title = "No items found",
  description = "Get started by creating your first entry.",
  actionLabel,
  onAction,
  secondaryActionLabel,
  onSecondaryAction,
  className = '',
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={cn('text-center py-12 px-4 max-w-lg mx-auto flex flex-col items-center justify-center', className)}
    >
      <div className="w-16 h-16 rounded-2xl bg-surface-subtle border border-border/50 flex items-center justify-center mb-5 shadow-surface-sm text-brand-accent">
        <Icon className="w-8 h-8" aria-hidden="true" />
      </div>

      <h3 className="text-xl font-bold text-primary mb-2 tracking-tight">{title}</h3>
      <p className="text-sm text-secondary mb-6 leading-relaxed text-center">{description}</p>

      <div className="flex flex-wrap items-center justify-center gap-3">
        {actionLabel && onAction && (
          <Button
            onClick={onAction}
            variant="primary"
            leftIcon={Plus}
          >
            {actionLabel}
          </Button>
        )}
        {secondaryActionLabel && onSecondaryAction && (
          <Button
            onClick={onSecondaryAction}
            variant="secondary"
          >
            {secondaryActionLabel}
          </Button>
        )}
      </div>
    </motion.div>
  );
}

/**
 * Standardized Empty State for when no project workspace is active
 */
export function NoProjectState({
  title = "No Project Selected",
  description = "Please select or create a project workspace to manage data and automations.",
  onCreateProject,
  className = '',
}) {
  return (
    <div className={cn("min-h-[400px] flex items-center justify-center p-8", className)}>
      <EmptyState
        icon={FolderKanban}
        title={title}
        description={description}
        actionLabel={onCreateProject ? "Create Project" : undefined}
        onAction={onCreateProject}
      />
    </div>
  );
}

export function DataEmptyState({
  title = "No data available",
  description = "There's nothing to display in this view yet.",
  className = ''
}) {
  return (
    <div className={cn('text-center py-8 px-4', className)}>
      <div className="w-12 h-12 rounded-xl bg-surface-subtle border border-border/40 flex items-center justify-center mx-auto mb-3 text-muted">
        <Inbox className="w-6 h-6" />
      </div>
      <h4 className="text-base font-semibold text-primary mb-1">{title}</h4>
      <p className="text-xs text-muted max-w-sm mx-auto">{description}</p>
    </div>
  );
}

export { EmptyState };

