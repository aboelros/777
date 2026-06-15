import React from 'react';
import { motion } from 'framer-motion';

export default function SkeletonLoader({ type = 'card', count = 1, className = '' }) {
    const renderSkeleton = () => {
        switch (type) {
            case 'card':
                return (
                    <div className={`p-6 rounded-2xl bg-white/5 border border-white/10 ${className}`}>
                        <div className="flex items-start justify-between mb-4">
                            <div className="w-12 h-12 rounded-xl bg-white/10 animate-pulse" />
                            <div className="w-16 h-6 rounded-lg bg-white/10 animate-pulse" />
                        </div>
                        <div className="space-y-3">
                            <div className="h-4 bg-white/10 rounded animate-pulse w-1/3" />
                            <div className="h-8 bg-white/10 rounded animate-pulse w-2/3" />
                            <div className="h-3 bg-white/10 rounded animate-pulse w-1/2" />
                        </div>
                    </div>
                );

            case 'table-row':
                return (
                    <div className={`flex items-center gap-4 p-4 ${className}`}>
                        <div className="w-10 h-10 rounded-lg bg-white/10 animate-pulse" />
                        <div className="flex-1 space-y-2">
                            <div className="h-4 bg-white/10 rounded animate-pulse w-1/4" />
                            <div className="h-3 bg-white/10 rounded animate-pulse w-1/3" />
                        </div>
                        <div className="w-20 h-6 rounded-lg bg-white/10 animate-pulse" />
                    </div>
                );

            case 'chart':
                return (
                    <div className={`p-8 rounded-2xl bg-white/5 border border-white/10 ${className}`}>
                        <div className="flex items-center justify-between mb-6">
                            <div className="space-y-2">
                                <div className="h-5 bg-white/10 rounded animate-pulse w-32" />
                                <div className="h-3 bg-white/10 rounded animate-pulse w-24" />
                            </div>
                            <div className="w-10 h-10 rounded-lg bg-white/10 animate-pulse" />
                        </div>
                        <div className="h-[300px] bg-white/5 rounded-xl animate-pulse" />
                    </div>
                );

            case 'text':
                return (
                    <div className={`space-y-2 ${className}`}>
                        <div className="h-4 bg-white/10 rounded animate-pulse w-full" />
                        <div className="h-4 bg-white/10 rounded animate-pulse w-5/6" />
                        <div className="h-4 bg-white/10 rounded animate-pulse w-4/6" />
                    </div>
                );

            default:
                return (
                    <div className={`h-20 bg-white/10 rounded-xl animate-pulse ${className}`} />
                );
        }
    };

    return (
        <>
            {Array.from({ length: count }).map((_, index) => (
                <motion.div
                    key={index}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: index * 0.1 }}
                >
                    {renderSkeleton()}
                </motion.div>
            ))}
        </>
    );
}
