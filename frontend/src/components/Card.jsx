import { motion } from 'framer-motion';

export default function Card({
    children,
    className = '',
    hover = true,
    glow = false,
    padding = 'p-6'
}) {
    return (
        <motion.div
            whileHover={hover ? { y: -2 } : {}}
            className={`
        ${padding}
        rounded-2xl 
        bg-white/5 
        backdrop-blur-xl 
        border 
        border-white/10 
        transition-all 
        duration-300
        ${hover ? 'hover:border-cyan-500/30 hover:shadow-lg hover:shadow-cyan-500/10' : ''}
        ${glow ? 'shadow-lg shadow-cyan-500/20' : ''}
        ${className}
      `}
        >
            {children}
        </motion.div>
    );
}
