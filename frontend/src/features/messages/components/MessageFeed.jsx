import React, { useRef, useEffect } from 'react';
import PropTypes from 'prop-types';
import { Send, Bot, Sparkles, User, Info, Check, CheckCheck } from 'lucide-react';
import GlassCard from '@/components/ui/GlassCard';
import Button from '@/components/ui/Button';

/**
 * MessageFeed - Center panel displaying customer chat history, AI copilot actions, and response input
 */
export default function MessageFeed({
  conversation,
  messages,
  isLoading,
  messageInput,
  setMessageInput,
  onSendMessage,
  onAIReply,
  isAISending,
  onToggleSidebar,
  t
}) {
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  if (!conversation) {
    return (
      <GlassCard className="h-full flex items-center justify-center p-8 text-center border-[var(--color-border)]">
        <div>
          <div className="w-12 h-12 rounded-2xl bg-sky-500/10 border border-sky-500/20 text-sky-400 flex items-center justify-center mx-auto mb-3">
            <Bot className="w-6 h-6" />
          </div>
          <h3 className="text-base font-semibold text-[var(--color-text-primary)]">Select a Conversation</h3>
          <p className="text-xs text-[var(--color-text-muted)] mt-1">
            Choose a customer thread from the left sidebar to start messaging.
          </p>
        </div>
      </GlassCard>
    );
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (messageInput.trim()) onSendMessage();
    }
  };

  return (
    <GlassCard className="h-full flex flex-col min-h-0 border-[var(--color-border)] overflow-hidden">
      {/* Top Header */}
      <div className="p-3 sm:p-4 border-b border-[var(--color-border)] flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 sm:w-9 sm:h-9 rounded-xl bg-[var(--color-surface-hover)] border border-[var(--color-border)] flex items-center justify-center font-bold text-xs sm:text-sm text-[var(--color-text-primary)]">
            {conversation.customer_name?.charAt(0)?.toUpperCase() || 'U'}
          </div>
          <div>
            <h3 className="font-semibold text-xs sm:text-sm text-[var(--color-text-primary)] truncate max-w-[140px] sm:max-w-[200px]">
              {conversation.customer_name || 'Customer'}
            </h3>
            <p className="text-[11px] text-[var(--color-text-muted)] capitalize">
              {conversation.channel} Channel Active
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="outline"
            onClick={onAIReply}
            disabled={isAISending}
            leftIcon={Sparkles}
          >
            AI Reply
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={onToggleSidebar}
            aria-label="Toggle Details"
          >
            <Info className="w-4 h-4 text-[var(--color-text-muted)]" />
          </Button>
        </div>
      </div>

      {/* Message Feed History - clean container with no disruptive scrollbar */}
      <div ref={scrollRef} className="flex-1 min-h-0 overflow-y-auto p-3 sm:p-4 space-y-2.5 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
        {isLoading ? (
          <div className="py-12 text-center text-xs text-[var(--color-text-muted)]">
            Loading message log...
          </div>
        ) : (messages || []).length === 0 ? (
          <div className="py-12 text-center text-xs text-[var(--color-text-muted)]">
            No messages exchanged yet.
          </div>
        ) : (
          (messages || []).map((msg, idx) => {
            const isUser = msg.sender === 'user' || msg.direction === 'outbound';
            const isBot = msg.sender === 'bot';

            return (
              <div
                key={msg.id || idx}
                className={`flex items-end gap-2 ${isUser ? 'justify-end' : 'justify-start'}`}
              >
                {!isUser && (
                  <div className="w-6 h-6 sm:w-7 sm:h-7 rounded-lg bg-[var(--color-surface-hover)] border border-[var(--color-border)] flex items-center justify-center text-[var(--color-text-muted)] flex-shrink-0">
                    {isBot ? <Bot className="w-3.5 h-3.5 text-sky-400" /> : <User className="w-3.5 h-3.5" />}
                  </div>
                )}

                <div
                  className={`max-w-[75%] p-2.5 sm:p-3 rounded-2xl text-xs leading-relaxed ${
                    isUser
                      ? 'bg-sky-500 text-white rounded-br-none'
                      : 'bg-[var(--color-surface)] border border-[var(--color-border)] text-[var(--color-text-primary)] rounded-bl-none'
                  }`}
                >
                  <p className="break-words">{msg.content || msg.text}</p>
                  <div className="flex items-center justify-end gap-1 mt-1 text-[10px] opacity-75">
                    <span>{new Date(msg.created_at || Date.now()).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                    {isUser && <CheckCheck className="w-3 h-3" />}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Message Input Bottom Bar - Locked & always visible */}
      <div className="p-2.5 sm:p-3 border-t border-[var(--color-border)] flex items-center gap-2 flex-shrink-0 bg-[var(--color-surface)]/50 backdrop-blur-md">
        <input
          type="text"
          value={messageInput}
          onChange={(e) => setMessageInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your message or prompt AI..."
          className="flex-1 px-4 py-2 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl text-xs text-[var(--color-text-primary)] placeholder-[var(--color-text-muted)] focus:outline-none focus:ring-2 focus:ring-sky-500/30"
        />
        <Button
          onClick={onSendMessage}
          disabled={!messageInput.trim()}
          variant="primary"
          size="sm"
          aria-label="Send Message"
        >
          <Send className="w-4 h-4" />
        </Button>
      </div>
    </GlassCard>
  );
}

MessageFeed.propTypes = {
  conversation: PropTypes.object,
  messages: PropTypes.array,
  isLoading: PropTypes.bool,
  messageInput: PropTypes.string.isRequired,
  setMessageInput: PropTypes.func.isRequired,
  onSendMessage: PropTypes.func.isRequired,
  onAIReply: PropTypes.func.isRequired,
  isAISending: PropTypes.bool,
  onToggleSidebar: PropTypes.func.isRequired,
  t: PropTypes.func.isRequired
};
