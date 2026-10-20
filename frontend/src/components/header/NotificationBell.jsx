import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Bell } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useProjectStore } from '@/store/projectStore';
import { useTranslation } from '@/lib/translations';
import api from '@/services/api';

/**
 * Automind Notification Bell & Intelligence Updates Flyout
 */
export default function NotificationBell() {
  const [isOpen, setIsOpen] = useState(false);
  const { currentProject } = useProjectStore();
  const navigate = useNavigate();
  const { t } = useTranslation();

  const { data: messageStats } = useQuery({
    queryKey: ['message-stats', currentProject?.id],
    queryFn: async () => {
      if (!currentProject?.id) return null;
      return await api.messages.stats(currentProject.id);
    },
    enabled: !!currentProject?.id,
    refetchInterval: 30000,
  });

  const unreadCount = messageStats?.unread_messages || 0;

  return (
    <div className="relative">
      <motion.button
        type="button"
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Open notifications"
        aria-expanded={isOpen}
        className={`relative w-9 h-9 rounded-xl flex items-center justify-center transition-colors border ${
          isOpen
            ? 'bg-brand-primary/20 text-brand-accent border-brand-accent/40'
            : 'bg-surface-card/60 text-secondary hover:text-primary hover:bg-surface-hover border-border/40'
        }`}
      >
        <Bell className="w-4 h-4" aria-hidden="true" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 min-w-[16px] h-4 px-1 bg-status-danger rounded-full text-[9px] font-bold text-white flex items-center justify-center border-2 border-surface-main">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </motion.button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 8, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 8, scale: 0.96 }}
            transition={{ duration: 0.15 }}
            className="absolute right-0 mt-2 w-80 rounded-2xl p-0 z-[100] border border-border/60 shadow-surface-lg bg-surface-card/95 backdrop-blur-xl overflow-hidden origin-top-right"
          >
            <div className="p-3.5 border-b border-border/30 flex items-center justify-between bg-surface-subtle/30">
              <h3 className="font-bold text-[11px] uppercase tracking-wider text-muted">
                {t('sidebar.intelligence')}
              </h3>
              {unreadCount > 0 && (
                <span className="text-[10px] font-semibold text-brand-accent bg-brand-primary/10 px-2 py-0.5 rounded-full">
                  {unreadCount} new
                </span>
              )}
            </div>

            <div className="max-h-72 overflow-y-auto custom-scrollbar">
              {unreadCount > 0 ? (
                <div className="p-2 space-y-1">
                  <button
                    type="button"
                    onClick={() => {
                      navigate('/inbox');
                      setIsOpen(false);
                    }}
                    className="w-full flex items-start gap-3 p-3 rounded-xl hover:bg-surface-hover cursor-pointer transition-colors text-left"
                  >
                    <div className="w-8 h-8 rounded-lg bg-brand-primary/15 flex items-center justify-center flex-shrink-0 text-brand-accent">
                      <Bell className="w-4 h-4" />
                    </div>
                    <div>
                      <p className="text-xs font-medium text-primary">Unread Customer Messages</p>
                      <p className="text-[10px] text-muted mt-0.5">{unreadCount} messages awaiting response</p>
                    </div>
                  </button>
                </div>
              ) : (
                <div className="p-8 text-center text-muted">
                  <div className="w-10 h-10 rounded-xl bg-surface-subtle flex items-center justify-center mx-auto mb-2 text-muted">
                    <Bell className="w-4 h-4 opacity-40" />
                  </div>
                  <p className="text-xs font-medium">{t('inbox.empty.no_conversations')}</p>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
