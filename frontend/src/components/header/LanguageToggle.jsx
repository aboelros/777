import { Globe } from 'lucide-react';
import { motion } from 'framer-motion';
import useThemeStore from '@/store/themeStore';

export default function LanguageToggle() {
  const { language, setLanguage } = useThemeStore();
  const isArabic = language === 'ar';

  const toggleLanguage = () => {
    setLanguage(isArabic ? 'en' : 'ar');
  };

  return (
    <motion.button
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={toggleLanguage}
      type="button"
      title={isArabic ? 'Switch to English' : 'التحويل إلى العربية'}
      aria-label={isArabic ? 'Switch to English' : 'التحويل إلى العربية'}
      className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl bg-white/[0.05] border border-white/10 hover:border-sky-400/40 hover:bg-sky-500/10 backdrop-blur-md text-slate-300 hover:text-white transition-colors duration-200 select-none shadow-[inset_0_1px_1px_rgba(255,255,255,0.08)]"
    >
      <Globe className="w-3.5 h-3.5 text-sky-400" />
      <span className="text-xs font-semibold tracking-wide">
        {isArabic ? 'العربية' : 'EN'}
      </span>
      <span className="text-[10px] text-slate-500 font-mono uppercase">
        {isArabic ? 'AR' : 'EN'}
      </span>
    </motion.button>
  );
}
