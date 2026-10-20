import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Bot } from 'lucide-react';
import { useTranslation } from '@/lib/translations';

export const ThinkingStep = ({ text, delay }) => {
  const [show, setShow] = useState(false);
  const [completed, setCompleted] = useState(false);

  useEffect(() => {
    const showTimer = setTimeout(() => setShow(true), delay);
    const completeTimer = setTimeout(() => setCompleted(true), delay + 1500);
    return () => {
      clearTimeout(showTimer);
      clearTimeout(completeTimer);
    };
  }, [delay]);

  if (!show) return null;

  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      className="flex items-center gap-2 text-xs text-text-muted"
    >
      {completed ? (
        <div className="w-3.5 h-3.5 rounded-full bg-emerald-500/20 flex items-center justify-center">
          <div className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
        </div>
      ) : (
        <div className="w-3.5 h-3.5 rounded-full border border-brand-primary/30 border-t-brand-primary animate-spin" />
      )}
      <span className={completed ? 'text-text-muted line-through' : 'text-text-secondary'}>
        {text}
      </span>
    </motion.div>
  );
};

export default function ThinkingEngine() {
  const { t } = useTranslation();

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="flex gap-3 max-w-[80%]"
    >
      <div className="w-8 h-8 rounded-xl bg-brand-primary/20 border border-brand-primary/30 flex items-center justify-center flex-shrink-0 text-brand-primary">
        <Bot className="w-4 h-4 animate-pulse" />
      </div>
      <div className="glass-card p-4 rounded-2xl border border-brand-primary/30 bg-surface-subtle w-full space-y-2">
        <div className="flex items-center gap-2 mb-2">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand-primary opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-brand-primary"></span>
          </span>
          <span className="text-[11px] font-bold text-brand-primary uppercase tracking-wider">
            {t('assistant.reasoning_engine') || 'Reasoning Engine Active'}
          </span>
        </div>

        <ThinkingStep text={t('assistant.steps.analyzing') || 'Synthesizing context and business intent...'} delay={0} />
        <ThinkingStep text={t('assistant.steps.context') || 'Retrieving real-time customer and catalog state...'} delay={800} />
        <ThinkingStep text={t('assistant.steps.formulating') || 'Drafting precise response recommendations...'} delay={1600} />
      </div>
    </motion.div>
  );
}
