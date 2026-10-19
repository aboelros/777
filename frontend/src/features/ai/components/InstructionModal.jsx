import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { X } from 'lucide-react';
import { useTranslation } from '../../../lib/translations';

export default function InstructionModal({ show, instruction, onClose, onSave }) {
  const { t } = useTranslation();
  const [formData, setFormData] = useState({
    title: '',
    instruction: '',
    category: 'tone',
    priority: 5,
    is_active: true,
  });

  useEffect(() => {
    if (instruction) {
      setFormData({
        title: instruction.title || '',
        instruction: instruction.instruction || '',
        category: instruction.category || 'tone',
        priority: instruction.priority || 5,
        is_active: instruction.is_active !== false,
      });
    } else {
      setFormData({
        title: '',
        instruction: '',
        category: 'tone',
        priority: 5,
        is_active: true,
      });
    }
  }, [instruction, show]);

  if (!show) return null;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-[999] p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="glass-card p-6 max-w-lg w-full rounded-2xl border border-white/10"
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-white">
            {instruction ? t('bot_training.modals.edit_instruction') : t('bot_training.modals.add_instruction')}
          </h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <X className="w-6 h-6" />
          </button>
        </div>
        <div className="space-y-4">
          <div>
            <label className="block text-xs font-bold text-gray-400 uppercase mb-2">Title</label>
            <input
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-accent-primary/50"
              placeholder="e.g., Friendly Greeting"
            />
          </div>
          <div>
            <label className="block text-xs font-bold text-gray-400 uppercase mb-2">Instruction</label>
            <textarea
              value={formData.instruction}
              onChange={(e) => setFormData({ ...formData, instruction: e.target.value })}
              className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 h-32 text-white focus:outline-none focus:ring-2 focus:ring-accent-primary/50"
              placeholder="Describe how the AI should behave..."
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-gray-400 uppercase mb-2">Category</label>
              <select
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                className="w-full bg-dark-800 border border-white/10 rounded-lg px-4 py-2 text-white"
              >
                <option value="tone">Tone / نبرة</option>
                <option value="response_style">Response Style / أسلوب الرد</option>
                <option value="sales">Sales & Closing / مبيعات</option>
                <option value="product_knowledge">Product Knowledge / منتجات</option>
                <option value="promotions">Promotions / عروض</option>
                <option value="service">Customer Service / خدمة عملاء</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-bold text-gray-400 uppercase mb-2">Priority</label>
              <input
                type="number"
                value={formData.priority}
                onChange={(e) => setFormData({ ...formData, priority: parseInt(e.target.value) || 0 })}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-accent-primary/50"
              />
            </div>
          </div>
        </div>
        <div className="flex gap-3 mt-8">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 transition-all font-medium text-white"
          >
            Cancel
          </button>
          <button
            onClick={() => onSave(formData)}
            className="flex-1 px-4 py-2 rounded-lg bg-accent-primary hover:bg-accent-600 transition-all font-medium text-white shadow-lg shadow-accent-primary/20"
          >
            Save changes
          </button>
        </div>
      </motion.div>
    </div>
  );
}
