import React from 'react';
import { motion } from 'framer-motion';
import { Loader2 } from 'lucide-react';
import { cn } from '../../lib/utils';

const Button = React.forwardRef(({
    className,
    variant = 'primary',
    size = 'md',
    isLoading = false,
    leftIcon: LeftIcon,
    rightIcon: RightIcon,
    children,
    ...props
}, ref) => {

    const variants = {
        primary: "btn-starlight text-white",
        secondary: "glass-panel hover:bg-white/10 text-white border-white/10",
        ghost: "btn-ghost-glow",
        danger: "bg-red-500/10 text-red-400 border border-red-500/20 hover:bg-red-500/20 hover:text-red-300",
        success: "bg-green-500/10 text-green-400 border border-green-500/20 hover:bg-green-500/20 hover:text-green-300",
    };

    const sizes = {
        sm: "px-3 py-1.5 text-xs",
        md: "px-5 py-2.5 text-sm",
        lg: "px-8 py-4 text-base",
        icon: "p-2",
    };

    const Component = props.onClick ? motion.button : 'button';
    const motionProps = props.onClick ? {
        whileHover: { scale: 1.02 },
        whileTap: { scale: 0.98 },
    } : {};

    return (
        <Component
            ref={ref}
            className={cn(
                "inline-flex items-center justify-center gap-2 rounded-md font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed outline-none focus:ring-1 focus:ring-accent-500/50",
                variants[variant],
                sizes[size],
                className
            )}
            disabled={isLoading || props.disabled}
            {...motionProps}
            {...props}
        >
            {isLoading && <Loader2 className="w-4 h-4 animate-spin" />}
            {!isLoading && LeftIcon && <LeftIcon className={cn("w-4 h-4", size === 'lg' && "w-5 h-5")} />}
            {children}
            {!isLoading && RightIcon && <RightIcon className={cn("w-4 h-4", size === 'lg' && "w-5 h-5")} />}
        </Component>
    );
});

Button.displayName = "Button";

export default Button;
