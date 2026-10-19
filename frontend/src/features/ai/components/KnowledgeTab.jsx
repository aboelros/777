import React from 'react';
import { motion } from 'framer-motion';
import { BookOpen, Edit2, Trash2, Plus, Zap, FileText } from 'lucide-react';

const QUICK_KNOWLEDGE_TEMPLATES = [
  {
    title: 'سياسة الاستبدال والاسترجاع',
    content: 'يحق للعميل استبدال أو استرجاع المنتج خلال 14 يوماً من الاستلام بشرط أن يكون بحالته الأصلية وبالغلاف. يتم فحص المنتج والتوصيل خلال 48 ساعة.',
    source_type: 'policy',
  },
  {
    title: 'مواعيد وتكلفة الشحن',
    content: 'التوصيل لجميع محافظات مصر: القاهرة والجيزة خلال 24-48 ساعة، باقي المحافظات خلال 2-4 أيام عمل. مصاريف الشحن 50 جنيه للقاهرة و65 جنيه للمحافظات.',
    source_type: 'shipping',
  },
  {
    title: 'طرق الدفع المتاحة',
    content: 'نوفر الدفع عند الاستلام (COD)، الدفع بالبطاقات البنكية، والتحويل عبر إنستاباي (InstaPay) ومحافظ الهاتف كاش.',
    source_type: 'faq',
  },
];

export default function KnowledgeTab({
  items,
  onAdd,
  onEdit,
  onDelete,
  onScrape,
  onApplyTemplate,
}) {
  return (
    <div className="space-y-6">
      {/* Quick Add Suggestions */}
      <div className="p-4 rounded-xl bg-white/5 border border-white/10 space-y-2">
        <span className="text-xs font-bold text-gray-400 uppercase tracking-wider block">
          قوالب سريعة مقترحة لبيانات متجرك (بنقرة واحدة):
        </span>
        <div className="flex flex-wrap gap-2">
          {QUICK_KNOWLEDGE_TEMPLATES.map((tmpl, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => onApplyTemplate(tmpl)}
              className="text-xs px-3 py-1.5 rounded-lg bg-white/5 hover:bg-accent-primary/20 text-gray-300 hover:text-white border border-white/10 transition-colors flex items-center gap-1.5"
            >
              <FileText className="w-3.5 h-3.5 text-accent-primary" />
              + {tmpl.title}
            </button>
          ))}
        </div>
      </div>

      {items.length === 0 ? (
        <div className="text-center py-16 glass-card rounded-2xl border border-white/10 p-8 space-y-4">
          <BookOpen className="w-16 h-16 text-gray-600 mx-auto" />
          <h3 className="text-xl font-bold text-white">قاعدة المعرفة فارغة</h3>
          <p className="text-gray-400 max-w-md mx-auto text-sm">
            أضف سياسات المتجر، أوقات العمل، مصاريف الشحن، أو اسحب محتوى صفحات الأسئلة الشائعة من موقعك.
          </p>
          <div className="flex justify-center gap-3 pt-2">
            <button
              onClick={onScrape}
              className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-emerald-500 to-teal-600 text-white rounded-xl font-bold text-sm hover:from-emerald-600 hover:to-teal-700 transition-all shadow-lg shadow-emerald-500/20"
            >
              <Zap className="w-4 h-4" />
              سحب من رابط صفحة (URL)
            </button>
            <button
              onClick={onAdd}
              className="px-5 py-2.5 bg-accent-primary text-white rounded-xl font-bold text-sm hover:bg-accent-600 transition-all"
            >
              إضافة معرفة يدوياً
            </button>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {items.map((item) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="glass-card p-5 rounded-2xl border border-white/10 hover:border-white/20 transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div className="flex items-center gap-2">
                    <BookOpen className="w-4 h-4 text-emerald-400 shrink-0" />
                    <h3 className="text-sm font-bold text-white line-clamp-1">{item.title}</h3>
                  </div>
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase shrink-0 ${
                      item.is_active ? 'bg-emerald-500/20 text-emerald-400' : 'bg-gray-500/20 text-gray-400'
                    }`}
                  >
                    {item.is_active ? 'Active' : 'Draft'}
                  </span>
                </div>
                <div className="text-xs text-gray-300 line-clamp-4 bg-black/20 p-3 rounded-xl border border-white/5 leading-relaxed">
                  {item.content}
                </div>
              </div>

              <div className="flex items-center justify-between pt-3 mt-3 border-t border-white/5">
                <span className="text-[10px] text-gray-500 uppercase font-mono font-bold">
                  {item.source_type || 'Text'}
                </span>
                <div className="flex gap-1">
                  <button
                    onClick={() => onEdit(item)}
                    className="p-1.5 hover:bg-white/10 rounded-lg text-gray-400 hover:text-white transition-all"
                    title="تعديل"
                  >
                    <Edit2 className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => onDelete(item.id)}
                    className="p-1.5 hover:bg-rose-500/20 rounded-lg text-gray-400 hover:text-rose-400 transition-all"
                    title="حذف"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
