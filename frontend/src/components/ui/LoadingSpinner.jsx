import { motion } from 'framer-motion';

export default function LoadingSpinner({ size = 'md', text = 'Loading...', className = '' }) {
  const sizeClasses = {
    sm: 'w-5 h-5',
    md: 'w-10 h-10',
    lg: 'w-14 h-14',
    xl: 'w-20 h-20'
  };

  const ringSize = {
    sm: 'w-5 h-5',
    md: 'w-10 h-10',
    lg: 'w-14 h-14',
    xl: 'w-20 h-20'
  };

  return (
    <div className={`flex flex-col items-center justify-center gap-4 ${className}`}>
      <div className={`relative ${sizeClasses[size]}`}>
        {/* Outer ring - slow rotation */}
        <motion.div
          className={`absolute inset-0 ${ringSize[size]} border-2 border-sky-500/10 rounded-full`}
          animate={{ rotate: 360 }}
          transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
        />
        {/* Inner ring - fast rotation */}
        <motion.div
          className={`absolute inset-0 ${ringSize[size]} border-2 border-transparent border-t-sky-400 border-r-sky-400/50 rounded-full`}
          animate={{ rotate: 360 }}
          transition={{ duration: 0.8, repeat: Infinity, ease: 'linear' }}
        />
        {/* Center glow dot */}
        <motion.div
          className="absolute inset-0 flex items-center justify-center"
          animate={{ scale: [1, 1.2, 1], opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
        >
          <div className="w-1.5 h-1.5 rounded-full bg-sky-400 shadow-[0_0_10px_rgba(14,165,233,0.6)]" />
        </motion.div>
      </div>
      {text && (
        <motion.p
          initial={{ opacity: 0, y: 5 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="text-sm text-slate-400 font-medium tracking-wide"
        >
          {text}
        </motion.p>
      )}
    </div>
  );
}

export function PageLoader({ text = 'Loading...' }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-[rgb(2,6,23)]">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="text-center"
      >
        <LoadingSpinner size="xl" text={text} />
      </motion.div>
    </div>
  );
}

export function CardLoader({ text = 'Loading...' }) {
  return (
    <div className="flex items-center justify-center p-12">
      <LoadingSpinner size="lg" text={text} />
    </div>
  );
}
