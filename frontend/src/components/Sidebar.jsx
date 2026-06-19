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
  Sparkles,
  Package,
  GraduationCap,
  Hash,
  Info,
  Activity,
  CreditCard,
  Building,
  Trello,
  GitBranch
} from 'lucide-react';
import { motion } from 'framer-motion';
import { cn } from '../lib/utils';
import { useProjectStore } from '../store/projectStore';
import { useTranslation } from '../lib/translations';
import api from '../services/api';

export default function Sidebar() {
  const { currentProject } = useProjectStore();
  const { t } = useTranslation();

  // Fetch AI usage stats
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
    <motion.aside
      initial={{ x: -100, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      className="w-72 bg-dark-950 flex flex-col relative z-20 border-r border-white/5 shadow-2xl"
    >
      {/* Golden Glow Effect */}
      <div className="absolute top-0 right-0 w-64 h-64 bg-accent-500/5 rounded-full blur-[100px] pointer-events-none" />

      {/* Logo Area */}
      <div className="p-8 pb-4">
        <div className="flex items-center gap-4 mb-2">
          <div className="relative group">
            <div className="absolute inset-0 bg-accent-500 blur-xl opacity-20 group-hover:opacity-40 transition-opacity duration-500 rounded-full" />
            <div className="relative w-12 h-12 rounded-2xl bg-gradient-to-br from-black to-gray-900 border border-white/10 flex items-center justify-center text-accent-500 shadow-lg group-hover:scale-105 transition-transform duration-500">
              <Sparkles className="w-6 h-6 text-accent-400 drop-shadow-[0_0_8px_rgba(14,165,233,0.5)]" />
            </div>
          </div>
          <div>
            <h1 className="text-xl font-bold text-white tracking-tight">AI Sales</h1>
            <p className="text-[10px] text-accent-400/80 font-bold tracking-[0.2em] uppercase">Enterprise</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto px-4 space-y-1.5 custom-scrollbar py-4" aria-label="Main navigation">
        {navigation.map((item, index) => (
          <motion.div
            key={item.to}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.02 }}
          >
            <NavLink
              to={item.to}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 group relative',
                  isActive
                    ? 'text-white bg-white/5'
                    : 'text-gray-400 hover:text-white hover:bg-white/5'
                )
              }
            >
              {({ isActive }) => (
                <>
                  {isActive && (
                    <motion.div
                      layoutId="activeNav"
                      className="absolute inset-0 border border-accent-500/30 rounded-xl bg-accent-500/5"
                      initial={false}
                      transition={{ type: "spring", stiffness: 350, damping: 30 }}
                    />
                  )}
                  {isActive && (
                    <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-accent-500 rounded-r-full shadow-[0_0_10px_rgba(14,165,233,0.5)]" />
                  )}
                  <item.icon
                    className={cn(
                      "w-5 h-5 relative z-10 transition-colors duration-300",
                      isActive ? "text-accent-400 drop-shadow-[0_0_5px_rgba(14,165,233,0.5)]" : "text-gray-500 group-hover:text-gray-300"
                    )}
                  />
                  <span className={cn(
                    "font-medium relative z-10 text-sm tracking-wide",
                    isActive ? "font-semibold" : ""
                  )}>
                    {item.name}
                  </span>
                </>
              )}
            </NavLink>
          </motion.div>
        ))}
      </nav>

      {/* Bottom Section - AI Usage */}
      <div className="p-4 mt-2">
        <div className="p-5 rounded-2xl bg-gradient-to-b from-white/5 to-transparent border border-white/5 relative overflow-hidden group">
          <div className="absolute inset-0 bg-accent-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

          <div className="flex items-center justify-between mb-3 relative z-10">
            <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">{t('sidebar.usage')}</span>
            <span className="text-xs font-mono font-bold text-accent-400">
              {aiUsagePercent}%
            </span>
          </div>

          <div className="h-1 bg-gray-800 rounded-full overflow-hidden relative z-10">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${aiUsagePercent}%` }}
              transition={{ duration: 1.5, ease: "easeOut" }}
              className="h-full bg-accent-500 shadow-[0_0_10px_rgba(14,165,233,0.5)]"
            />
          </div>

          <div className="flex items-center gap-2 mt-3 text-[10px] text-gray-500 relative z-10 font-mono">
            <Activity className="w-3 h-3" />
            <span>{aiGeneratedMessages} / {totalMessages} OPS</span>
          </div>
        </div>
      </div>
    </motion.aside>
  );
}
