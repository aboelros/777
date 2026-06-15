import { motion } from 'framer-motion';
import { Facebook, Instagram, Hash, MessageCircle } from 'lucide-react';
import useThemeStore from '../store/themeStore';
import { useTranslation } from '../lib/translations';

export default function SocialAccountCard({ account, isSelected, onClick }) {
    const { t } = useTranslation();
    const getIcon = (platform) => {
        switch (platform) {
            case 'facebook': return Facebook;
            case 'instagram': return Instagram;
            case 'whatsapp': return MessageCircle; // Approximate
            case 'tiktok': return Hash;
            default: return Hash;
        }
    };

    const getGradient = (platform) => {
        switch (platform) {
            case 'facebook': return 'from-blue-600 to-blue-700';
            case 'instagram': return 'from-pink-500 to-purple-600';
            case 'whatsapp': return 'from-green-500 to-emerald-600';
            case 'tiktok': return 'from-slate-800 to-black';
            default: return 'from-gray-600 to-gray-700';
        }
    };

    const Icon = getIcon(account.platform);
    const gradient = getGradient(account.platform);

    return (
        <motion.button
            whileHover={{ y: -2 }}
            whileTap={{ scale: 0.98 }}
            onClick={onClick}
            className={`relative min-w-[200px] p-4 rounded-xl text-left transition-all overflow-hidden ${isSelected
                ? 'ring-2 ring-purple-500 ring-offset-2 ring-offset-dark-950 bg-white/10'
                : 'bg-white/5 hover:bg-white/10'
                }`}
        >
            <div className="flex items-center gap-3 mb-3">
                {account.profile_picture ? (
                    <img
                        src={account.profile_picture}
                        alt={account.name}
                        className="w-10 h-10 rounded-lg object-cover ring-2 ring-white/10"
                        onError={(e) => { e.target.style.display = 'none'; e.target.nextSibling.style.display = 'flex'; }}
                    />
                ) : null}

                <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${gradient} flex items-center justify-center ${account.profile_picture ? 'hidden' : ''}`}>
                    <Icon className="w-5 h-5 text-white" />
                </div>
                <div className={`w-2 h-2 rounded-full ${account.status === 'connected' ? 'bg-green-500' : 'bg-red-500'}`} />
            </div>

            <div className="space-y-1">
                <h3 className="font-semibold text-white truncate pr-2" title={account.name}>
                    {account.name || t('social.accounts.unnamed')}
                </h3>
                <p className="text-xs text-gray-400 font-mono truncate">
                    {t('social.accounts.id')}: {account.account_id || 'N/A'}
                </p>
            </div>

            {/* Background decoration */}
            <Icon className="absolute -right-4 -bottom-4 w-24 h-24 text-white/5 -rotate-12 pointer-events-none" />
        </motion.button>
    );
}
