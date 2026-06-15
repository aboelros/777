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
      const projectsList = await api.projects.list();

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

  // Initialize auth by checking if user is authenticated via cookies
  initialize: async () => {
    try {
      // Try to fetch user - cookies will be automatically sent
      const user = await api.auth.getCurrentUser();
      set({ user, isAuthenticated: true, isLoading: false });

      // Load projects after auth
      await get().loadProjects();
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
