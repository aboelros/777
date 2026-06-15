import { motion } from 'framer-motion';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function ErrorFallback({ error, resetErrorBoundary }) {
  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-md w-full text-center"
      >
        <div className="glass-card p-8 rounded-2xl">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2 }}
            className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-4"
          >
            <AlertTriangle className="w-8 h-8 text-red-400" />
          </motion.div>
          
          <h2 className="text-2xl font-bold text-white mb-2">Something went wrong</h2>
          <p className="text-gray-400 mb-6">
            We encountered an unexpected error. Please try refreshing the page or go back to the dashboard.
          </p>
          
          {process.env.NODE_ENV === 'development' && (
            <details className="mb-6 text-left">
              <summary className="cursor-pointer text-sm text-gray-500 hover:text-gray-400">
                Error Details (Development)
              </summary>
              <pre className="mt-2 p-3 bg-red-900/20 rounded text-xs text-red-300 overflow-auto">
                {error.message}
              </pre>
            </details>
          )}
          
          <div className="flex gap-3">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={resetErrorBoundary}
              className="flex-1 btn-neon flex items-center justify-center gap-2"
            >
              <RefreshCw className="w-4 h-4" />
              Try Again
            </motion.button>
            
            <Link
              to="/"
              className="flex-1 glass-card px-4 py-2 rounded-xl hover:bg-white/10 transition-colors flex items-center justify-center gap-2"
            >
              <Home className="w-4 h-4" />
              Dashboard
            </Link>
          </div>
        </div>
      </motion.div>
    </div>
  );
}

export function InlineError({ error, onRetry, className = '' }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`glass-card p-4 rounded-xl border border-red-500/20 ${className}`}
    >
      <div className="flex items-center gap-3">
        <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0" />
        <div className="flex-1">
          <p className="text-sm text-red-300 font-medium">Error loading data</p>
          <p className="text-xs text-gray-400 mt-1">
            {error?.message || 'Something went wrong'}
          </p>
        </div>
        {onRetry && (
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onRetry}
            className="px-3 py-1 bg-red-500/20 text-red-300 rounded-lg text-xs hover:bg-red-500/30 transition-colors"
          >
            Retry
          </motion.button>
        )}
      </div>
    </motion.div>
  );
}
