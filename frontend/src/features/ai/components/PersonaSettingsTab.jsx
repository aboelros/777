import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { User, Sparkles, Save, CheckCircle2, ShieldAlert } from 'lucide-react';
import { toast } from 'sonner';
import api from '../../../services/api';
import { useProjectStore } from '../../../store/projectStore';

const PERSONA_PRESETS = [
  {
    id: 'egyptian_warm',
    name: '🇪🇬 مصري عامي ودود ولَبِق',
    tone: 'Egyptian Warm & Friendly',
    prompt: `أنت بائع بشري شاطر ومحترم من فريق مبيعات المتجر، بتتكلم مصري عامي ودود ولطيف جداً.
- رسائلك سريعة ومختصرة (سطر لـ 3 سطور فقط كأنك بتدردش على إنستغرام أو واتساب).
- بتستخدم عبارات ترحيب راقية زي: (أهلاً بحضرتك يا فندم، من عيوني، ثواني أشوفلك المتاح، تحت أمرك، تمام جداً).
- ممنوع تماماً تبان آلي أو تقول (أنا نموذج ذكاء اصطناعي أو بوت). أنت شخص حقيقي بتساعد العميل في الشراء بحب واهتمام.
- أنهي ردك بسؤال لطيف يقرب من إتمام البيع (زي السؤال عن المقاس أو اللون أو الحجز).`,
  },
  {
    id: 'instagram_punchy',
    name: '📱 Instagram DM (Short & Punchy)',
    tone: 'Casual & Conversational',
    prompt: `You are a real human sales consultant chatting with customers on Instagram Direct.
- Keep replies super crisp and natural (1 to 3 short sentences max).
- Speak with warm enthusiasm, light emojis (✨, 📦), and authentic friendliness.
- Never write robotic paragraphs or essays.
- Help the customer find the right item and guide them smoothly to complete their order.`,
  },
  {
    id: 'pro_closer',
    name: '💼 محترف مبيعات وإغلاق صفقات',
    tone: 'Consultative Sales Specialist',
    prompt: `أنت مستشار مبيعات خبير من فريق المتجر.
- تركز على إبراز جودة المنتج، الرد على الاستفسارات بثقة وبشاشة، وتقديم بدائل ممتازة في حالة نفاذ المنتج.
- تجمع بيانات العميل (الاسم، رقم الهاتف، العنوان) لإنشاء الطلب فوراً.
- تتعامل مع اعتراضات السعر بتوضيح القيمة الحقيقية والضمان بدون جدال.`,
  },
  {
    id: 'gulf_respectful',
    name: '🌟 خليجي راقي ومضياف',
    tone: 'Gulf Respectful & Warm',
    prompt: `أنت مستشار مبيعات بشري راقي يمثل المتجر.
- أسلوبك خليجي محترم ولطيف (يا هلا وغلا، أبشر بعزك، تم يا غالي، نتشرف بخدمتك).
- تشرح تفاصيل المنتجات بأمانة ومحبة وتساعد العميل في اختيار الأنسب بدون تكلف.`,
  },
];

export default function PersonaSettingsTab() {
  const { currentProject, setCurrentProject, loadProjects } = useProjectStore();
  const [botName, setBotName] = useState(currentProject?.bot_name || 'Alex');
  const [botTone, setBotTone] = useState(currentProject?.bot_tone || 'Friendly');
  const [personalityPrompt, setPersonalityPrompt] = useState(currentProject?.personality_prompt || '');
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (currentProject) {
      setBotName(currentProject.bot_name || 'Alex');
      setBotTone(currentProject.bot_tone || 'Friendly');
      setPersonalityPrompt(currentProject.personality_prompt || '');
    }
  }, [currentProject]);

  const handleApplyPreset = (preset) => {
    setBotTone(preset.tone);
    setPersonalityPrompt(preset.prompt);
    toast.info(`تم تطبيق نموذج: ${preset.name}`);
  };

  const handleSave = async () => {
    if (!currentProject) return;
    try {
      setIsSaving(true);
      const updated = await api.projects.update(currentProject.id, {
        bot_name: botName.trim() || 'Alex',
        bot_tone: botTone.trim() || 'Friendly',
        personality_prompt: personalityPrompt.trim(),
      });
      setCurrentProject({ ...currentProject, ...updated });
      await loadProjects();
      toast.success('تم حفظ شخصية وهوية البائع بنجاح!');
    } catch (err) {
      console.error('Failed to update bot persona:', err);
      toast.error('فشل في حفظ بيانات الشخصية. يرجى المحاولة ثانية.');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
      <div className="glass-card p-6 rounded-2xl border border-white/10 space-y-6">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <User className="w-5 h-5 text-accent-primary" />
            هوية وشخصية البائع البشري (Human Sales Persona)
          </h2>
          <p className="text-sm text-gray-400 mt-1">
            اجعل البوت يتحدث كبائع حقيقي من فريق مبيعات متجرك بأسلوب طبيعي ومحبب بعيداً عن الروبوتات.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
            <label className="block text-xs font-bold text-gray-400 uppercase mb-2">نبرة الحديث (Tone / Vibe)</label>
            <input
              type="text"
              value={botTone}
              onChange={(e) => setBotTone(e.target.value)}
              placeholder="مثال: مصري ودود، راقي، حماسي"
              className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-accent-primary/50"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-bold text-gray-400 uppercase mb-2">
            قوالب جاهزة لطريقة الكلام (Quick Presets)
          </label>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {PERSONA_PRESETS.map((p) => (
              <button
                key={p.id}
                type="button"
                onClick={() => handleApplyPreset(p)}
                className="p-3 text-left rounded-xl bg-white/5 hover:bg-accent-primary/10 border border-white/10 hover:border-accent-primary/40 transition-all group"
              >
                <div className="text-sm font-semibold text-white group-hover:text-accent-primary mb-1">{p.name}</div>
                <div className="text-xs text-gray-400 line-clamp-2">{p.tone}</div>
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-xs font-bold text-gray-400 uppercase mb-2">
            تعليمات طريقة الكلام والشخصية المخصصة (Custom Human Style Instructions)
          </label>
          <textarea
            rows={6}
            value={personalityPrompt}
            onChange={(e) => setPersonalityPrompt(e.target.value)}
            placeholder="اكتب هنا التوجيهات الخاصة بكيفية كلام البائع، المصطلحات المفضلة، وطريقة الترحيب وإغلاق الصفقات..."
            className="w-full bg-white/5 border border-white/10 rounded-xl p-4 text-white font-mono text-sm focus:outline-none focus:ring-2 focus:ring-accent-primary/50"
          />
        </div>

        <div className="p-4 rounded-xl bg-sky-500/10 border border-sky-500/20 flex items-start gap-3">
          <ShieldAlert className="w-5 h-5 text-sky-400 shrink-0 mt-0.5" />
          <div className="text-xs text-sky-200 leading-relaxed">
            <strong>قواعد بشرية مطبقة تلقائياً:</strong> البوت يلتزم بإرسال رسائل قصيرة ومركزة (1 إلى 3 جمل كأقصى حد
            لكل رسالة)، لا يذكر أبداً أنه روبوت أو نموذج ذكاء اصطناعي، ويطابق لغة ولهجة العميل تلقائياً.
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
            حفظ إعدادات الشخصية
          </button>
        </div>
      </div>
    </motion.div>
  );
}
