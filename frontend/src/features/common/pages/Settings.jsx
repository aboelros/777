import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Settings as SettingsIcon, User, Bell, Palette, CreditCard, Users, LogOut
} from 'lucide-react';
import { useAuthStore } from '@/store/authStore';
import useThemeStore from '@/store/themeStore';
import { useTranslation } from '@/lib/translations';
import Button from '@/components/ui/Button';
import TeamManagement from '@/components/TeamManagement';
import PermissionGate from '@/components/PermissionGate';

const ThemeSelector = () => {
  const { theme, setTheme } = useThemeStore();
  const { t } = useTranslation();

  const themes = [
    { id: 'dark-modern', name: 'Dark Modern', bg: 'bg-[#0a0d14]' },
    { id: 'dark-elegance', name: 'Dark Elegance', bg: 'bg-black' },
    { id: 'light-classic', name: 'Light Classic', bg: 'bg-gray-50' },
    { id: 'light-vibrant', name: 'Light Vibrant', bg: 'bg-white' },
  ];

  return (
    <div className="space-y-4">
      <h3 className="text-base font-bold text-text-primary">{t('settings.theme') || 'Visual Theme'}</h3>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {themes.map((themeOption) => (
          <button
            key={themeOption.id}
            onClick={() => setTheme(themeOption.id)}
            className={`group relative p-4 rounded-2xl border transition-all ${
              theme === themeOption.id
                ? 'border-brand-primary ring-2 ring-brand-primary/20 bg-surface'
                : 'border-border hover:border-text-muted bg-surface-subtle'
            } overflow-hidden`}
          >
            <div className="flex flex-col items-center gap-3">
              <div className={`w-full h-20 rounded-xl ${themeOption.bg} border border-border flex items-center justify-center`}>
                <div className="w-8 h-8 rounded-full bg-brand-primary/20 flex items-center justify-center text-brand-primary">
                  <Palette className="w-4 h-4" />
                </div>
              </div>
              <span className="font-semibold text-xs text-text-primary">
                {themeOption.name}
              </span>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};

const LanguageSelector = () => {
  const { language, setLanguage } = useThemeStore();

  return (
    <div className="space-y-4">
      <h3 className="text-base font-bold text-text-primary">Platform Language / اللغة</h3>
      <div className="flex gap-4">
        <button
          onClick={() => setLanguage('en')}
          className={`flex-1 p-4 rounded-xl border flex items-center justify-center gap-3 transition-all ${
            language === 'en'
              ? 'bg-brand-primary text-white border-brand-primary shadow-sm'
              : 'bg-surface-subtle border-border hover:bg-surface-hover text-text-secondary'
          }`}
        >
          <span className="text-xl">🇺🇸</span>
          <span className="font-semibold text-sm">English</span>
        </button>

        <button
          onClick={() => setLanguage('ar')}
          className={`flex-1 p-4 rounded-xl border flex items-center justify-center gap-3 transition-all ${
            language === 'ar'
              ? 'bg-brand-primary text-white border-brand-primary shadow-sm'
              : 'bg-surface-subtle border-border hover:bg-surface-hover text-text-secondary'
          }`}
        >
          <span className="text-xl">🇸🇦</span>
          <span className="font-semibold text-sm font-arabic">العربية</span>
        </button>
      </div>
    </div>
  );
};

export default function Settings() {
  const { user, logout } = useAuthStore();
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState('general');

  const tabs = [
    { id: 'general', label: t('settings.general') || 'General', icon: SettingsIcon, desc: 'Global application preferences' },
    { id: 'appearance', label: t('settings.theme') || 'Appearance', icon: Palette, desc: 'Themes and typography' },
    { id: 'account', label: t('settings.account') || 'Account', icon: User, desc: 'Profile and security credentials' },
    { id: 'team', label: 'Team Members', icon: Users, desc: 'Access and roles' },
    { id: 'billing', label: 'Billing & Plan', icon: CreditCard, desc: 'Subscription and invoices' },
  ];

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-border">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3 text-text-primary tracking-tight">
            <span className="p-2.5 rounded-xl bg-brand-primary/10 border border-brand-primary/20 text-brand-primary">
              <SettingsIcon className="w-6 h-6" />
            </span>
            {t('settings.title')}
          </h1>
          <p className="text-sm text-text-secondary mt-1">{t('settings.subtitle')}</p>
        </div>
        <Button onClick={logout} variant="danger" leftIcon={LogOut}>
          {t('auth.logout') || 'Sign Out'}
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Navigation Tabs */}
        <div className="lg:col-span-4 space-y-2">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`w-full text-left p-3.5 rounded-2xl transition-all border ${
                activeTab === tab.id
                  ? 'bg-brand-primary/10 border-brand-primary/40 text-text-primary'
                  : 'bg-surface-subtle border-border text-text-secondary hover:bg-surface-hover hover:text-text-primary'
              }`}
            >
              <div className="flex items-center gap-2.5 mb-0.5">
                <tab.icon className={`w-4 h-4 ${activeTab === tab.id ? 'text-brand-primary' : 'text-text-muted'}`} />
                <span className="font-semibold text-sm">{tab.label}</span>
              </div>
              <p className="text-xs text-text-muted pl-6">{tab.desc}</p>
            </button>
          ))}
        </div>

        {/* Content Pane */}
        <div className="lg:col-span-8 glass-card p-6 rounded-2xl border border-border">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="space-y-6"
            >
              {activeTab === 'appearance' && (
                <>
                  <ThemeSelector />
                  <div className="h-px bg-border my-6" />
                  <LanguageSelector />
                </>
              )}

              {activeTab === 'general' && (
                <div className="space-y-4">
                  <h3 className="text-lg font-bold text-text-primary">{t('settings.general')}</h3>
                  <div className="p-4 bg-surface-subtle rounded-xl border border-border flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Bell className="w-5 h-5 text-brand-primary" />
                      <div>
                        <h4 className="font-semibold text-sm text-text-primary">System Notifications</h4>
                        <p className="text-xs text-text-muted">Receive alerts on new orders and failed webhooks</p>
                      </div>
                    </div>
                    <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      Enabled
                    </span>
                  </div>
                </div>
              )}

              {activeTab === 'account' && (
                <div className="space-y-4">
                  <h3 className="text-lg font-bold text-text-primary">{t('settings.account')}</h3>
                  <div className="flex items-center gap-4 p-4 rounded-xl bg-surface-subtle border border-border">
                    <div className="w-14 h-14 rounded-2xl bg-brand-primary flex items-center justify-center text-xl font-bold text-white">
                      {user?.name?.[0] || 'U'}
                    </div>
                    <div>
                      <h4 className="font-bold text-base text-text-primary">{user?.name || 'Administrator'}</h4>
                      <p className="text-xs text-text-muted">{user?.email || 'admin@automio.online'}</p>
                      <span className="inline-block mt-2 px-2.5 py-0.5 bg-brand-primary/10 text-brand-primary text-xs rounded-full font-mono border border-brand-primary/20">
                        {user?.role?.toUpperCase() || 'OWNER'}
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'team' && <TeamManagement />}

              {activeTab === 'billing' && (
                <PermissionGate requiredRole="owner" showLock>
                  <div className="flex flex-col items-center justify-center py-16 text-center space-y-3">
                    <CreditCard className="w-12 h-12 text-brand-primary opacity-80" />
                    <h3 className="text-lg font-bold text-text-primary">Enterprise Billing Portal</h3>
                    <p className="text-xs text-text-secondary max-w-sm">Manage payment cards, invoice records, and team seat allocations.</p>
                    <Button variant="primary">Manage Subscription via Stripe</Button>
                  </div>
                </PermissionGate>
              )}
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
