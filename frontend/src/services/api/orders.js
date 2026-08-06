import { apiRequest, API_BASE_URL } from './core';

export const orders = {
  list: async (projectId, params = {}) => {
    const query = new URLSearchParams(params).toString();
    return apiRequest(`/api/v1/orders/${projectId}?${query}`);
  },

  get: async (orderId) => {
    return apiRequest(`/api/v1/orders/${orderId}`);
  },

  create: async (projectId, data) => {
    return apiRequest(`/api/v1/orders/${projectId}`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  updateStatus: async (orderId, status) => {
    return apiRequest(`/api/v1/orders/${orderId}/status`, {
      method: 'PUT',
      body: JSON.stringify({ status }),
    });
  },

  track: async (orderId) => {
    return apiRequest(`/api/v1/orders/${orderId}/track`);
  },

  aiProcess: async (orderId) => {
    return apiRequest(`/api/v1/orders/${orderId}/ai-process`, {
      method: 'POST',
    });
  },

  stats: async (projectId, days = 30) => {
    return apiRequest(`/api/v1/orders/${projectId}/stats?days=${days}`);
  },
};
