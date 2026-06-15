import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance with cookie support
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Enable cookies for cross-origin requests
});

// Request interceptor (cookies are automatically sent with withCredentials)
api.interceptors.request.use(
  (config) => {
    // No need to manually add Authorization header - cookies handle it
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh via cookies
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If 401 and not already retried, try to refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Call refresh endpoint - cookies are automatically sent
        await axios.post(
          `${API_URL}/api/v1/auth/refresh`,
          {},
          { withCredentials: true } // Ensure cookies are sent
        );

        // Refresh succeeded, retry original request
        // New cookies are automatically set by the server
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed, redirect to login
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Auth API
export const auth = {
  register: (data) => api.post('/api/v1/auth/register', data),
  login: (data) => api.post('/api/v1/auth/login', data),
  logout: (refreshToken) => api.post('/api/v1/auth/logout', { refresh_token: refreshToken }),
  me: () => api.get('/api/v1/auth/me'),
};

// Projects API
export const projects = {
  list: () => api.get('/api/v1/projects'),
  get: (id) => api.get(`/api/v1/projects/${id}`),
  create: (data) => api.post('/api/v1/projects', data),
  update: (id, data) => api.patch(`/api/v1/projects/${id}`, data),
  delete: (id) => api.delete(`/api/v1/projects/${id}`),
};

// Integrations API
export const integrations = {
  list: (projectId) => api.get(`/api/v1/integrations/${projectId}`),
  get: (projectId, id) => api.get(`/api/v1/integrations/${projectId}/${id}`),
  connect: (projectId, data) => api.post(`/api/v1/integrations/${projectId}/connect`, data),
  update: (projectId, id, data) => api.patch(`/api/v1/integrations/${projectId}/${id}`, data),
  disconnect: (projectId, id) => api.delete(`/api/v1/integrations/${projectId}/${id}`),
  sync: (projectId, id) => api.post(`/api/v1/integrations/${projectId}/${id}/sync`),
};

// Orders API
export const orders = {
  list: (projectId, params) => api.get(`/api/v1/orders/${projectId}`, { params }),
  get: (projectId, id) => api.get(`/api/v1/orders/${projectId}/${id}`),
  create: (projectId, data) => api.post(`/api/v1/orders/${projectId}`, data),
  update: (projectId, id, data) => api.patch(`/api/v1/orders/${projectId}/${id}`, data),
  delete: (projectId, id) => api.delete(`/api/v1/orders/${projectId}/${id}`),
  stats: (projectId, days) => api.get(`/api/v1/orders/${projectId}/stats/summary`, { params: { days } }),
};

// Messages API
export const messages = {
  inbox: (projectId, params) => api.get(`/api/v1/messages/${projectId}/inbox`, { params }),
  get: (projectId, id) => api.get(`/api/v1/messages/${projectId}/${id}`),
  send: (projectId, data) => api.post(`/api/v1/messages/${projectId}/send`, data),
  markRead: (projectId, id) => api.patch(`/api/v1/messages/${projectId}/${id}/read`),
  conversation: (projectId, orderId) => api.get(`/api/v1/messages/${projectId}/conversation/${orderId}`),
  stats: (projectId, days) => api.get(`/api/v1/messages/${projectId}/stats/summary`, { params: { days } }),
};

// Assistant API
export const assistant = {
  query: (data) => api.post('/api/v1/assistant/query', data),
  generateReply: (projectId, orderId, customerMessage) =>
    api.post('/api/v1/assistant/generate-reply', null, {
      params: { project_id: projectId, order_id: orderId, customer_message: customerMessage }
    }),
  analyzeSentiment: (projectId, message) =>
    api.post('/api/v1/assistant/analyze-sentiment', null, {
      params: { project_id: projectId, message }
    }),
  usage: (projectId, days) => api.get(`/api/v1/assistant/usage/${projectId}`, { params: { days } }),
};

// Reports API
export const reports = {
  list: (projectId, params) => api.get(`/api/v1/reports/${projectId}`, { params }),
  get: (projectId, id) => api.get(`/api/v1/reports/${projectId}/${id}`),
  generate: (projectId, data) => api.post(`/api/v1/reports/${projectId}/generate`, data),
  delete: (projectId, id) => api.delete(`/api/v1/reports/${projectId}/${id}`),
};

export default api;
