/**
 * API client and administrative service request helpers.
 */

import axios from 'axios';

const RAW_API_URL = import.meta.env.VITE_API_URL;
export const API_URL = RAW_API_URL || (import.meta.env.PROD ? '/api/v1' : 'http://localhost:8000/api/v1');

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('admin_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 || error.response?.status === 403) {
      localStorage.removeItem('admin_token');
      localStorage.removeItem('admin_user');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export const adminApi = {
  // Dashboard & Health
  getDashboard: (days = 30) => api.get(`/admin/dashboard?days=${days}`),
  getHealth: () => api.get('/admin/health'),

  // Users
  getUsers: (q = '', page = 1) => api.get(`/admin/users?page=${page}${q ? `&q=${encodeURIComponent(q)}` : ''}`),
  createUser: (data) => api.post('/admin/users', data),
  updateUser: (userId, data) => api.patch(`/admin/users/${userId}`, data),
  resetPassword: (userId, newPassword) => api.post(`/admin/users/${userId}/reset-password`, { new_password: newPassword }),
  deleteUser: (userId) => api.delete(`/admin/users/${userId}`),

  // Projects
  getProjects: (q = '', page = 1) => api.get(`/admin/projects?page=${page}${q ? `&q=${encodeURIComponent(q)}` : ''}`),
  updateProject: (projectId, data) => api.patch(`/admin/projects/${projectId}`, data),

  // Subscriptions
  getSubscriptions: (page = 1) => api.get(`/admin/billing/subscriptions?page=${page}`),
  overrideSubscription: (userId, data) => api.patch(`/admin/billing/subscriptions/${userId}`, data),

  // AI Telemetry
  getAiTelemetry: () => api.get('/admin/ai/telemetry'),

  // Webhooks
  getWebhookLogs: (page = 1, status = '') =>
    api.get(`/admin/webhooks/logs?page=${page}${status ? `&status_filter=${status}` : ''}`),
  retryWebhook: (deliveryId) => api.post(`/admin/webhooks/logs/${deliveryId}/retry`),

  // Audit Logs & Settings
  getAuditLogs: (page = 1) => api.get(`/admin/system/audit-logs?page=${page}`),
  getSettings: () => api.get('/admin/settings'),
  updateSettings: (data) => api.patch('/admin/settings', data),
};
