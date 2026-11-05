import React from 'react';
import PropTypes from 'prop-types';
import { motion, AnimatePresence } from 'framer-motion';
import {
  MessageSquare,
  Search,
  MessageCircle,
  Send,
  Instagram,
  Facebook,
  Phone
} from 'lucide-react';
import Input from '@/components/ui/Input';
import Button from '@/components/ui/Button';

const CHANNEL_ICONS = {
  whatsapp: MessageCircle,
  telegram: Send,
  instagram: Instagram,
  facebook: Facebook,
  sms: Phone,
  email: MessageSquare
};

const CHANNEL_COLORS = {
  whatsapp: 'text-emerald-400',
  telegram: 'text-sky-400',
  instagram: 'text-pink-400',
  facebook: 'text-blue-400',
  sms: 'text-cyan-400',
  email: 'text-slate-400'
};

/**
 * ConversationList - Left sidebar for searching, filtering, and switching customer chats
 */
export default function ConversationList({
  conversations,
  isLoading,
  selectedId,
  onSelect,
  searchQuery,
  setSearchQuery,
  channelFilter,
  setChannelFilter,
  t
}) {
  const filtered = (conversations || []).filter(
    (c) =>
      !searchQuery ||
      c.customer_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.customer_email?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="h-full w-full flex flex-col min-h-0 border border-white/10 rounded-2xl bg-[#0c1326]/85 backdrop-blur-2xl shadow-2xl relative overflow-hidden">
      {/* Specular Rim Light */}
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/25 to-transparent pointer-events-none" />

      {/* Search & Channel Filters */}
      <div className="p-3 sm:p-4 border-b border-white/10 space-y-2.5 flex-shrink-0 bg-[#090e1d]/70 backdrop-blur-md z-10">
        <Input
          icon={Search}
          placeholder={t('inbox.search_placeholder') || 'Search name or email...'}
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />

        <div className="flex flex-wrap gap-1">
          {['all', 'whatsapp', 'telegram', 'instagram', 'facebook'].map((ch) => {
            const Icon = CHANNEL_ICONS[ch] || MessageSquare;
            const isActive = channelFilter === ch;

            return (
              <button
                key={ch}
                onClick={() => setChannelFilter(ch)}
                className={`px-2 py-0.5 text-[11px] rounded-lg flex items-center gap-1 transition-all ${
                  isActive
                    ? 'bg-sky-500 text-white font-medium shadow-sm'
                    : 'bg-[var(--color-surface)] text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)]'
                }`}
              >
                <Icon className="w-2.5 h-2.5" />
                <span className="capitalize">{ch}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Conversations Scroll Area */}
      <div
        className="flex-1 min-h-0 overflow-y-auto p-2 space-y-1 custom-scrollbar"
        style={{ scrollBehavior: 'smooth', overscrollBehavior: 'contain' }}
      >
        {isLoading ? (
          <div className="py-12 text-center text-xs text-[var(--color-text-muted)]">
            Loading conversations...
          </div>
        ) : filtered.length === 0 ? (
          <div className="py-12 text-center text-xs text-[var(--color-text-muted)]">
            No active conversations
          </div>
        ) : (
          <AnimatePresence>
            {filtered.map((conv) => {
              const ChannelIcon = CHANNEL_ICONS[conv.channel] || MessageSquare;
              const chColor = CHANNEL_COLORS[conv.channel] || 'text-slate-400';
              const isSelected = selectedId === conv.id;

              return (
                <div
                  key={conv.id}
                  onClick={() => onSelect(conv)}
                  className={`p-3 rounded-xl cursor-pointer transition-all flex items-start gap-3 border ${
                    isSelected
                      ? 'bg-sky-500/10 border-sky-500/40 shadow-sm'
                      : 'border-transparent hover:bg-[var(--color-surface-hover)]'
                  }`}
                >
                  <div className="relative">
                    <div className="w-10 h-10 rounded-xl bg-[var(--color-surface-hover)] border border-[var(--color-border)] flex items-center justify-center font-bold text-sm text-[var(--color-text-primary)]">
                      {conv.customer_name?.charAt(0)?.toUpperCase() || 'U'}
                    </div>
                    <div className="absolute -bottom-1 -right-1 w-4 h-4 rounded-full bg-[var(--color-bg)] border border-[var(--color-border)] flex items-center justify-center">
                      <ChannelIcon className={`w-2.5 h-2.5 ${chColor}`} />
                    </div>
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-0.5">
                      <p className="text-sm font-semibold text-[var(--color-text-primary)] truncate">
                        {conv.customer_name || 'Customer'}
                      </p>
                      {conv.unread_count > 0 && (
                        <span className="px-1.5 py-0.5 bg-sky-500 text-white text-[10px] font-bold rounded-full">
                          {conv.unread_count}
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-[var(--color-text-muted)] truncate">
                      {conv.last_message || 'Start conversation...'}
                    </p>
                  </div>
                </div>
              );
            })}
          </AnimatePresence>
        )}
      </div>
    </div>
  );
}

ConversationList.propTypes = {
  conversations: PropTypes.array,
  isLoading: PropTypes.bool,
  selectedId: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  onSelect: PropTypes.func.isRequired,
  searchQuery: PropTypes.string.isRequired,
  setSearchQuery: PropTypes.func.isRequired,
  channelFilter: PropTypes.string.isRequired,
  setChannelFilter: PropTypes.func.isRequired,
  t: PropTypes.func.isRequired
};
