import React, { useState } from 'react';
import { Search, LogOut } from 'lucide-react';
import { motion } from 'framer-motion';
import { useAuthStore } from '@/store/authStore';
import { useTranslation } from '@/lib/translations';
import ProjectSelector from '@/components/header/ProjectSelector';
import NotificationBell from '@/components/header/NotificationBell';
import CreateProjectModal from '@/components/CreateProjectModal';

/**
 * Standardized Automio Application Shell Header
 */
export default function Header() {
  const { user, logout } = useAuthStore();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const { t } = useTranslation();

  return (
    <header className="px-6 py-3 relative z-30 bg-[#060a16]/75 backdrop-blur-2xl border-b border-white/10 select-none shadow-[0_4px_30px_rgba(0,0,0,0.35)]">
      {/* Specular Rim Light */}
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/20 to-transparent pointer-events-none" />

      <div className="flex items-center justify-between gap-4">
        {/* Global Search Input */}
        <div className="flex-1 max-w-md">
          <div className="relative group">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 group-focus-within:text-sky-400 transition-colors pointer-events-none" aria-hidden="true" />
            <input
              type="search"
              aria-label="Search Automio"
              placeholder={t('inbox.search_placeholder') || "Search across conversations, orders, customers..."}
              className="w-full bg-[#0c1326]/70 border border-white/10 rounded-xl pl-10 pr-4 py-2 text-xs text-white placeholder:text-slate-500 focus:bg-[#0f1733]/90 focus:border-sky-400/60 focus:ring-2 focus:ring-sky-500/25 transition-all duration-200 outline-none backdrop-blur-md shadow-[inset_0_1px_2px_rgba(0,0,0,0.4)]"
            />
          </div>
        </div>

        {/* Right Action Cluster */}
        <div className="flex items-center gap-3">
          {/* Project Workspace Selector */}
          <ProjectSelector onCreateClick={() => setShowCreateModal(true)} />

          {/* Notifications */}
          <NotificationBell />

          {/* User Profile & Session Controls */}
          <div className="pl-3 border-l border-white/10 flex items-center gap-3">
            <div className="text-right hidden sm:block leading-tight">
              <p className="text-xs font-semibold text-white truncate max-w-[120px]">
                {user?.name || t('auth.roles.admin')}
              </p>
              <p className="text-[10px] text-slate-400 tracking-wider uppercase">
                {user?.role || 'Administrator'}
              </p>
            </div>

            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-sky-400 via-blue-500 to-indigo-500 p-0.5 shadow-[0_0_12px_rgba(56,189,248,0.35)]">
              <div className="w-full h-full rounded-[10px] bg-[#070b18] flex items-center justify-center">
                <span className="text-xs font-bold text-sky-400">
                  {user?.name?.charAt(0) || user?.email?.charAt(0) || 'A'}
                </span>
              </div>
            </div>

            <motion.button
              type="button"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={logout}
              title={t('auth.logout') || "Sign Out"}
              aria-label={t('auth.logout') || "Sign Out"}
              className="w-8 h-8 rounded-xl bg-white/[0.05] border border-white/10 flex items-center justify-center text-slate-400 hover:text-rose-400 hover:border-rose-500/40 hover:bg-rose-500/10 backdrop-blur-md transition-colors"
            >
              <LogOut className="w-3.5 h-3.5" />
            </motion.button>
          </div>
        </div>
      </div>

      {/* Standalone Create Project Modal */}
      <CreateProjectModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
      />
    </header>
  );
}
