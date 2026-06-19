import { motion } from 'framer-motion';
import { cn } from '../lib/utils';

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

  const pulseClass = pulse ? 'neon-glow-pulse ring-1 ring-sky-500/30' : '';
  const glowClass = glow ? 'neon-glow' : '';

  const motionProps = animate ? {
    initial: { opacity: 0, y: 16, scale: 0.98 },
    animate: { opacity: 1, y: 0, scale: 1 },
    transition: {
      duration: 0.45,
      delay,
      ease: [0.25, 0.46, 0.45, 0.94]
    },
    whileHover: hover ? { y: -3, transition: { duration: 0.25 } } : {},
  } : {};

  return (
    <Component
      className={cn('glass-card', pulseClass, glowClass, className)}
      {...motionProps}
      {...props}
    >
      {/* Top edge light reflection */}
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent pointer-events-none" />
      {/* Content */}
      <div className="relative z-10">
        {children}
      </div>
    </Component>
  );
}
