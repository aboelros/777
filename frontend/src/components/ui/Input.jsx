import React from 'react';
import { cn } from '../../lib/utils';
import { motion } from 'framer-motion';

const Input = React.forwardRef(({
    className,
    label,
    error,
    icon: Icon,
    containerClassName,
    ...props
}, ref) => {
    return (
        <div className={cn("space-y-1.5", containerClassName)}>
            {label && (
                <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider ml-1">
                    {label}
                </label>
            )}
            <div className="relative group">
                {Icon && (
                    <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 group-focus-within:text-accent-400 transition-colors">
                        <Icon className="w-5 h-5" />
                    </div>
                )}
                <input
                    ref={ref}
                    className={cn(
                        "input-fluid w-full",
                        Icon && "pl-10",
                        error && "border-red-500/50 focus:border-red-500 focus:ring-red-500/20",
                        className
                    )}
                    {...props}
                />
                {/* Glow effect on focus */}
                <div className="absolute inset-0 rounded-xl bg-accent-500/20 opacity-0 group-focus-within:opacity-100 blur-xl -z-10 transition-opacity duration-300 pointer-events-none" />
            </div>
            {error && (
                <motion.p
                    initial={{ opacity: 0, y: -5 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-xs text-red-400 ml-1"
                >
                    {error}
                </motion.p>
            )}
        </div>
    );
});

Input.displayName = "Input";

export default Input;
