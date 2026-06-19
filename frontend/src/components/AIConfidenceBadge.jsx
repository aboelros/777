/**
 * AI Confidence Badge Component
 * Displays confidence score and breakdown for AI responses.
 */
import { motion } from 'framer-motion';
import { Brain, CheckCircle, AlertTriangle, XCircle, Info } from 'lucide-react';
import { useState } from 'react';
import { useTranslation } from '../lib/translations';

export default function AIConfidenceBadge({ confidence }) {
    const [showBreakdown, setShowBreakdown] = useState(false);
    const { t } = useTranslation();

    if (!confidence) return null;

    const { overall, breakdown, level, threshold_met } = confidence;
    const percentage = Math.round(overall * 100);

    // Determine color and icon based on confidence level
    const getConfidenceStyle = () => {
        if (level === 'VERY_HIGH') {
            return {
                color: 'from-green-500 to-emerald-600',
                textColor: 'text-green-400',
                bgColor: 'bg-green-500/10',
                icon: CheckCircle
            };
        } else if (level === 'HIGH') {
            return {
                color: 'from-blue-500 to-cyan-600',
                textColor: 'text-blue-400',
                bgColor: 'bg-blue-500/10',
                icon: CheckCircle
            };
        } else if (level === 'MEDIUM') {
            return {
                color: 'from-yellow-500 to-orange-600',
                textColor: 'text-yellow-400',
                bgColor: 'bg-yellow-500/10',
                icon: AlertTriangle
            };
        } else {
            return {
                color: 'from-red-500 to-rose-600',
                textColor: 'text-red-400',
                bgColor: 'bg-red-500/10',
                icon: XCircle
            };
        }
    };

    const style = getConfidenceStyle();
    const Icon = style.icon;

    return (
        <div className="relative">
            <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-lg ${style.bgColor} border border-white/10 cursor-pointer`}
                onClick={() => setShowBreakdown(!showBreakdown)}
            >
                <Brain className={`w-4 h-4 ${style.textColor}`} />
                <span className={`text-sm font-medium ${style.textColor}`}>
                    {percentage}% {t('inbox.chat.intelligence')}
                </span>
                <Icon className={`w-3 h-3 ${style.textColor}`} />
            </motion.div>

            {/* Breakdown Tooltip */}
            {showBreakdown && (
                <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="absolute top-full left-0 mt-2 w-64 glass-card p-4 rounded-xl border border-white/10 z-50"
                >
                    <div className="flex items-center gap-2 mb-3">
                        <Info className="w-4 h-4 text-sky-400" />
                        <h4 className="text-sm font-semibold">{t('reports.insights.title')}</h4>
                    </div>

                    <div className="space-y-2">
                        {Object.entries(breakdown).map(([key, value]) => (
                            <div key={key} className="flex items-center justify-between">
                                <span className="text-xs text-gray-400 capitalize">
                                    {key.replace(/_/g, ' ')}
                                </span>
                                <div className="flex items-center gap-2">
                                    <div className="w-16 h-1.5 bg-dark-800 rounded-full overflow-hidden">
                                        <div
                                            className={`h-full bg-gradient-to-r ${style.color}`}
                                            style={{ width: `${value * 100}%` }}
                                        />
                                    </div>
                                    <span className="text-xs font-medium w-10 text-right">
                                        {Math.round(value * 100)}%
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>

                    {!threshold_met && (
                        <div className="mt-3 pt-3 border-t border-white/10">
                            <p className="text-xs text-yellow-400 flex items-center gap-1">
                                <AlertTriangle className="w-3 h-3" />
                                {t('common.error')}
                            </p>
                        </div>
                    )}
                </motion.div>
            )}
        </div>
    );
}
