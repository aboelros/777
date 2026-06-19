import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Building,
    Plus,
    Trash2,
    Calendar,
    Globe,
    CheckCircle,
    AlertCircle
} from 'lucide-react';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';
import GlassCard from '../components/GlassCard';
import { PageLoader } from '../components/LoadingSpinner';
import { useProjectStore } from '../store/projectStore';
import useThemeStore from '../store/themeStore';
import { useTranslation } from '../lib/translations';
import api from '../services/api';
import CreateProjectModal from '../components/CreateProjectModal';

export default function Projects() {
    const navigate = useNavigate();
    const queryClient = useQueryClient();
    const { currentProject, setCurrentProject } = useProjectStore();
    const { t } = useTranslation();
    const [showDeleteModal, setShowDeleteModal] = useState(null); // stores project object to delete
    const [showCreateModal, setShowCreateModal] = useState(false);

    // Fetch projects
    const { data: projects, isLoading } = useQuery({
        queryKey: ['projects'],
        queryFn: () => api.projects.list(),
    });

    // Delete project mutation
    const deleteMutation = useMutation({
        mutationFn: (projectId) => api.projects.delete(projectId),
        onSuccess: () => {
            queryClient.invalidateQueries(['projects']);
            toast.success(t('projects.delete_success'));
            setShowDeleteModal(null);
            // If deleted project was active, switch to another or null
            if (currentProject?.id === showDeleteModal?.id) {
                setCurrentProject(null);
            }
        },
        onError: (error) => {
            toast.error(error.message || t('projects.delete_error'));
        },
    });

    const handleDelete = (project) => {
        setShowDeleteModal(project);
    };

    const confirmDelete = () => {
        if (showDeleteModal) {
            deleteMutation.mutate(showDeleteModal.id);
        }
    };

    if (isLoading) return <PageLoader />;

    return (
        <div className="p-6 space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-4xl font-bold text-white tracking-tight">{t('projects.title')}</h1>
                    <p className="text-gray-400 mt-2 text-lg font-light tracking-wide">{t('projects.description')}</p>
                </div>
                <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => setShowCreateModal(true)}
                    className="btn-starlight flex items-center gap-2"
                >
                    <Plus className="w-4 h-4" />
                    {t('projects.create_new')}
                </motion.button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {projects?.map((project, index) => {
                    const isActive = currentProject?.id === project.id;
                    return (
                        <motion.div
                            key={project.id}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.1 }}
                        >
                            <GlassCard className={`p-0 h-full flex flex-col relative group transition-all duration-500 overflow-visible ${isActive ? 'shadow-[0_0_30px_-5px_rgba(14,165,233,0.15)] scale-[1.02]' : 'hover:scale-[1.01]'}`}>
                                {/* Active Border Gradient */}
                                {isActive && (
                                    <div className="absolute inset-0 rounded-2xl p-[1px] bg-gradient-to-br from-[#D4AF37] via-[#FCF6BA] to-[#AA771C] -z-10 opacity-70" />
                                )}

                                {/* Card Content Container */}
                                <div className={`h-full flex flex-col rounded-2xl bg-[#080808] ${isActive ? 'bg-[#050505]' : ''} p-6 relative overflow-hidden`}>

                                    {/* Abstract Background Decoration */}
                                    <div className="absolute top-0 right-0 w-32 h-32 bg-accent-primary/5 rounded-full blur-3xl transform translate-x-10 -translate-y-10 group-hover:bg-accent-primary/10 transition-colors duration-500" />

                                    <div className="flex items-start justify-between mb-6 relative z-10">
                                        <div className="flex items-center gap-4">
                                            <div className={`w-14 h-14 rounded-2xl flex items-center justify-center border border-white/5 shadow-2xl transition-all duration-500 group-hover:shadow-[0_0_20px_-5px_rgba(14,165,233,0.3)] ${isActive ? 'bg-gradient-to-br from-[#D4AF37] to-[#AA771C] text-black border-none' : 'bg-white/5 text-gray-500 group-hover:text-[#D4AF37]'}`}>
                                                <Building className={`w-6 h-6 ${isActive ? 'drop-shadow-[0_2px_4px_rgba(0,0,0,0.2)]' : ''}`} />
                                            </div>
                                            <div>
                                                <h3 className={`font-bold text-xl tracking-tight transition-colors ${isActive ? 'text-gradient-neon' : 'text-gray-200 group-hover:text-white'}`}>
                                                    {project.name}
                                                </h3>
                                                <p className="text-[10px] text-gray-500 font-mono mt-1 tracking-widest uppercase">
                                                    ID: {project.project_code || 'LEGACY-001'}
                                                </p>
                                            </div>
                                        </div>
                                        {isActive && (
                                            <motion.div
                                                initial={{ scale: 0 }}
                                                animate={{ scale: 1 }}
                                                className="px-3 py-1 rounded-full bg-accent-primary/10 border border-accent-primary/20 text-[#D4AF37] text-[10px] font-bold tracking-widest uppercase flex items-center gap-1.5 shadow-[0_0_10px_rgba(14,165,233,0.2)] shadow-glow"
                                            >
                                                <div className="w-1.5 h-1.5 rounded-full bg-[#D4AF37] animate-pulse" />
                                                Active
                                            </motion.div>
                                        )}
                                    </div>

                                    <div className="space-y-4 mb-8 flex-1 relative z-10">
                                        <div className="flex items-center gap-3 text-sm text-gray-500 group-hover:text-gray-400 transition-colors">
                                            <div className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center">
                                                <Globe className="w-4 h-4 opacity-50" />
                                            </div>
                                            <span className="font-medium">{project.timezone || 'UTC'}</span>
                                        </div>
                                        <div className="flex items-center gap-3 text-sm text-gray-500 group-hover:text-gray-400 transition-colors">
                                            <div className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center">
                                                <Calendar className="w-4 h-4 opacity-50" />
                                            </div>
                                            <span className="font-medium">est. {new Date(project.created_at).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })}</span>
                                        </div>
                                    </div>

                                    <div className="flex items-center gap-3 pt-4 border-t border-white/5 relative z-10">
                                        <motion.button
                                            whileHover={{ scale: 1.02 }}
                                            whileTap={{ scale: 0.98 }}
                                            onClick={() => {
                                                setCurrentProject(project);
                                                toast.success(`${t('projects.switched_to')} ${project.name}`);
                                            }}
                                            disabled={isActive}
                                            className={`flex-1 h-10 rounded-lg text-xs font-bold uppercase tracking-widest transition-all ${isActive
                                                ? 'bg-transparent text-gray-500 cursor-default opacity-50'
                                                : 'bg-white/5 hover:bg-white/10 text-gray-300 hover:text-white border border-white/5 hover:border-white/10'
                                                }`}
                                        >
                                            {isActive ? 'Current Session' : 'Access Project'}
                                        </motion.button>
                                        <motion.button
                                            whileHover={{ scale: 1.05, rotate: 5 }}
                                            whileTap={{ scale: 0.95 }}
                                            onClick={() => handleDelete(project)}
                                            className="w-10 h-10 rounded-lg bg-red-500/5 hover:bg-red-500/10 border border-red-500/10 text-red-400/50 hover:text-red-400 transition-all flex items-center justify-center"
                                        >
                                            <Trash2 className="w-4 h-4" />
                                        </motion.button>
                                    </div>
                                </div>
                            </GlassCard>
                        </motion.div>
                    );
                })}
            </div>

            {/* Delete Confirmation Modal */}
            <AnimatePresence>
                {showDeleteModal && (
                    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.95 }}
                            className="glass-card p-6 max-w-md w-full rounded-2xl border border-red-500/30"
                        >
                            <div className="flex items-center gap-3 mb-4 text-red-400">
                                <AlertCircle className="w-8 h-8" />
                                <h2 className="text-xl font-semibold">{t('projects.delete_confirm_title')}</h2>
                            </div>
                            <p className="text-gray-300 mb-6">
                                {t('projects.delete_confirm_desc')}
                            </p>
                            <div className="flex gap-3">
                                <button
                                    onClick={() => setShowDeleteModal(null)}
                                    className="flex-1 px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 transition-colors"
                                >
                                    {t('common.cancel')}
                                </button>
                                <button
                                    onClick={confirmDelete}
                                    disabled={deleteMutation.isPending}
                                    className="flex-1 px-4 py-2 rounded-xl bg-red-500 hover:bg-red-600 transition-colors font-medium flex items-center justify-center gap-2"
                                >
                                    {deleteMutation.isPending ? t('projects.creating').replace('Creating', 'Deleting') : t('projects.switch').replace('Switch', 'Delete')}
                                </button>
                            </div>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>

            <CreateProjectModal
                isOpen={showCreateModal}
                onClose={() => setShowCreateModal(false)}
            />
        </div>
    );
}
