import React from 'react';
import { motion } from 'framer-motion';
import { Info, AlertTriangle, CheckCircle2, XCircle, X } from 'lucide-react';
import { cn } from '@/lib/utils';

/**
 * Standardized Automio Feedback Alert Banner
 */
export default function Alert({
  type = 'info',
  title,
  message,
  children,
  onClose,
  className = ''
}) {
  const config = {
    info: {
      icon: Info,
      bg: 'bg-status-info/10',
      border: 'border-status-info/25',
      text: 'text-sky-400',
      iconBg: 'bg-status-info/20'
    },
    warning: {
      icon: AlertTriangle,
      bg: 'bg-status-warning/10',
      border: 'border-status-warning/25',
      text: 'text-amber-400',
      iconBg: 'bg-status-warning/20'
    },
    success: {
      icon: CheckCircle2,
      bg: 'bg-status-success/10',
      border: 'border-status-success/25',
      text: 'text-emerald-400',
      iconBg: 'bg-status-success/20'
    },
    error: {
      icon: XCircle,
      bg: 'bg-status-danger/10',
      border: 'border-status-danger/25',
      text: 'text-red-400',
      iconBg: 'bg-status-danger/20'
    }
  };

  const { icon: Icon, bg, border, text, iconBg } = config[type] || config.info;

  return (
    <motion.div
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      role="alert"
      className={cn('flex items-start gap-3.5 p-4 rounded-xl border', bg, border, className)}
    >
      <div className={cn('w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0', iconBg)}>
        <Icon className={cn('w-5 h-5', text)} aria-hidden="true" />
      </div>
      <div className="flex-1 min-w-0 pt-0.5">
        {title && <h4 className={cn('font-semibold text-sm mb-1', text)}>{title}</h4>}
        <div className="text-sm text-secondary leading-relaxed">
          {message || children}
        </div>
      </div>
      {onClose && (
        <button
          onClick={onClose}
          aria-label="Close notification"
          className={cn('p-1 rounded-md text-muted hover:text-primary hover:bg-white/5 transition-colors', text)}
        >
          <X className="w-4 h-4" />
        </button>
      )}
    </motion.div>
  );
}
