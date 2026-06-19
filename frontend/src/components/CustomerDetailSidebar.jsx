import { motion } from 'framer-motion';
import {
    User,
    Mail,
    Phone,
    Calendar,
    Tag,
    ShoppingBag,
    Star,
    MoreVertical,
    Instagram,
    Facebook,
    MessageCircle,
    Shield,
    TrendingUp,
    Zap,
    ExternalLink
} from 'lucide-react';
import GlassCard from './GlassCard';
import { formatCurrency, formatDateTime } from '../utils/helpers';
import { cn } from '../lib/utils';

export default function CustomerDetailSidebar({ customer, onClose, onToggleAI }) {
    if (!customer) return null;

    const platform = customer.platform || 'messenger';
    const PlatformIcon = platform === 'instagram' ? Instagram : Facebook;

    return (
        <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            className="w-full lg:w-80 h-full overflow-y-auto custom-scrollbar border-l border-white/5 bg-slate-950/40 backdrop-blur-md p-4 space-y-6"
        >
            {/* Header */}
            <div className="flex flex-col items-center text-center space-y-4 pt-4">
                <div className="relative group">
                    <div className="absolute -inset-1 bg-gradient-to-r from-accent-500 to-sky-600 rounded-full blur opacity-25 group-hover:opacity-50 transition duration-1000 group-hover:duration-200"></div>
                    <div className="relative w-24 h-24 rounded-full border-2 border-white/10 overflow-hidden bg-slate-800">
                        {customer.avatar_url ? (
                            <img
                                src={customer.avatar_url}
                                alt={customer.name}
                                className="w-full h-full object-cover"
                            />
                        ) : (
                            <div className="w-full h-full flex items-center justify-center text-3xl font-bold bg-gradient-to-br from-slate-700 to-slate-900 text-slate-400">
                                {customer.name?.charAt(0)}
                            </div>
                        )}
                    </div>
                    {customer.is_vip && (
                        <div className="absolute -bottom-1 -right-1 p-1 bg-cyan-500 rounded-full border-2 border-slate-900 shadow-lg">
                            <Star className="w-4 h-4 text-white fill-white" />
                        </div>
                    )}
                </div>

                <div>
                    <h3 className="text-xl font-bold text-white flex items-center justify-center gap-2">
                        {customer.name}
                        <Shield className="w-4 h-4 text-accent-400" />
                    </h3>
                    <div className="flex items-center justify-center gap-2 mt-1 text-slate-400 text-sm">
                        <PlatformIcon className="w-4 h-4" />
                        <span>@{customer.platform_id || 'customer'}</span>
                    </div>
                </div>
            </div>

            {/* AI Insights Card */}
            <GlassCard className="p-4 bg-accent-500/5 border-accent-500/20">
                <div className="flex items-center gap-2 mb-3">
                    <Zap className="w-4 h-4 text-accent-400" />
                    <span className="text-xs font-bold uppercase tracking-wider text-accent-300">AI Intelligence</span>
                </div>

                <div className="space-y-3">
                    <div className="flex items-center justify-between">
                        <span className="text-xs text-slate-400">Customer Persona</span>
                        <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-accent-500/20 text-accent-300 border border-accent-500/30">
                            {customer.customer_type || 'Regular'}
                        </span>
                    </div>
                    <div className="flex items-center justify-between">
                        <span className="text-xs text-slate-400">Sentiment Pulse</span>
                        <div className="flex items-center gap-2">
                            <span className={cn(
                                "text-xs font-medium px-2 py-0.5 rounded-full capitalize",
                                customer.overall_sentiment === 'positive' ? 'bg-green-500/20 text-green-400 border-green-500/30' :
                                    customer.overall_sentiment === 'negative' ? 'bg-red-500/20 text-red-400 border-red-500/30' :
                                        'bg-slate-500/20 text-slate-400 border-slate-500/30'
                            )}>
                                {customer.overall_sentiment || 'Neutral'}
                            </span>
                        </div>
                    </div>
                    <div className="pt-2 border-t border-white/5 space-y-3">
                        <div className="flex items-center justify-between">
                            <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">AI Automation</span>
                            <button
                                onClick={onToggleAI}
                                className={cn(
                                    "px-2 py-1 rounded text-[9px] font-bold uppercase tracking-widest border transition-all",
                                    customer.ai_enabled
                                        ? "bg-sky-500/20 text-sky-400 border-sky-500/30 animate-pulse"
                                        : "bg-slate-500/10 text-slate-500 border-slate-500/20"
                                )}
                            >
                                {customer.ai_enabled ? 'Active' : 'Disabled'}
                            </button>
                        </div>
                        <p className="text-[10px] text-slate-500 leading-relaxed italic">
                            "{customer.notes || 'No recent insights available for this customer.'}"
                        </p>
                    </div>
                </div>
            </GlassCard>

            {/* Details Section */}
            <div className="space-y-4">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 px-1">Contact Details</h4>
                <div className="space-y-3 px-1">
                    <div className="flex items-center gap-3 text-sm text-slate-300">
                        <Mail className="w-4 h-4 text-slate-500" />
                        <span className="truncate">{customer.email || 'No email saved'}</span>
                    </div>
                    <div className="flex items-center gap-3 text-sm text-slate-300">
                        <Phone className="w-4 h-4 text-slate-500" />
                        <span>{customer.phone || 'No phone saved'}</span>
                    </div>
                    <div className="flex items-center gap-3 text-sm text-slate-300">
                        <Calendar className="w-4 h-4 text-slate-500" />
                        <span>Joined {formatDateTime(customer.created_at, 'date')}</span>
                    </div>
                </div>
            </div>

            {/* Commerce Summary */}
            <div className="space-y-4 pt-2">
                <div className="flex items-center justify-between px-1">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">Commerce</h4>
                    <TrendingUp className="w-4 h-4 text-green-500" />
                </div>
                <div className="grid grid-cols-2 gap-3">
                    <div className="bg-white/5 border border-white/5 rounded-xl p-3">
                        <p className="text-[10px] text-slate-500 uppercase mb-1">Orders</p>
                        <p className="text-lg font-bold text-white">{customer.total_orders || 0}</p>
                    </div>
                    <div className="bg-white/5 border border-white/5 rounded-xl p-3">
                        <p className="text-[10px] text-slate-500 uppercase mb-1">Spent</p>
                        <p className="text-lg font-bold text-white">{formatCurrency(customer.total_spent || 0)}</p>
                    </div>
                </div>
            </div>

            {/* Tags Section */}
            {customer.tags && customer.tags.length > 0 && (
                <div className="space-y-2">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 px-1">Tags</h4>
                    <div className="flex flex-wrap gap-2 px-1">
                        {customer.tags.map((tag, i) => (
                            <span
                                key={i}
                                className="text-[10px] bg-slate-800 text-slate-400 px-2 py-1 rounded-md border border-white/5"
                            >
                                {tag}
                            </span>
                        ))}
                    </div>
                </div>
            )}

            {/* Platform Debug/Info */}
            <div className="pt-6 border-t border-white/5">
                <div className="bg-black/20 rounded-lg p-3 space-y-2">
                    <div className="flex items-center justify-between text-[10px] font-mono">
                        <span className="text-slate-500 uppercase">Provider</span>
                        <span className="text-slate-300 capitalize">{platform}</span>
                    </div>
                    <div className="flex items-center justify-between text-[10px] font-mono">
                        <span className="text-slate-500 uppercase">Customer ID</span>
                        <span className="text-slate-300">{customer.customer_id?.substring(0, 16)}...</span>
                    </div>
                </div>
            </div>

            <button className="w-full flex items-center justify-center gap-2 py-3 bg-white/5 hover:bg-white/10 text-xs font-medium text-slate-300 rounded-xl border border-white/10 transition-colors mt-4 group">
                Account Settings
                <ExternalLink className="w-3 h-3 text-slate-500 group-hover:text-accent-400" />
            </button>
        </motion.div>
    );
}
