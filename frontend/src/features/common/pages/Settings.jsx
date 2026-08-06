import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Settings as SettingsIcon, User, Bell, Palette, Globe, Shield, CreditCard, Users, LogOut
} from 'lucide-react';
import { useAuthStore } from '../../../store/authStore';
import useThemeStore from '../../../store/themeStore';
import { useTranslation } from '../../../lib/translations';
import Button from '../../../components/ui/Button';
import TeamManagement from '../../../components/TeamManagement';
import PermissionGate from '../../../components/PermissionGate';

/* Sub-components */
const ThemeSelector = () => {
  const { theme, setTheme } = useThemeStore();
  const themes = [
    { id: 'dark-modern', name: 'Dark Modern', bg: 'bg-[#0a0a0f]' },
    { id: 'dark-elegance', name: 'Dark Elegance', bg: 'bg-black' },
    { id: 'light-classic', name: 'Light Classic', bg: 'bg-gray-50' },
    { id: 'light-vibrant', name: 'Light Vibrant', bg: 'bg-white' },
  ];

  const { t } = useTranslation();
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-medium text-primary">{t('settings.theme')}</h3>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {themes.map((themeOption) => (
          <button
            key={themeOption.id}
            onClick={() => setTheme(themeOption.id)}
            className={`group relative p-4 rounded-xl border transition-all ${theme === themeOption.id
              ? 'border-accent-500 ring-2 ring-accent-500/20'
              : 'border-border hover:border-gray-500'
              } overflow-hidden`}
          >
            <div className={`absolute inset-0 opacity-20 ${themeOption.bg}`} />
            <div className="relative z-10 flex flex-col items-center gap-3">
              <div className={`w-full h-24 rounded-lg shadow-inner ${themeOption.bg} border border-border/50 flex items-center justify-center`}>
                <div className="w-8 h-8 rounded-full bg-accent-500/20 flex items-center justify-center text-accent-500">
                  <Palette className="w-4 h-4" />
                </div>
              </div>
              <span className="font-medium text-primary">{t('settings.themes.' + themeOption.id.replace('-', '_')) || themeOption.name}</span>
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
      <h3 className="text-lg font-medium text-primary">Language / اللغة</h3>
      <div className="flex gap-4">
        <button
          onClick={() => setLanguage('en')}
          className={`flex-1 p-4 rounded-xl border flex items-center justify-center gap-3 transition-all ${language === 'en'
            ? 'bg-accent-500 text-white border-accent-500'
            : 'bg-surface border-border hover:bg-surface-hover text-secondary'
            }`}
        >
          <span className="text-xl">🇺🇸</span>
          <span className="font-medium">English</span>
        </button>

        <button
          onClick={() => setLanguage('ar')}
          className={`flex-1 p-4 rounded-xl border flex items-center justify-center gap-3 transition-all ${language === 'ar'
            ? 'bg-accent-500 text-white border-accent-500'
            : 'bg-surface border-border hover:bg-surface-hover text-secondary'
            }`}
        >
          <span className="text-xl">🇸🇦</span>
          <span className="font-medium font-arabic">العربية</span>
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
    { id: 'general', label: t('settings.general'), icon: SettingsIcon, desc: 'Global application preferences' },
    { id: 'appearance', label: t('settings.theme'), icon: Palette, desc: 'Customize look and feel' },
    { id: 'account', label: t('settings.account'), icon: User, desc: 'Manage your profile and security' },
    { id: 'team', label: 'Team Members', icon: Users, desc: 'Manage access and roles' },
    { id: 'billing', label: 'Billing & Plan', icon: CreditCard, desc: 'Subscription and invoices' },
  ];

  return (
    <div className="h-full flex flex-col items-center p-6 max-w-6xl mx-auto w-full">
      {/* Header */}
      <div className="w-full flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3 text-primary">
            <SettingsIcon className="w-8 h-8 text-accent-500" />
            {t('settings.title')}
          </h1>
          <p className="text-secondary mt-1">{t('settings.subtitle')}</p>
        </div>
        <Button
          onClick={logout}
          variant="danger"
          leftIcon={LogOut}
          className="rtl-flip-icon"
        >
          {t('auth.logout') || "Sign Out"}
        </Button>
      </div>

      <div className="w-full grid grid-cols-1 lg:grid-cols-12 gap-8 h-full min-h-0">
        {/* Sidebar Tabs */}
        <div className="lg:col-span-3 space-y-3">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`w-full text-left p-4 rounded-xl transition-all duration-300 border group ${activeTab === tab.id
                ? 'bg-accent-500/10 border-accent-500/50 shadow-[0_0_20px_rgba(14,165,233,0.1)]'
                : 'bg-transparent border-transparent hover:bg-white/5 hover:border-white/10'
                }`}
            >
              <div className="flex items-center gap-3 mb-1">
                <tab.icon className={`w-5 h-5 ${activeTab === tab.id ? 'text-accent-500' : 'text-gray-400 group-hover:text-gray-300'}`} />
                <span className={`font-medium ${activeTab === tab.id ? 'text-white' : 'text-gray-400 group-hover:text-white'}`}>
                  {tab.label}
                </span>
              </div>
              <p className="text-xs text-gray-500 pl-8 group-hover:text-gray-400 transition-colors">
                {tab.desc}
              </p>
            </button>
          ))}
        </div>

        {/* Main Content Area */}
        <div className="lg:col-span-9 glass-card p-8 overflow-y-auto">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-8"
            >
              {activeTab === 'appearance' && (
                <>
                  <ThemeSelector />
                  <div className="h-px bg-border" />
                  <LanguageSelector />
                </>
              )}

              {activeTab === 'general' && (
                <div className="space-y-6">
                  <h3 className="text-xl font-bold text-primary">{t('settings.general')}</h3>
                  <p className="text-secondary">{t('settings.subtitle')}</p>

                  <div className="space-y-4">
                    <div className="flex items-center justify-between p-4 bg-surface rounded-xl border border-border">
                      <div className="flex items-center gap-3">
                        <Bell className="w-5 h-5 text-accent-500" />
                        <div>
                          <h4 className="font-medium text-primary">{t('settings.account')}</h4>
                          <p className="text-sm text-secondary">{t('settings.subtitle')}</p>
                        </div>
                      </div>
                      <div className="w-12 h-6 bg-accent-500 rounded-full relative cursor-pointer">
                        <div className="absolute right-1 top-1 w-4 h-4 bg-white rounded-full shadow-sm" />
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'account' && (
                <div className="space-y-6">
                  <div className="flex items-center gap-4 mb-6">
                    <div className="w-20 h-20 rounded-full bg-accent-500 flex items-center justify-center text-3xl font-bold text-white">
                      {user?.name?.[0] || 'U'}
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-primary">{user?.name}</h3>
                      <p className="text-secondary">{user?.email}</p>
                      <span className="inline-block mt-2 px-3 py-1 bg-accent-500/10 text-accent-500 text-xs rounded-full border border-accent-500/20">
                        {user?.role?.toUpperCase() || t('auth.roles.admin')}
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'team' && (
                <TeamManagement />
              )}

              {activeTab === 'billing' && (
                <PermissionGate requiredRole="owner" showLock>
                  <div className="flex flex-col items-center justify-center py-20 text-center">
                    <CreditCard className="w-16 h-16 text-border mb-4" />
                    <h3 className="text-xl font-bold text-primary">Billing Portal</h3>
                    <p className="text-secondary max-w-sm mx-auto mb-6">Manage your subscription, payment methods, and invoices.</p>
                    <Button variant="primary">Manage Subscription</Button>
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
