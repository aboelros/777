import React from 'react';
import PropTypes from 'prop-types';
import { Bot, CheckCheck } from 'lucide-react';

/**
 * Safely extracts image attachment URL from various Meta webhook payload schemas
 */
export const extractImageUrl = (msg) => {
  if (!msg) return null;
  if (typeof msg.media_url === 'string' && msg.media_url.trim()) return msg.media_url;
  if (typeof msg.image_url === 'string' && msg.image_url.trim()) return msg.image_url;
  if (Array.isArray(msg.attachments) && msg.attachments.length > 0) {
    const att = msg.attachments[0];
    if (att) {
      if (typeof att.url === 'string' && att.url.trim()) return att.url;
      if (att.payload && typeof att.payload.url === 'string' && att.payload.url.trim()) return att.payload.url;
    }
  }
  const extra = msg.extra_data || msg.metadata;
  if (extra && typeof extra === 'object') {
    if (Array.isArray(extra.media) && extra.media.length > 0) {
      const m = extra.media[0];
      if (m && typeof m.url === 'string') return m.url;
      if (m && m.payload && typeof m.payload.url === 'string') return m.payload.url;
    }
    if (Array.isArray(extra.attachments) && extra.attachments.length > 0) {
      const a = extra.attachments[0];
      if (a && typeof a.url === 'string') return a.url;
      if (a && a.payload && typeof a.payload.url === 'string') return a.payload.url;
    }
  }
  return null;
};

/**
 * Individual chat message bubble supporting images, text, and avatars
 */
export default function MessageItem({ msg, isUser, isBot, customerAvatar, customerName }) {
  const imageUrl = extractImageUrl(msg);
  const rawContent = msg.content || msg.text || '';
  const isPlaceholder =
    rawContent.toLowerCase() === '[image attachment]' ||
    rawContent.toLowerCase() === '[photo attachment]' ||
    rawContent.toLowerCase() === '[media attachment]';
  const displayContent = isPlaceholder && imageUrl ? '' : rawContent;
  const senderAvatar = msg.sender?.avatar_url || customerAvatar;

  return (
    <div className={`flex items-end gap-2 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div className="w-6 h-6 sm:w-7 sm:h-7 rounded-lg bg-[var(--color-surface-hover)] border border-[var(--color-border)] flex items-center justify-center text-[var(--color-text-muted)] flex-shrink-0 overflow-hidden relative">
          {isBot ? (
            <Bot className="w-3.5 h-3.5 text-sky-400" />
          ) : (
            <>
              <span className="select-none text-[10px] font-bold">
                {customerName?.charAt(0)?.toUpperCase() || 'U'}
              </span>
              {senderAvatar && (
                <img
                  src={senderAvatar}
                  alt=""
                  className="absolute inset-0 w-full h-full object-cover"
                  onError={(e) => {
                    e.currentTarget.style.display = 'none';
                  }}
                />
              )}
            </>
          )}
        </div>
      )}

      <div
        className={`max-w-[85%] sm:max-w-[75%] p-2.5 sm:p-3 rounded-2xl text-xs leading-relaxed ${
          isUser
            ? 'bg-sky-500 text-white rounded-br-none shadow-md'
            : 'bg-[var(--color-surface)] border border-[var(--color-border)] text-[var(--color-text-primary)] rounded-bl-none shadow-sm'
        }`}
      >
        {imageUrl && (
          <div className="mb-2 overflow-hidden rounded-xl border border-white/10 bg-black/30">
            <a
              href={imageUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="block group relative"
              title="Click to view full image in new tab"
            >
              <img
                src={imageUrl}
                alt="Photo Attachment"
                className="w-full max-h-60 sm:max-h-72 object-cover rounded-xl transition-transform duration-200 group-hover:scale-[1.02]"
                loading="lazy"
                onError={(e) => {
                  e.currentTarget.style.display = 'none';
                }}
              />
              <div className="absolute top-2 right-2 px-1.5 py-0.5 rounded-md bg-black/60 text-[10px] text-white opacity-0 group-hover:opacity-100 transition-opacity backdrop-blur-sm pointer-events-none">
                View full ↗
              </div>
            </a>
          </div>
        )}

        {displayContent ? <p className="break-words">{displayContent}</p> : null}

        <div className="flex items-center justify-end gap-1 mt-1 text-[10px] opacity-75">
          <span>{new Date(msg.created_at || Date.now()).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
          {isUser && <CheckCheck className="w-3 h-3" />}
        </div>
      </div>
    </div>
  );
}

MessageItem.propTypes = {
  msg: PropTypes.object.isRequired,
  isUser: PropTypes.bool.isRequired,
  isBot: PropTypes.bool.isRequired,
  customerAvatar: PropTypes.string,
  customerName: PropTypes.string
};
