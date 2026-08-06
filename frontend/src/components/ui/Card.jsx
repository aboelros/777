import { motion } from 'framer-motion';

export default function Card({
  children,
  className = '',
  hover = true,
  glow = false,
  padding = 'p-6',
  delay = 0,
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay, ease: [0.25, 0.46, 0.45, 0.94] }}
      whileHover={hover ? { y: -2, transition: { duration: 0.2 } } : {}}
      whileTap={hover ? { scale: 0.995 } : {}}
      className={`
        ${padding}
        rounded-2xl 
        bg-white/[0.03]
        backdrop-blur-xl 
        border 
        border-white/[0.07]
        transition-all 
        duration-300
        ${hover ? 'hover:border-sky-500/25 hover:shadow-lg hover:shadow-sky-500/[0.06]' : ''}
        ${glow ? 'shadow-lg shadow-sky-500/15 border-sky-500/20' : ''}
        ${className}
      `}
    >
      {children}
    </motion.div>
  );
}
