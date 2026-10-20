import { create } from 'zustand';
import api from '../services/api';
import { useProjectStore } from './projectStore';

export const useAuthStore = create((set, get) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,

  setAuth: (user, token) => {
    if (token) localStorage.setItem('access_token', token);
    set({ user, isAuthenticated: true, isLoading: false });
  },

  // Load projects and set default
  loadProjects: async () => {
    try {
      const raw = await api.projects.list();
      const projectsList = Array.isArray(raw)
        ? raw
        : (Array.isArray(raw?.projects) ? raw.projects : (Array.isArray(raw?.data) ? raw.data : []));

      const projectStore = useProjectStore.getState();
      projectStore.setProjects(projectsList);

      // Set first project as current if none selected
      if (projectsList.length > 0 && !projectStore.currentProject) {
        projectStore.setCurrentProject(projectsList[0]);
      }
    } catch (error) {
      console.error('Failed to load projects:', error);
    }
  },

  // Initialize auth by checking if user is authenticated
  initialize: async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        set({ user: null, isAuthenticated: false, isLoading: false });
        return;
      }

      const user = await api.auth.getCurrentUser();
      if (user && (user.id || user.email)) {
        set({ user, isAuthenticated: true, isLoading: false });
        await get().loadProjects();
      } else {
        set({ user: null, isAuthenticated: false, isLoading: false });
      }
    } catch (error) {
      // Not authenticated or token expired
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },

  // Login
  login: async (email, password) => {
    try {
      // Login - backend will set HttpOnly cookies automatically
      await api.auth.login({ email, password });

      // Fetch user data
      const user = await api.auth.getCurrentUser();
      set({ user, isAuthenticated: true });

      // Load projects after login
      await get().loadProjects();

      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || error.message || 'Login failed'
      };
    }
  },

  // Register
  register: async (email, password, name) => {
    try {
      await api.auth.register({ email, password, name });

      // Auto-login after registration
      return await get().login(email, password);
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Registration failed'
      };
    }
  },

  // Logout
  logout: async () => {
    try {
      // Call logout endpoint - server will clear cookies
      await api.auth.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      set({ user: null, isAuthenticated: false });
      // Redirect to login
      window.location.href = '/login';
    }
  },
}));
