import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { User, Save, ShieldAlert, Sparkles, Store } from 'lucide-react';
import { toast } from 'sonner';
import api from '../../../services/api';
import { useProjectStore } from '../../../store/projectStore';
import { SHOP_TYPES, INDUSTRY_PRESETS } from './shopTypePresets';

export default function PersonaSettingsTab() {
  const { currentProject, setCurrentProject, loadProjects } = useProjectStore();
  const [shopType, setShopType] = useState(currentProject?.settings?.shop_type || 'general');
  const [botName, setBotName] = useState(currentProject?.bot_name || 'Alex');
  const [botTone, setBotTone] = useState(currentProject?.bot_tone || 'Friendly');
  const [personalityPrompt, setPersonalityPrompt] = useState(currentProject?.personality_prompt || '');
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (currentProject) {
      setShopType(currentProject.settings?.shop_type || 'general');
      setBotName(currentProject.bot_name || 'Alex');
      setBotTone(currentProject.bot_tone || 'Friendly');
      setPersonalityPrompt(currentProject.personality_prompt || '');
    }
  }, [currentProject]);

  const handleSelectShopType = (typeId) => {
    setShopType(typeId);
    const presets = INDUSTRY_PRESETS[typeId] || INDUSTRY_PRESETS.general;
    if (presets && presets.length > 0) {
      const first = presets[0];
      setBotTone(first.tone);
      setPersonalityPrompt(first.prompt);
      toast.info(`تم تفعيل إعدادات نشاط: ${first.name}`);
    }
  };

  const handleApplyPreset = (preset) => {
    setBotTone(preset.tone);
    setPersonalityPrompt(preset.prompt);
    toast.info(`تم تطبيق قالب: ${preset.name}`);
  };

  const handleSave = async () => {
    if (!currentProject) return;
    try {
      setIsSaving(true);
      const updatedSettings = {
        ...(currentProject.settings || {}),
        shop_type: shopType,
      };
      const updated = await api.projects.update(currentProject.id, {
        bot_name: botName.trim() || 'Alex',
        bot_tone: botTone.trim() || 'Friendly',
        personality_prompt: personalityPrompt.trim(),
        settings: updatedSettings,
      });
      setCurrentProject({ ...currentProject, ...updated, settings: updatedSettings });
      await loadProjects();
      toast.success('تم حفظ نوع النشاط وهوية البائع بنجاح!');
    } catch (err) {
      console.error('Failed to update bot persona:', err);
      toast.error('فشل في حفظ البيانات. يرجى المحاولة ثانية.');
    } finally {
      setIsSaving(false);
    }
  };

  const activePresets = INDUSTRY_PRESETS[shopType] || INDUSTRY_PRESETS.general;

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
      <div className="glass-card p-6 rounded-2xl border border-white/10 space-y-6">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Store className="w-5 h-5 text-accent-primary" />
            نوع المتجر والنشاط التجاري (Shop / Business Category)
          </h2>
          <p className="text-sm text-gray-400 mt-1">
            اختر نوع نشاط متجرك لتخصيص مصطلحات الذكاء الاصطناعي وطريقة عرض المنتجات والوجبات والخدمات.
          </p>
        </div>

        {/* Shop Type Selector */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
          {SHOP_TYPES.map((type) => {
            const isSelected = shopType === type.id;
            return (
              <button
                key={type.id}
                type="button"
                onClick={() => handleSelectShopType(type.id)}
                className={`p-4 rounded-xl border text-right transition-all flex flex-col justify-between ${
                  isSelected
                    ? 'bg-accent-primary/20 border-accent-primary text-white shadow-lg shadow-accent-primary/20'
                    : 'bg-white/5 border-white/10 hover:border-white/20 text-gray-300 hover:text-white'
                }`}
              >
                <div>
                  <div className="text-xs font-bold mb-1 text-accent-primary">{type.badge}</div>
                  <div className="text-sm font-bold text-white">{type.name}</div>
                </div>
                <div className="text-[11px] text-gray-400 mt-2 line-clamp-2 leading-relaxed">{type.desc}</div>
              </button>
            );
          })}
        </div>

        {/* Basic Info */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
          <div>
            <label className="block text-xs font-bold text-gray-400 uppercase mb-2">اسم البائع (Agent Name)</label>
            <input
              type="text"
              value={botName}
              onChange={(e) => setBotName(e.target.value)}
              placeholder="مثال: سارة، أحمد، Alex"
              className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-accent-primary/50"
            />
          </div>
          <div>
            <label className="block text-xs font-bold text-gray-400 uppercase mb-2">أسلوب ونبرة الرد (Tone)</label>
            <input
              type="text"
              value={botTone}
              onChange={(e) => setBotTone(e.target.value)}
              placeholder="مثال: مصري ودود، استشاري مبيعات، باريستا مضياف"
              className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-accent-primary/50"
            />
          </div>
        </div>

        {/* Industry Presets */}
        <div>
          <label className="block text-xs font-bold text-gray-400 uppercase mb-2 flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-accent-primary" />
            نماذج طريقة الكلام الخاصة بهذا النشاط (Industry Presets)
          </label>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {activePresets.map((p) => (
              <button
                key={p.id}
                type="button"
                onClick={() => handleApplyPreset(p)}
                className="p-3 text-right rounded-xl bg-white/5 hover:bg-accent-primary/10 border border-white/10 hover:border-accent-primary/40 transition-all group"
              >
                <div className="text-sm font-semibold text-white group-hover:text-accent-primary mb-1">{p.name}</div>
                <div className="text-xs text-gray-400 line-clamp-2">{p.tone}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Custom Instructions */}
        <div>
          <label className="block text-xs font-bold text-gray-400 uppercase mb-2">
            تعليمات أسلوب الكلام المخصصة (Custom Instructions)
          </label>
          <textarea
            rows={5}
            value={personalityPrompt}
            onChange={(e) => setPersonalityPrompt(e.target.value)}
            placeholder="اكتب هنا التوجيهات الخاصة بكيفية كلام البائع، المصطلحات المفضلة، وطريقة الترحيب وإغلاق الصفقات..."
            className="w-full bg-white/5 border border-white/10 rounded-xl p-4 text-white font-mono text-xs focus:outline-none focus:ring-2 focus:ring-accent-primary/50"
          />
        </div>

        <div className="p-4 rounded-xl bg-sky-500/10 border border-sky-500/20 flex items-start gap-3">
          <ShieldAlert className="w-5 h-5 text-sky-400 shrink-0 mt-0.5" />
          <div className="text-xs text-sky-200 leading-relaxed">
            <strong>قواعد التفاعل التلقائية:</strong> البوت يتحدث بطبيعة بشرية سلسة في فقاعات قصيرة (1 إلى 3 جمل)، ويطابق مصطلحات النشاط تلقائياً (منيو/وجبات للمطاعم، مقاسات/ألوان للملابس، ونوع البشرة للصيدليات).
          </div>
        </div>

        <div className="flex justify-end pt-2">
          <button
            type="button"
            onClick={handleSave}
            disabled={isSaving}
            className="flex items-center gap-2 px-6 py-3 bg-accent-primary hover:bg-accent-600 disabled:opacity-50 text-white rounded-xl font-bold transition-all shadow-lg shadow-accent-primary/20"
          >
            {isSaving ? (
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : (
              <Save className="w-5 h-5" />
            )}
            حفظ إعدادات النشاط والشخصية
          </button>
        </div>
      </div>
    </motion.div>
  );
}
