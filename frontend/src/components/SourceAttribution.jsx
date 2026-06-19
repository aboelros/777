/**
 * Source Attribution Component
 * Displays sources used for AI responses.
 */
import { motion, AnimatePresence } from 'framer-motion';
import { FileText, Globe, BookOpen, ExternalLink, ChevronDown, ChevronUp } from 'lucide-react';
import { useState } from 'react';

export default function SourceAttribution({ sources, attribution }) {
    const [expanded, setExpanded] = useState(false);

    if (!sources || !attribution || attribution.primary_sources.length === 0) {
        return null;
    }

    const { primary_sources, citation_count, source_types, attribution_confidence } = attribution;

    const getSourceIcon = (type) => {
        switch (type) {
            case 'web':
                return Globe;
            case 'document':
                return FileText;
            default:
                return BookOpen;
        }
    };

    return (
        <div className="mt-4 glass-card p-4 rounded-xl border border-white/10">
            <div
                className="flex items-center justify-between cursor-pointer"
                onClick={() => setExpanded(!expanded)}
            >
                <div className="flex items-center gap-2">
                    <BookOpen className="w-4 h-4 text-sky-400" />
                    <span className="text-sm font-medium">
                        {citation_count} Source{citation_count !== 1 ? 's' : ''} Used
                    </span>
                    <span className="text-xs text-gray-400">
                        ({Math.round(attribution_confidence * 100)}% relevance)
                    </span>
                </div>
                {expanded ? (
                    <ChevronUp className="w-4 h-4 text-gray-400" />
                ) : (
                    <ChevronDown className="w-4 h-4 text-gray-400" />
                )}
            </div>

            <AnimatePresence>
                {expanded && (
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="mt-4 space-y-3"
                    >
                        {primary_sources.map((source, index) => {
                            const Icon = getSourceIcon(source.type);

                            return (
                                <motion.div
                                    key={source.document_id}
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: index * 0.1 }}
                                    className="p-3 bg-dark-800/50 rounded-lg border border-white/5"
                                >
                                    <div className="flex items-start gap-3">
                                        <div className="w-8 h-8 rounded-lg bg-sky-500/10 flex items-center justify-center flex-shrink-0">
                                            <Icon className="w-4 h-4 text-sky-400" />
                                        </div>

                                        <div className="flex-1 min-w-0">
                                            <div className="flex items-center justify-between mb-1">
                                                <h4 className="text-sm font-medium truncate">
                                                    {source.document_name}
                                                </h4>
                                                <span className="text-xs text-gray-400 ml-2">
                                                    {Math.round(source.relevance_score * 100)}%
                                                </span>
                                            </div>

                                            {source.excerpt && (
                                                <p className="text-xs text-gray-400 line-clamp-2 mb-2">
                                                    {source.excerpt}
                                                </p>
                                            )}

                                            <div className="flex items-center gap-2">
                                                <span className="text-xs px-2 py-0.5 rounded bg-white/5 text-gray-400">
                                                    {source.type}
                                                </span>

                                                {source.url && (
                                                    <a
                                                        href={source.url}
                                                        target="_blank"
                                                        rel="noopener noreferrer"
                                                        className="text-xs text-sky-400 hover:text-sky-300 flex items-center gap-1 transition-colors"
                                                    >
                                                        View Source
                                                        <ExternalLink className="w-3 h-3" />
                                                    </a>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                </motion.div>
                            );
                        })}

                        {/* Source Type Summary */}
                        <div className="pt-3 border-t border-white/5">
                            <div className="flex items-center gap-2 flex-wrap">
                                <span className="text-xs text-gray-400">Source Types:</span>
                                {Object.entries(source_types).map(([type, count]) => (
                                    <span key={type} className="text-xs px-2 py-1 rounded bg-sky-500/10 text-sky-400">
                                        {type}: {count}
                                    </span>
                                ))}
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
