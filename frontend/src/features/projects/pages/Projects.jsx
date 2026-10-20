import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { Building, Plus, Trash2, Calendar, Globe, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';
import api from '@/services/api';
import { useProjectStore } from '@/store/projectStore';
import { useTranslation } from '@/lib/translations';
import GlassCard from '@/components/ui/GlassCard';
import Button from '@/components/ui/Button';
import Badge from '@/components/ui/Badge';
import EmptyState from '@/components/ui/EmptyState';
import { PageLoader } from '@/components/ui/LoadingSpinner';
import CreateProjectModal from '@/components/CreateProjectModal';

/**
 * Standardized Automio Projects & Workspaces Directory
 */
export default function Projects() {
  const queryClient = useQueryClient();
  const { currentProject, setCurrentProject } = useProjectStore();
  const { t } = useTranslation();
  const [showDeleteModal, setShowDeleteModal] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);

  const { data: projectsData, isLoading } = useQuery({
    queryKey: ['projects'],
    queryFn: () => api.projects.list(),
  });

  const projects = Array.isArray(projectsData) ? projectsData : [];

  const deleteMutation = useMutation({
    mutationFn: (projectId) => api.projects.delete(projectId),
    onSuccess: () => {
      queryClient.invalidateQueries(['projects']);
      toast.success(t('projects.delete_success') || "Project deleted successfully");
      setShowDeleteModal(null);
      if (currentProject?.id === showDeleteModal?.id) {
        setCurrentProject(null);
      }
    },
    onError: (error) => {
      toast.error(error.message || t('projects.delete_error') || "Failed to delete project");
    },
  });

  if (isLoading) return <PageLoader text="Loading workspaces..." />;

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-primary tracking-tight">{t('projects.title')}</h1>
          <p className="text-secondary text-sm mt-1">{t('projects.description')}</p>
        </div>
        <Button
          onClick={() => setShowCreateModal(true)}
          variant="primary"
          leftIcon={Plus}
        >
          {t('projects.create_new')}
        </Button>
      </div>

      {/* Projects Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {projects.length === 0 ? (
          <div className="col-span-full py-10 bg-surface-card/40 rounded-2xl border border-border/40">
            <EmptyState
              icon={Building}
              title={t('projects.no_projects')}
              description="Create a workspace to manage channels, AI bot training, orders, and sales automation."
              actionLabel={t('projects.create_new')}
              onAction={() => setShowCreateModal(true)}
            />
          </div>
        ) : (
          projects.map((project, index) => {
            const isActive = currentProject?.id === project.id;
            return (
              <motion.div
                key={project.id}
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
              >
                <GlassCard
                  className={`p-5 h-full flex flex-col justify-between transition-all duration-200 border ${
                    isActive
                      ? 'border-brand-accent/50 shadow-brand-glow bg-surface-card/90'
                      : 'border-border/50 hover:border-border/80'
                  }`}
                >
                  <div>
                    <div className="flex items-start justify-between gap-3 mb-4">
                      <div className="flex items-center gap-3">
                        <div
                          className={`w-11 h-11 rounded-xl flex items-center justify-center border transition-colors ${
                            isActive
                              ? 'bg-brand-primary text-white border-brand-accent/40 shadow-surface-sm'
                              : 'bg-surface-subtle text-secondary border-border/40'
                          }`}
                        >
                          <Building className="w-5 h-5" />
                        </div>
                        <div>
                          <h3 className="font-bold text-base text-primary truncate max-w-[160px]">
                            {project.name}
                          </h3>
                          <span className="text-[10px] text-muted font-mono tracking-wider uppercase">
                            {project.project_code || 'PRJ-DEFAULT'}
                          </span>
                        </div>
                      </div>
                      {isActive && (
                        <Badge variant="brand" size="sm" dot>
                          Active
                        </Badge>
                      )}
                    </div>

                    <div className="space-y-2 py-3 border-y border-border/30 text-xs text-secondary mb-4">
                      <div className="flex items-center gap-2">
                        <Globe className="w-3.5 h-3.5 text-muted" />
                        <span>{project.timezone || 'UTC'}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Calendar className="w-3.5 h-3.5 text-muted" />
                        <span>Created {new Date(project.created_at || Date.now()).toLocaleDateString()}</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 pt-2">
                    <Button
                      variant={isActive ? "outline" : "secondary"}
                      size="sm"
                      className="flex-1 text-xs"
                      disabled={isActive}
                      onClick={() => {
                        setCurrentProject(project);
                        toast.success(`${t('projects.switched_to') || "Switched to"} ${project.name}`);
                      }}
                    >
                      {isActive ? 'Current Active' : 'Switch Workspace'}
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="text-muted hover:text-status-danger"
                      onClick={() => setShowDeleteModal(project)}
                      aria-label="Delete project"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </GlassCard>
              </motion.div>
            );
          })
        )}
      </div>

      {/* Delete Confirmation Modal */}
      <AnimatePresence>
        {showDeleteModal && (
          <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="glass-card p-6 max-w-md w-full rounded-2xl border border-status-danger/40 bg-surface-card"
            >
              <div className="flex items-center gap-3 mb-3 text-status-danger">
                <AlertCircle className="w-6 h-6 flex-shrink-0" />
                <h2 className="text-lg font-bold text-primary">{t('projects.delete_confirm_title')}</h2>
              </div>
              <p className="text-sm text-secondary mb-6 leading-relaxed">
                {t('projects.delete_confirm_desc')}
              </p>
              <div className="flex gap-3">
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={() => setShowDeleteModal(null)}
                >
                  {t('common.cancel')}
                </Button>
                <Button
                  variant="danger"
                  className="flex-1"
                  isLoading={deleteMutation.isPending}
                  onClick={() => deleteMutation.mutate(showDeleteModal.id)}
                >
                  {t('common.delete')}
                </Button>
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
