import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import { motion } from 'framer-motion';

export default function ApiErrorState({
    error,
    onRetry,
    title = 'Something went wrong',
    compact = false
}) {
    const getErrorMessage = () => {
        if (!error) return 'An unexpected error occurred';

        // Handle different error types
        if (error.response) {
            const status = error.response.status;

            switch (status) {
                case 401:
                    return 'Your session has expired. Please log in again.';
                case 403:
                    return 'You don\'t have permission to access this resource.';
                case 404:
                    return 'The requested resource was not found.';
                case 422:
                    return 'Invalid request format. Please try again.';
                case 500:
                    return 'Server error. Our team has been notified.';
                default:
                    return error.response.data?.message || 'An error occurred while loading data.';
            }
        }

        return error.message || 'Failed to load data. Please check your connection.';
    };

    if (compact) {
        return (
            <div className="flex items-center justify-center gap-3 p-4 rounded-xl bg-red-500/10 border border-red-500/20">
                <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0" />
                <p className="text-sm text-red-400">{getErrorMessage()}</p>
                {onRetry && (
                    <button
                        onClick={onRetry}
                        className="ml-auto px-3 py-1 text-xs font-medium text-red-400 hover:text-red-300 border border-red-500/30 rounded-lg hover:bg-red-500/10 transition-colors"
                    >
                        Retry
                    </button>
                )}
            </div>
        );
    }

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col items-center justify-center p-12 text-center"
        >
            <div className="w-16 h-16 rounded-2xl bg-red-500/10 border border-red-500/20 flex items-center justify-center mb-4">
                <AlertTriangle className="w-8 h-8 text-red-400" />
            </div>

            <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
            <p className="text-sm text-gray-400 max-w-md mb-6">{getErrorMessage()}</p>

            {onRetry && (
                <button
                    onClick={onRetry}
                    className="flex items-center gap-2 px-4 py-2 bg-violet-500/10 hover:bg-violet-500/20 border border-violet-500/30 text-violet-400 rounded-xl transition-colors"
                >
                    <RefreshCw className="w-4 h-4" />
                    <span className="font-medium">Try Again</span>
                </button>
            )}
        </motion.div>
    );
}
