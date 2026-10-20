import { motion } from 'framer-motion';
import { Bot, User, Sparkles, TrendingUp, Package, MessageCircle, BarChart3 } from 'lucide-react';
import { useTranslation } from '@/lib/translations';

const ICON_MAP = {
  TrendingUp,
  Package,
  MessageCircle,
  BarChart3,
  User,
};

export default function ChatMessageItem({ message, onQuickAction }) {
  const { t } = useTranslation();
  const isUser = message.role === 'user';

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
    >
      <div
        className={`w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 text-white ${
          isUser ? 'bg-sky-600' : 'bg-brand-primary'
        }`}
      >
        {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
      </div>

      <div className={`flex-1 max-w-[85%] ${isUser ? 'items-end' : 'items-start'} flex flex-col`}>
        <div
          className={`p-4 rounded-2xl text-sm leading-relaxed ${
            isUser
              ? 'bg-brand-primary text-white rounded-tr-sm shadow-sm'
              : 'glass-card border border-border bg-surface-subtle text-text-primary rounded-tl-sm'
          }`}
        >
          <p className="whitespace-pre-wrap">{message.content}</p>

          {message.suggestions && message.suggestions.length > 0 && (
            <div className="mt-4 pt-3 border-t border-border/50">
              <p className="text-[11px] font-semibold text-text-muted mb-2 flex items-center gap-1.5 uppercase tracking-wider">
                <Sparkles className="w-3.5 h-3.5 text-brand-primary" />
                {t('assistant.suggested_actions') || 'Suggested Actions'}
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {message.suggestions.map((suggestion, idx) => {
                  if (!suggestion || typeof suggestion !== 'object') return null;
                  const IconComponent = ICON_MAP[suggestion.icon] || Sparkles;
                  return (
                    <button
                      key={idx}
                      onClick={() => onQuickAction(suggestion.text)}
                      className="p-2.5 rounded-xl text-left bg-surface border border-border hover:border-brand-primary/40 hover:bg-surface-hover transition-all flex items-center gap-2 group"
                    >
                      <div className="w-6 h-6 rounded-lg bg-brand-primary/10 text-brand-primary flex items-center justify-center flex-shrink-0 group-hover:scale-105 transition-transform">
                        <IconComponent className="w-3.5 h-3.5" />
                      </div>
                      <span className="text-xs font-medium text-text-secondary group-hover:text-text-primary line-clamp-1">
                        {suggestion.text}
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {message.tokens && (
            <div className="flex items-center gap-2 mt-3 pt-2 border-t border-border/40 text-[10px] font-mono text-text-muted">
              <span>{message.tokens} tokens</span>
              <span>•</span>
              <span>${message.cost?.toFixed(5) || '0.00'}</span>
            </div>
          )}
        </div>
        <span className="text-[11px] text-text-muted mt-1 px-1 font-mono">
          {message.timestamp?.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </span>
      </div>
    </motion.div>
  );
}
