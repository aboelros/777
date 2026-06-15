import { motion } from 'framer-motion';
import { cn } from '../lib/utils';

export default function GlassCard({
  children,
  className,
  hover = false,
  animate = true,
  pulse = false,
  ...props
}) {
  const Component = animate ? motion.div : 'div';

  const baseClass = hover ? 'glass-card' : 'glass-panel';
  const pulseClass = pulse ? 'animate-pulse ring-1 ring-accent-500/50' : '';

  const motionProps = animate ? {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.4, ease: "easeOut" }
  } : {};

  return (
    <Component
      className={cn(baseClass, pulseClass, className)}
      {...motionProps}
      {...props}
    >
      {/* Optional: Add gradient overlay for extra depth */}
      {!hover && <div className="absolute inset-0 bg-gradient-to-b from-white/5 to-transparent pointer-events-none" />}
      <div className="relative z-10">
        {children}
      </div>
    </Component>
  );
}
