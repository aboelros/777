import React, { useId } from 'react';
import { cn } from '@/lib/utils';
import { motion } from 'framer-motion';

/**
 * Standardized Automio Form Input Field
 * Accessible, keyboard friendly with label, icon, helper text and error state.
 */
const Input = React.forwardRef(({
  className,
  label,
  error,
  helperText,
  icon: Icon,
  containerClassName,
  id: explicitId,
  required,
  ...props
}, ref) => {
  const generatedId = useId();
  const inputId = explicitId || generatedId;
  const errorId = `${inputId}-error`;
  const helperId = `${inputId}-helper`;

  return (
    <div className={cn("space-y-1.5", containerClassName)}>
      {label && (
        <label
          htmlFor={inputId}
          className="block text-xs font-semibold text-secondary uppercase tracking-wider ml-0.5"
        >
          {label}
          {required && <span className="text-status-danger ml-1" aria-hidden="true">*</span>}
        </label>
      )}
      <div className="relative group">
        {Icon && (
          <div
            className="absolute left-3.5 top-1/2 -translate-y-1/2 text-muted group-focus-within:text-brand-accent transition-colors pointer-events-none"
            aria-hidden="true"
          >
            <Icon className="w-4 h-4" />
          </div>
        )}
        <input
          id={inputId}
          ref={ref}
          aria-invalid={!!error}
          aria-describedby={error ? errorId : helperText ? helperId : undefined}
          required={required}
          className={cn(
            "input-fluid w-full text-sm",
            Icon && "pl-10",
            error && "border-status-danger/60 focus:border-status-danger focus:ring-status-danger/20",
            className
          )}
          {...props}
        />
      </div>
      {error && (
        <motion.p
          id={errorId}
          initial={{ opacity: 0, y: -4 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-xs text-status-danger font-medium ml-0.5"
          role="alert"
        >
          {error}
        </motion.p>
      )}
      {!error && helperText && (
        <p id={helperId} className="text-xs text-muted ml-0.5">
          {helperText}
        </p>
      )}
    </div>
  );
});

Input.displayName = "Input";

export default Input;
