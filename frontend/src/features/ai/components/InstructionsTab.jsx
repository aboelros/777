import React from 'react';
import { motion } from 'framer-motion';
import { GraduationCap, Edit2, Trash2, Zap, Sparkles } from 'lucide-react';

const CATEGORY_COLORS = {
  tone: 'from-accent-primary to-accent-600',
  response_style: 'from-indigo-500 to-blue-600',
  sales: 'from-amber-500 to-orange-600',
  product_knowledge: 'from-green-500 to-emerald-600',
  promotions: 'from-yellow-500 to-orange-600',
  service: 'from-rose-500 to-pink-600',
};

export default function InstructionsTab({
  instructions,
  onAdd,
  onEdit,
  onDelete,
  onSeed,
  isSeeding,
}) {
  return (
    <div className="space-y-6">
      {instructions.length === 0 ? (
        <div className="text-center py-16 glass-card rounded-2xl border border-white/10 p-8 space-y-4">
          <GraduationCap className="w-16 h-16 text-gray-600 mx-auto" />
          <h3 className="text-xl font-bold text-white">لا توجد تعليمات مخصصة حتى الآن</h3>
          <p className="text-gray-400 max-w-md mx-auto text-sm">
            أضف قواعد مخصصة أو انقر على الزر السريع لإضافة باقة تعليمات البائع البشري الذكي تلقائياً.
          </p>
          <div className="flex justify-center gap-3 pt-2">
            <button
              onClick={onSeed}
              disabled={isSeeding}
              className="flex items-center gap-2 px-5 py-2.5 bg-sky-500/10 text-sky-400 border border-sky-500/20 rounded-xl hover:bg-sky-500/20 transition-all font-bold text-sm"
            >
              <Zap className="w-4 h-4" />
              {isSeeding ? 'جاري التحميل...' : 'إضافة باقة تعليمات البائع البشري الجاهزة'}
            </button>
            <button
              onClick={onAdd}
              className="px-5 py-2.5 bg-accent-primary text-white rounded-xl hover:bg-accent-600 transition-all font-bold text-sm"
            >
              إضافة تعليمات يدوياً
            </button>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {instructions.map((item) => {
            const badgeColor = CATEGORY_COLORS[item.category] || 'from-gray-500 to-gray-600';
            return (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="glass-card p-5 rounded-2xl border border-white/10 hover:border-white/20 transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-start justify-between gap-3 mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 flex-wrap mb-1">
                        <h3 className="text-base font-bold text-white">{item.title}</h3>
                        {item.category && (
                          <span
                            className={`px-2 py-0.5 rounded-full text-[10px] font-bold bg-gradient-to-r ${badgeColor} text-white`}
                          >
                            {item.category}
                          </span>
                        )}
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-accent-primary/20 text-accent-primary">
                          أولوية: {item.priority}
                        </span>
                      </div>
                      <p className="text-gray-300 text-xs leading-relaxed line-clamp-3">{item.instruction}</p>
                    </div>
                    <div
                      className={`px-2 py-1 rounded text-[10px] font-bold ${
                        item.is_active ? 'bg-emerald-500/20 text-emerald-400' : 'bg-gray-500/20 text-gray-400'
                      }`}
                    >
                      {item.is_active ? 'نشط' : 'معطل'}
                    </div>
                  </div>
                </div>

                <div className="flex gap-2 pt-3 border-t border-white/5">
                  <button
                    onClick={() => onEdit(item)}
                    className="flex-1 glass-card py-2 px-3 rounded-lg hover:bg-white/10 text-xs font-semibold text-white flex items-center justify-center gap-1.5 transition-colors"
                  >
                    <Edit2 className="w-3.5 h-3.5" />
                    تعديل
                  </button>
                  <button
                    onClick={() => onDelete(item.id)}
                    className="p-2 rounded-lg hover:bg-rose-500/20 text-gray-400 hover:text-rose-400 transition-colors"
                    title="حذف"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </motion.div>
            );
          })}
        </div>
      )}
    </div>
  );
}
