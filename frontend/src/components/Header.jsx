import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Bell, Search, ChevronDown, LogOut, Check, Plus } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'sonner';
import { useAuthStore } from '../store/authStore';
import { useProjectStore } from '../store/projectStore';
import api from '../services/api';
import { useTranslation } from '../lib/translations';

export default function Header() {
  const { user, logout } = useAuthStore();
  const { currentProject, setCurrentProject } = useProjectStore();
  const [showProjectMenu, setShowProjectMenu] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [newProjectName, setNewProjectName] = useState('');
  const [newProjectCode, setNewProjectCode] = useState('');
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { t } = useTranslation();

  // Fetch all projects
  const { data: projectsData } = useQuery({
    queryKey: ['projects'],
    queryFn: async () => {
      return await api.projects.list();
    },
  });

  const projects = projectsData || [];

  // Fetch message stats for notifications
  const { data: messageStats } = useQuery({
    queryKey: ['message-stats', currentProject?.id],
    queryFn: async () => {
      if (!currentProject?.id) return null;
      return await api.messages.stats(currentProject.id);
    },
    enabled: !!currentProject?.id,
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  const unreadCount = messageStats?.unread_messages || 0;

  // Auto-generate project code from name
  const generateProjectCode = (name) => {
    const code = name
      .toUpperCase()
      .replace(/[^A-Z0-9]/g, '')
      .substring(0, 10);
    const timestamp = Date.now().toString().slice(-3);
    return `${code}-${timestamp}`;
  };

  // Create project mutation
  const createProjectMutation = useMutation({
    mutationFn: async ({ name, code }) => {
      return await api.projects.create({
        project_code: code,
        name,
        description: '',
        timezone: 'UTC'
      });
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries(['projects']);
      setCurrentProject(data);
      setShowCreateModal(false);
      setNewProjectName('');
      setNewProjectCode('');
      toast.success(t('common.save'));
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || t('common.error'));
    },
  });

  const handleCreateProject = (e) => {
    e.preventDefault();
    if (newProjectName.trim()) {
      const code = generateProjectCode(newProjectName);
      createProjectMutation.mutate({
        name: newProjectName.trim(),
        code
      });
    }
  };

  return (
    <motion.header
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className="px-8 py-4 relative z-50 bg-dark-900/50 backdrop-blur-md border-b border-white/5"
    >
      <div className="flex items-center justify-between p-2 pl-0">
        {/* Search */}
        <div className="flex-1 max-w-xl">
          <div className="relative group">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500 group-hover:text-accent-400 transition-colors" />
            <input
              type="text"
              placeholder={t('inbox.search_placeholder')}
              className="w-full bg-black/20 border border-white/5 rounded-xl pl-12 py-2.5 text-sm focus:bg-black/40 focus:border-accent-500/30 focus:ring-1 focus:ring-accent-500/30 transition-all duration-300 placeholder:text-gray-700 font-medium"
            />
          </div>
        </div>

        {/* Right Section */}
        <div className="flex items-center gap-6">
          {/* Project Selector */}
          <div className="relative">
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => {
                setShowProjectMenu(!showProjectMenu);
                setShowNotifications(false);
              }}
              className="glass-panel px-4 py-2 rounded-xl flex items-center gap-3 border-white/5 hover:border-accent-500/20 transition-all duration-300 bg-black/40 shadow-sm"
            >
              <div className={`w-2 h-2 rounded-full ${currentProject ? 'bg-accent-500 shadow-[0_0_8px_rgba(212,175,55,0.6)]' : 'bg-gray-600'}`} />
              <span className="text-sm font-semibold tracking-wide text-gray-200">
                {currentProject ? currentProject.name : t('projects.select_project')}
              </span>
              <ChevronDown className="w-3.5 h-3.5 text-gray-500" />
            </motion.button>
            <AnimatePresence>
              {showProjectMenu && (
                <motion.div
                  initial={{ opacity: 0, y: 10, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 10, scale: 0.95 }}
                  className="absolute right-0 mt-3 w-72 glass-panel rounded-2xl p-2 z-[1000] border border-white/10 shadow-2xl bg-[#0a0a0a]/95 backdrop-blur-3xl origin-top-right"
                >
                  <div className="px-3 py-2 text-[10px] font-bold text-gray-500 uppercase tracking-widest">Projects</div>
                  {projects.map((project) => (
                    <motion.button
                      key={project.id}
                      whileHover={{ x: 4, backgroundColor: 'rgba(255,255,255,0.03)' }}
                      onClick={() => {
                        setCurrentProject(project);
                        setShowProjectMenu(false);
                      }}
                      className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl transition-all mb-1 ${currentProject?.id === project.id ? 'bg-accent-500/5 text-accent-400' : 'text-gray-400'
                        }`}
                    >
                      <span className="text-sm font-medium">{project.name}</span>
                      {currentProject?.id === project.id && (
                        <Check className="w-3.5 h-3.5 text-accent-400" />
                      )}
                    </motion.button>
                  ))}
                  <div className="border-t border-white/5 my-2" />
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    onClick={() => {
                      setShowCreateModal(true);
                      setShowProjectMenu(false);
                    }}
                    className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-accent-600 text-black hover:bg-accent-500 transition-all shadow-lg shadow-accent-500/20"
                  >
                    <Plus className="w-4 h-4" />
                    <span className="text-sm font-bold">{t('projects.add')}</span>
                  </motion.button>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Notifications */}
          <div className="relative">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => {
                setShowNotifications(!showNotifications);
                setShowProjectMenu(false);
              }}
              className={`relative w-10 h-10 rounded-full flex items-center justify-center transition-all duration-300 ${showNotifications ? 'bg-accent-500 text-black shadow-[0_0_15px_rgba(212,175,55,0.4)]' : 'bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white'}`}
            >
              <Bell className="w-4.5 h-4.5" />
              {unreadCount > 0 && (
                <span className="absolute -top-0.5 -right-0.5 w-3.5 h-3.5 bg-red-500 rounded-full text-[9px] font-bold flex items-center justify-center border-2 border-black">
                  {unreadCount > 9 ? '9+' : unreadCount}
                </span>
              )}
            </motion.button>
            <AnimatePresence>
              {showNotifications && (
                <motion.div
                  initial={{ opacity: 0, y: 10, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 10, scale: 0.95 }}
                  className="absolute right-0 mt-3 w-80 glass-panel rounded-2xl p-0 z-[1000] border border-white/10 shadow-2xl bg-[#0a0a0a]/95 backdrop-blur-3xl overflow-hidden origin-top-right"
                >
                  <div className="p-4 border-b border-white/5 flex items-center justify-between bg-white/2">
                    <h3 className="font-bold text-xs uppercase tracking-widest text-gray-400">{t('sidebar.intelligence')}</h3>
                  </div>
                  <div className="max-h-[300px] overflow-y-auto custom-scrollbar">
                    {unreadCount > 0 ? (
                      <div className="p-2 space-y-1">
                        <div
                          className="flex items-start gap-3 p-3 rounded-xl hover:bg-white/5 cursor-pointer transition-colors group"
                          onClick={() => {
                            navigate('/messages');
                            setShowNotifications(false);
                          }}
                        >
                          <div className="w-10 h-10 rounded-full bg-accent-500/10 flex items-center justify-center flex-shrink-0 group-hover:bg-accent-500/20 transition-colors">
                            <Bell className="w-4 h-4 text-accent-400" />
                          </div>
                          <div>
                            <p className="text-sm font-medium text-gray-200 group-hover:text-white transition-colors">{t('inbox.empty.select_desc')}</p>
                            <p className="text-[10px] text-gray-500 mt-0.5 uppercase tracking-wide">{t('inbox.chat.intelligence')}</p>
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="p-12 text-center text-gray-500">
                        <div className="w-12 h-12 rounded-full bg-white/5 flex items-center justify-center mx-auto mb-4 border border-white/5">
                          <Bell className="w-5 h-5 opacity-30" />
                        </div>
                        <p className="text-xs font-medium uppercase tracking-wide opacity-60">{t('inbox.empty.no_conversations')}</p>
                      </div>
                    )}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* User Menu */}
          <div className="pl-6 border-l border-white/10">
            <div className="flex items-center gap-4 cursor-pointer group">
              <div className="text-right hidden md:block">
                <p className="text-sm font-bold text-white group-hover:text-accent-400 transition-colors">{user?.name || t('auth.roles.admin')}</p>
                <p className="text-[10px] text-gray-500 uppercase tracking-widest">{user?.role || 'Administrator'}</p>
              </div>
              <div className="w-10 h-10 rounded-full p-[1px] bg-gradient-to-br from-accent-500 to-gray-800 shadow-lg shadow-accent-500/10 group-hover:shadow-accent-500/30 transition-all duration-300">
                <div className="w-full h-full rounded-full bg-black flex items-center justify-center">
                  <span className="text-sm font-bold text-accent-400">
                    {user?.name?.charAt(0) || user?.email?.charAt(0)}
                  </span>
                </div>
              </div>
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={logout}
                className="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center text-gray-500 hover:text-white hover:bg-white/10 transition-all"
              >
                <LogOut className="w-3.5 h-3.5" />
              </motion.button>
            </div>
          </div>
        </div>
      </div>

      {/* Create Project Modal */}
      <AnimatePresence>
        {showCreateModal && (
          <div
            className="fixed inset-0 bg-black/70 backdrop-blur-md flex items-center justify-center z-[9999] p-4"
            onClick={() => setShowCreateModal(false)}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              onClick={(e) => e.stopPropagation()}
              className="glass-card p-8 max-w-md w-full rounded-2xl border border-white/10 shadow-2xl"
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold bg-gradient-to-r from-accent-400 to-purple-400 bg-clip-text text-transparent">
                  {t('projects.add')}
                </h2>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="text-gray-400 hover:text-white transition-colors"
                >
                  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <form onSubmit={handleCreateProject} className="space-y-5">
                {/* Project Name */}
                <div>
                  <label className="block text-sm font-medium mb-2 text-gray-300">
                    {t('projects.name')} <span className="text-accent-400">*</span>
                  </label>
                  <input
                    type="text"
                    value={newProjectName}
                    onChange={(e) => setNewProjectName(e.target.value)}
                    placeholder="My Awesome Store"
                    required
                    className="w-full bg-dark-800/50 border border-white/10 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-transparent transition-all"
                    autoFocus
                  />
                </div>

                {/* Action Buttons */}
                <div className="flex gap-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowCreateModal(false)}
                    className="flex-1 glass-card px-6 py-3 rounded-xl hover:bg-white/10 transition-all font-medium"
                  >
                    {t('common.cancel')}
                  </button>
                  <button
                    type="submit"
                    disabled={createProjectMutation.isLoading || !newProjectName.trim()}
                    className="flex-1 bg-gradient-to-r from-accent-500 to-purple-600 px-6 py-3 rounded-xl hover:from-accent-600 hover:to-purple-700 transition-all font-medium disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-accent-500/30"
                  >
                    {createProjectMutation.isLoading ? (
                      <span className="flex items-center justify-center gap-2">
                        <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                        </svg>
                        {t('reports.controls.generating')}
                      </span>
                    ) : (
                      t('projects.add')
                    )}
                  </button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </motion.header>
  );
}
