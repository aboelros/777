/**
 * Global Zustand store for administrative user state, system health, and layout preferences.
 */

import { create } from 'zustand';

export const useAdminStore = create((set) => ({
  user: (() => {
    try {
      const raw = localStorage.getItem('admin_user');
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  })(),
  isAuthenticated: !!localStorage.getItem('admin_token'),
  systemHealth: null,
  notification: null,
  sidebarOpen: true,

  setUser: (user, token) => {
    if (token) localStorage.setItem('admin_token', token);
    if (user) localStorage.setItem('admin_user', JSON.stringify(user));
    set({ user, isAuthenticated: true });
  },

  logout: () => {
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin_user');
    set({ user: null, isAuthenticated: false });
    window.location.href = '/login';
  },

  setSystemHealth: (health) => set({ systemHealth: health }),

  setNotification: (notification) => set({ notification }),

  clearNotification: () => set({ notification: null }),

  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
}));
