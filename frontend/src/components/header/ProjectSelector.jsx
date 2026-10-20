import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ChevronDown, Check, Plus, FolderKanban } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useProjectStore } from '@/store/projectStore';
import { useTranslation } from '@/lib/translations';
import api from '@/services/api';

/**
 * Automind Workspace & Project Selector Dropdown
 */
export default function ProjectSelector({ onCreateClick }) {
  const [isOpen, setIsOpen] = useState(false);
  const { currentProject, setCurrentProject } = useProjectStore();
  const { t } = useTranslation();

  const { data: projectsData } = useQuery({
    queryKey: ['projects'],
    queryFn: () => api.projects.list(),
  });

  const projects = Array.isArray(projectsData) ? projectsData : [];

  return (
    <div className="relative">
      <motion.button
        type="button"
        whileHover={{ scale: 1.01 }}
        whileTap={{ scale: 0.99 }}
        onClick={() => setIsOpen(!isOpen)}
        className="px-3.5 py-1.5 rounded-xl flex items-center gap-2.5 border border-border/50 hover:border-brand-accent/30 transition-colors bg-surface-card/60 shadow-surface-sm text-sm"
        aria-expanded={isOpen}
        aria-haspopup="listbox"
      >
        <span
          className={`w-2 h-2 rounded-full ${
            currentProject ? 'bg-status-success shadow-[0_0_6px_rgba(16,185,129,0.6)]' : 'bg-slate-500'
          }`}
          aria-hidden="true"
        />
        <span className="font-medium text-primary max-w-[140px] truncate">
          {currentProject ? currentProject.name : t('projects.select_project')}
        </span>
        <ChevronDown className="w-3.5 h-3.5 text-muted" aria-hidden="true" />
      </motion.button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 8, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 8, scale: 0.96 }}
            transition={{ duration: 0.15 }}
            className="absolute right-0 mt-2 w-72 rounded-2xl p-2 z-[100] border border-border/60 shadow-surface-lg bg-surface-card/95 backdrop-blur-xl origin-top-right"
          >
            <div className="px-3 py-1.5 text-[10px] font-bold text-muted uppercase tracking-widest flex items-center gap-1.5">
              <FolderKanban className="w-3 h-3 text-brand-accent" />
              <span>{t('projects.title')}</span>
            </div>

            <div className="max-h-60 overflow-y-auto custom-scrollbar my-1 space-y-0.5">
              {projects.length === 0 ? (
                <div className="px-3 py-3 text-xs text-muted text-center">
                  {t('projects.no_projects')}
                </div>
              ) : (
                projects.map((project) => {
                  const isSelected = currentProject?.id === project.id;
                  return (
                    <button
                      key={project.id}
                      type="button"
                      onClick={() => {
                        setCurrentProject(project);
                        setIsOpen(false);
                      }}
                      className={`w-full flex items-center justify-between px-3 py-2 rounded-xl text-left text-xs transition-colors ${
                        isSelected
                          ? 'bg-brand-primary/15 text-brand-accent font-semibold'
                          : 'text-secondary hover:text-primary hover:bg-white/5'
                      }`}
                    >
                      <span className="truncate">{project.name}</span>
                      {isSelected && <Check className="w-3.5 h-3.5 text-brand-accent flex-shrink-0" />}
                    </button>
                  );
                })
              )}
            </div>

            <div className="border-t border-border/30 pt-1.5 mt-1">
              <button
                type="button"
                onClick={() => {
                  setIsOpen(false);
                  onCreateClick();
                }}
                className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-xl bg-brand-primary hover:bg-brand-hover text-white text-xs font-semibold shadow-surface-sm transition-all"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>{t('projects.create_new')}</span>
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
