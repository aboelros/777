import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { X, Globe, Sparkles } from 'lucide-react';
import { useTranslation } from '../../../lib/translations';

export default function ScrapeModal({ show, onClose, onScrape, isLoading }) {
  const { t } = useTranslation();
  const [url, setUrl] = useState('');

  if (!show) return null;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-[999] p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="glass-card p-6 max-w-lg w-full rounded-2xl border border-white/10"
      >
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2 text-white">
            <Globe className="w-5 h-5 text-emerald-400" />
            <h2 className="text-xl font-bold">{t('bot_training.modals.scrape_title')}</h2>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-white transition-colors">
            <X className="w-6 h-6" />
          </button>
        </div>

        <p className="text-sm text-gray-400 mb-6">{t('bot_training.modals.scrape_desc')}</p>

        <div className="space-y-4">
          <div>
            <label className="block text-xs font-bold text-gray-400 uppercase mb-2">
              {t('bot_training.modals.fields.website_url')}
            </label>
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com/faq"
              className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-accent-primary/50 focus:outline-none transition-all font-mono text-sm"
            />
          </div>
        </div>

        <div className="flex gap-3 mt-8">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-3 rounded-xl bg-white/5 hover:bg-white/10 transition-all font-bold text-sm text-white"
          >
            {t('bot_training.buttons.cancel')}
          </button>
          <button
            onClick={() => onScrape(url)}
            disabled={!url || isLoading}
            className="flex-1 px-4 py-3 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 disabled:opacity-50 transition-all font-bold text-sm text-white shadow-lg shadow-emerald-500/20 flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                {t('bot_training.buttons.extract')}
              </>
            )}
          </button>
        </div>
      </motion.div>
    </div>
  );
}
