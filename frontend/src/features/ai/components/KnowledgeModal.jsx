import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { X } from 'lucide-react';
import { useTranslation } from '../../../lib/translations';

export default function KnowledgeModal({ show, item, onClose, onSave }) {
  const { t } = useTranslation();
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    source_type: 'text',
    is_active: true,
  });

  useEffect(() => {
    if (item) {
      setFormData({
        title: item.title || '',
        content: item.content || '',
        source_type: item.source_type || 'text',
        is_active: item.is_active !== false,
      });
    } else {
      setFormData({
        title: '',
        content: '',
        source_type: 'text',
        is_active: true,
      });
    }
  }, [item, show]);

  if (!show) return null;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-[999] p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="glass-card p-6 max-w-lg w-full rounded-2xl border border-white/10"
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-white">{item ? 'Edit Knowledge' : 'Add Knowledge'}</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white transition-colors">
            <X className="w-6 h-6" />
          </button>
        </div>
        <div className="space-y-4">
          <div>
            <label className="block text-xs font-bold text-gray-400 uppercase mb-2">
              {t('bot_training.modals.fields.title')}
            </label>
            <input
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white focus:ring-2 focus:ring-accent-primary/50 focus:outline-none transition-all"
              placeholder="e.g., Return & Refund Policy"
            />
          </div>
          <div>
            <label className="block text-xs font-bold text-gray-400 uppercase mb-2">
              {t('bot_training.modals.fields.content')}
            </label>
            <textarea
              value={formData.content}
              onChange={(e) => setFormData({ ...formData, content: e.target.value })}
              className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 h-40 text-white focus:ring-2 focus:ring-accent-primary/50 focus:outline-none transition-all resize-none"
              placeholder="Paste business knowledge, rules, shipping fees, or FAQs here..."
            />
          </div>
          <div className="flex items-center justify-between pt-2">
            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                className="w-5 h-5 rounded bg-white/5 border-white/20 accent-accent-primary cursor-pointer"
                id="kb-active"
              />
              <label htmlFor="kb-active" className="text-sm font-medium cursor-pointer select-none text-white">
                {t('bot_training.modals.fields.published')}
              </label>
            </div>
            <select
              value={formData.source_type}
              onChange={(e) => setFormData({ ...formData, source_type: e.target.value })}
              className="bg-dark-800 border border-white/10 rounded-lg px-3 py-1 text-[10px] font-bold uppercase text-white outline-none cursor-pointer"
            >
              <option value="text">Text</option>
              <option value="faq">FAQ</option>
              <option value="policy">Policy</option>
              <option value="shipping">Shipping</option>
              <option value="document">Document</option>
            </select>
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
            onClick={() => onSave(formData)}
            className="flex-1 px-4 py-3 rounded-xl bg-accent-primary hover:bg-accent-600 transition-all font-bold text-sm text-white shadow-lg shadow-accent-primary/20"
          >
            {t('bot_training.buttons.save')}
          </button>
        </div>
      </motion.div>
    </div>
  );
}
