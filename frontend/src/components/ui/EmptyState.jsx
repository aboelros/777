import { motion } from 'framer-motion';
import { Plus } from 'lucide-react';
import Button from './Button';

export default function EmptyState({
  icon: Icon,
  title,
  description,
  actionLabel,
  onAction,
  className = ''
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`text-center py-12 ${className}`}
    >
      <motion.div
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ delay: 0.2 }}
        className="w-20 h-20 bg-gradient-to-br from-accent-500/20 to-sky-600/20 rounded-2xl flex items-center justify-center mx-auto mb-6 border border-white/5 shadow-neon"
      >
        <Icon className="w-10 h-10 text-accent-400" />
      </motion.div>

      <h3 className="text-xl font-bold text-white mb-2 tracking-tight">{title}</h3>
      <p className="text-gray-400 mb-8 max-w-md mx-auto leading-relaxed">{description}</p>

      {actionLabel && onAction && (
        <Button
          onClick={onAction}
          variant="primary"
          leftIcon={Plus}
        >
          {actionLabel}
        </Button>
      )}
    </motion.div>
  );
}

export function DataEmptyState({
  title = "No data available",
  description = "There's nothing to show here yet.",
  className = ''
}) {
  return (
    <div className={`text-center py-8 ${className}`}>
      <div className="w-12 h-12 bg-gray-500/20 rounded-full flex items-center justify-center mx-auto mb-3">
        <div className="w-6 h-6 border-2 border-gray-500 border-dashed rounded"></div>
      </div>
      <h4 className="text-lg font-medium text-gray-300 mb-1">{title}</h4>
      <p className="text-sm text-gray-500">{description}</p>
    </div>
  );
}
