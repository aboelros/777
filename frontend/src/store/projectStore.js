import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import api from '../services/api';
import { toast } from 'sonner';

export const useProjectStore = create(
  persist(
    (set, get) => ({
      currentProject: null,
      projects: [],
      isLoading: false,

      setCurrentProject: (project) => set({ currentProject: project }),
      setProjects: (projects) => set({ projects }),

      clearProject: () => set({ currentProject: null }),

      // Load projects from API
      loadProjects: async () => {
        try {
          set({ isLoading: true });
          const raw = await api.projects.list();
          const projectsList = Array.isArray(raw)
            ? raw
            : (Array.isArray(raw?.projects) ? raw.projects : (Array.isArray(raw?.data) ? raw.data : []));

          set({ projects: projectsList });

          const current = get().currentProject;

          // If we have a current project, verify it still exists
          if (current) {
            const exists = projectsList.find(p => p && p.id === current.id);
            if (!exists) {
              const nextProject = projectsList.length > 0 ? projectsList[0] : null;
              set({ currentProject: nextProject });
              if (nextProject) {
                toast.error('Previous project not found. Switched to ' + nextProject.name);
              }
            } else {
              set({ currentProject: exists });
            }
          } else if (projectsList.length > 0) {
            set({ currentProject: projectsList[0] });
          }
        } catch (error) {
          console.error('Failed to load projects:', error);
          // Don't show toast on 401 as api.js handles redirect
          if (error.message !== 'Authentication required. Please log in again.') {
            toast.error('Failed to load projects');
          }
        } finally {
          set({ isLoading: false });
        }
      },

      // Create new project
      createProject: async (projectData) => {
        try {
          set({ isLoading: true });

          // Auto-generate project code if missing
          if (!projectData.project_code && projectData.name) {
            const code = projectData.name
              .toUpperCase()
              .replace(/[^A-Z0-9]/g, '')
              .substring(0, 10);
            const timestamp = Date.now().toString().slice(-3);
            projectData.project_code = `${code}-${timestamp}`;
          }

          const newProject = await api.projects.create(projectData);

          // Add to projects list and set as current
          const currentProjects = get().projects;
          const updatedProjects = [...currentProjects, newProject];

          set({
            projects: updatedProjects,
            currentProject: newProject
          });

          toast.success('🎉 Project created successfully!');
          return { success: true, project: newProject };
        } catch (error) {
          console.error('Failed to create project:', error);
          toast.error(error.message || 'Failed to create project');
          return { success: false, error: error.message };
        } finally {
          set({ isLoading: false });
        }
      },

      // Update project
      updateProject: async (projectId, updateData) => {
        try {
          const updatedProject = await api.projects.update(projectId, updateData);

          // Update in projects list
          const currentProjects = get().projects;
          const updatedProjects = currentProjects.map(p =>
            p.id === projectId ? updatedProject : p
          );

          set({ projects: updatedProjects });

          // Update current project if it's the one being updated
          if (get().currentProject?.id === projectId) {
            set({ currentProject: updatedProject });
          }

          toast.success('Project updated successfully!');
          return { success: true };
        } catch (error) {
          console.error('Failed to update project:', error);
          toast.error(error.message || 'Failed to update project');
          return { success: false, error: error.message };
        }
      },
    }),
    {
      name: 'project-storage',
    }
  )
);
