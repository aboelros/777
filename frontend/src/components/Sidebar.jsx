import React from 'react';
import { NavLink } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  LayoutDashboard,
  Plug,
  Bot,
  ShoppingCart,
  MessageSquare,
  BarChart3,
  Settings,
  Package,
  GraduationCap,
  Hash,
  Info,
  Activity,
  CreditCard,
  Building,
  Trello,
  GitBranch,
  ExternalLink,
  ShieldCheck
} from 'lucide-react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { useAuthStore } from '@/store/authStore';
import { useProjectStore } from '@/store/projectStore';
import { useTranslation } from '@/lib/translations';
import Logo from '@/components/brand/Logo';
import api from '@/services/api';

/**
 * Standardized Automio Shell Navigation Sidebar
 */
export default function Sidebar() {
  const { currentProject } = useProjectStore();
  const { user } = useAuthStore();
  const { t } = useTranslation();
  const isAdmin = user?.role === 'admin';

  // Fetch AI usage statistics
  const { data: stats } = useQuery({
    queryKey: ['ai-usage-stats', currentProject?.id],
    queryFn: async () => {
      if (!currentProject) return null;
      const [messageStats, usageStats] = await Promise.all([
        api.messages.stats(currentProject.id),
        api.assistant.usage(currentProject.id)
      ]);
      return { ...messageStats, ...usageStats };
    },
    enabled: !!currentProject?.id,
    refetchInterval: 30000,
  });

  const aiUsagePercent = stats ? Math.round(stats.automation_rate || 0) : 0;
  const aiGeneratedMessages = stats?.ai_generated_messages || 0;
  const totalMessages = stats?.total_messages || 0;

  const navigation = [
    { name: t('sidebar.dashboard'), to: '/', icon: LayoutDashboard },
    { name: t('sidebar.projects'), to: '/projects', icon: Building },
    { name: t('sidebar.integrations'), to: '/integrations', icon: Plug },
    { name: t('sidebar.pipeline'), to: '/deals', icon: Trello },
    { name: t('sidebar.ai_assistant'), to: '/assistant', icon: Bot },
    { name: t('sidebar.orders'), to: '/orders', icon: ShoppingCart },
    { name: t('sidebar.inbox'), to: '/inbox', icon: MessageSquare },
    { name: t('sidebar.products'), to: '/products', icon: Package },
    { name: t('sidebar.training'), to: '/bot-training', icon: GraduationCap },
    { name: t('sidebar.social'), to: '/social-media', icon: Hash },
    { name: t('sidebar.campaigns'), to: '/campaigns', icon: GitBranch },
    { name: t('sidebar.payments'), to: '/payments', icon: CreditCard },
    { name: t('sidebar.reports'), to: '/reports', icon: BarChart3 },
    { name: t('sidebar.usage'), to: '/usage', icon: Activity },
    { name: t('sidebar.subscription'), to: '/subscription', icon: CreditCard },
    { name: t('sidebar.settings'), to: '/settings', icon: Settings },
    { name: t('sidebar.about'), to: '/about', icon: Info },
  ];

  return (
    <aside
      className="w-64 bg-[#050814]/80 backdrop-blur-2xl flex flex-col relative z-20 border-r border-white/10 select-none flex-shrink-0 shadow-[4px_0_30px_rgba(0,0,0,0.5)]"
      aria-label="Application sidebar"
    >
      {/* Brand Header */}
      <div className="p-5 pb-3 border-b border-white/10 relative">
        <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-sky-500/25 to-transparent pointer-events-none" />
        <NavLink to="/" className="inline-block focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-500/50 rounded-xl">
          <Logo variant="full" size={34} subtitle="AI SALES PLATFORM" />
        </NavLink>
      </div>

      {/* Navigation List */}
      <nav className="flex-1 overflow-y-auto px-3 space-y-1 custom-scrollbar py-3" aria-label="Main navigation">
        {isAdmin && (
          <a
            href={import.meta.env.VITE_ADMIN_PANEL_URL || 'http://localhost:5174'}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center justify-between px-3.5 py-2.5 rounded-xl transition-all duration-200 group text-sm font-semibold text-indigo-300 bg-gradient-to-r from-indigo-500/20 via-purple-500/10 to-transparent border border-indigo-400/40 shadow-[0_0_16px_rgba(99,102,241,0.25)] mb-2.5"
          >
            <div className="flex items-center gap-3">
              <ShieldCheck className="w-5 h-5 text-indigo-400" />
              <span>Admin Commander</span>
            </div>
            <ExternalLink className="w-3.5 h-3.5 text-indigo-400/70" />
          </a>
        )}
        {navigation.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition-all duration-200 group relative text-sm',
                isActive
                  ? 'text-white bg-gradient-to-r from-sky-500/20 via-blue-500/10 to-transparent font-semibold border border-sky-400/30 shadow-[0_0_16px_rgba(56,189,248,0.2)]'
                  : 'text-slate-400 hover:text-white hover:bg-white/[0.06] font-medium border border-transparent'
              )
            }
          >
            {({ isActive }) => (
              <>
                <item.icon
                  className={cn(
                    "w-4 h-4 flex-shrink-0 transition-colors duration-200",
                    isActive ? "text-sky-400 drop-shadow-[0_0_8px_rgba(56,189,248,0.6)]" : "text-slate-500 group-hover:text-slate-200"
                  )}
                  aria-hidden="true"
                />
                <span className="truncate">
                  {item.name}
                </span>
                {isActive && (
                  <span className="ml-auto w-1.5 h-1.5 rounded-full bg-sky-400 shadow-[0_0_8px_rgba(56,189,248,0.9)] animate-pulse" aria-hidden="true" />
                )}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Usage Footer Widget - Liquid Glass Card */}
      <div className="p-3 border-t border-white/10 bg-[#050814]/60">
        <div className="p-3.5 rounded-xl bg-gradient-to-b from-white/[0.07] to-white/[0.02] border border-white/10 shadow-[inset_0_1px_1px_rgba(255,255,255,0.15)] backdrop-blur-md">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">{t('sidebar.usage')}</span>
            <span className="text-xs font-mono font-bold text-sky-400">
              {aiUsagePercent}%
            </span>
          </div>

          <div className="h-1.5 bg-slate-900/80 rounded-full overflow-hidden border border-white/5">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${aiUsagePercent}%` }}
              transition={{ duration: 1.2, ease: "easeOut" }}
              className="h-full bg-gradient-to-r from-sky-400 via-blue-500 to-indigo-500 rounded-full shadow-[0_0_8px_rgba(56,189,248,0.6)]"
            />
          </div>

          <div className="flex items-center justify-between mt-2.5 pt-2 border-t border-white/5 text-[10px] text-slate-400 font-mono">
            <span className="flex items-center gap-1.5">
              <Activity className="w-3 h-3 text-sky-400" aria-hidden="true" />
              <span>{aiGeneratedMessages} / {totalMessages} OPS</span>
            </span>
            <a
              href="https://automio.online"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sky-400 hover:text-sky-300 transition-colors flex items-center gap-1"
              title="Visit Automio Official Website"
            >
              automio.online
              <ExternalLink className="w-2.5 h-2.5" />
            </a>
          </div>
        </div>
      </div>
    </aside>
  );
}
