import React from 'react';
import { motion } from 'framer-motion';
import { Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

/**
 * Standardized Automio Interactive Button Component
 * Supports keyboard accessibility, loading state, visual variants and icon alignment.
 */
const Button = React.forwardRef(({
  className,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  leftIcon: LeftIcon,
  rightIcon: RightIcon,
  children,
  type = 'button',
  disabled,
  ...props
}, ref) => {
  const variants = {
    primary: "btn-starlight text-white font-semibold",
    secondary: "bg-white/[0.06] hover:bg-white/[0.1] text-primary border border-white/15 hover:border-white/25 backdrop-blur-xl shadow-[0_4px_16px_rgba(0,0,0,0.3)]",
    outline: "border border-white/15 hover:border-sky-400/50 hover:bg-sky-500/[0.08] text-secondary hover:text-white backdrop-blur-md transition-all shadow-[0_0_15px_rgba(14,165,233,0)] hover:shadow-[0_0_15px_rgba(14,165,233,0.15)]",
    ghost: "btn-ghost-glow text-secondary hover:text-primary",
    danger: "bg-rose-500/10 text-rose-300 border border-rose-500/30 hover:bg-rose-500/20 hover:border-rose-500/50 hover:shadow-[0_0_15px_rgba(244,63,94,0.2)] backdrop-blur-md",
    success: "bg-emerald-500/10 text-emerald-300 border border-emerald-500/30 hover:bg-emerald-500/20 hover:border-emerald-500/50 hover:shadow-[0_0_15px_rgba(16,185,129,0.2)] backdrop-blur-md",
    link: "text-brand-accent hover:underline p-0 h-auto font-normal bg-transparent border-0",
  };

  const sizes = {
    sm: "px-3 py-1.5 text-xs rounded-lg gap-1.5",
    md: "px-4 py-2 text-sm rounded-xl gap-2",
    lg: "px-6 py-3 text-base rounded-xl gap-2.5",
    icon: "p-2.5 rounded-xl aspect-square",
  };

  const isDisabled = disabled || isLoading;
  const Component = props.onClick ? motion.button : 'button';
  const motionProps = props.onClick && !isDisabled ? {
    whileHover: { scale: 1.015 },
    whileTap: { scale: 0.985 },
  } : {};

  return (
    <Component
      ref={ref}
      type={type}
      aria-busy={isLoading}
      disabled={isDisabled}
      className={cn(
        "inline-flex items-center justify-center font-medium transition-all duration-200 select-none",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-accent/50 focus-visible:ring-offset-1 focus-visible:ring-offset-surface-main",
        "disabled:opacity-40 disabled:cursor-not-allowed disabled:pointer-events-none",
        variants[variant] || variants.primary,
        sizes[size] || sizes.md,
        className
      )}
      {...motionProps}
      {...props}
    >
      {isLoading ? (
        <Loader2 className="w-4 h-4 animate-spin text-current flex-shrink-0" aria-hidden="true" />
      ) : (
        LeftIcon && <LeftIcon className={cn("w-4 h-4 flex-shrink-0", size === 'lg' && "w-5 h-5")} aria-hidden="true" />
      )}
      {children}
      {!isLoading && RightIcon && (
        <RightIcon className={cn("w-4 h-4 flex-shrink-0", size === 'lg' && "w-5 h-5")} aria-hidden="true" />
      )}
    </Component>
  );
});

Button.displayName = "Button";

export default Button;
