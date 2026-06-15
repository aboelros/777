import { motion } from 'framer-motion';
import { Info, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';

export default function Alert({ type = 'info', title, message, onClose, className = '' }) {
    const config = {
        info: {
            icon: Info,
            bg: 'bg-blue-500/10',
            border: 'border-blue-500/30',
            text: 'text-blue-400',
            iconBg: 'bg-blue-500/20'
        },
        warning: {
            icon: AlertTriangle,
            bg: 'bg-yellow-500/10',
            border: 'border-yellow-500/30',
            text: 'text-yellow-400',
            iconBg: 'bg-yellow-500/20'
        },
        success: {
            icon: CheckCircle,
            bg: 'bg-green-500/10',
            border: 'border-green-500/30',
            text: 'text-green-400',
            iconBg: 'bg-green-500/20'
        },
        error: {
            icon: XCircle,
            bg: 'bg-red-500/10',
            border: 'border-red-500/30',
            text: 'text-red-400',
            iconBg: 'bg-red-500/20'
        }
    };

    const { icon: Icon, bg, border, text, iconBg } = config[type];

    return (
        <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className={`flex items-start gap-3 p-4 rounded-xl ${bg} border ${border} ${className}`}
        >
            <div className={`w-10 h-10 rounded-lg ${iconBg} flex items-center justify-center flex-shrink-0`}>
                <Icon className={`w-5 h-5 ${text}`} />
            </div>
            <div className="flex-1 min-w-0">
                {title && <h4 className={`font-semibold ${text} mb-1`}>{title}</h4>}
                <p className="text-sm text-gray-300">{message}</p>
            </div>
            {onClose && (
                <button
                    onClick={onClose}
                    className={`${text} hover:opacity-70 transition-opacity`}
                >
                    <XCircle className="w-5 h-5" />
                </button>
            )}
        </motion.div>
    );
}
