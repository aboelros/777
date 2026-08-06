import { apiRequest, API_BASE_URL } from './core';

export const reports = {
  list: async (projectId, params = {}) => {
    const query = new URLSearchParams(params).toString();
    return apiRequest(`/api/v1/reports/${projectId}?${query}`);
  },

  get: async (projectId, reportId) => {
    return apiRequest(`/api/v1/reports/${projectId}/${reportId}`);
  },

  generate: async (projectId, data) => {
    return apiRequest(`/api/v1/reports/${projectId}/generate`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  delete: async (projectId, reportId) => {
    return apiRequest(`/api/v1/reports/${projectId}/${reportId}`, {
      method: 'DELETE',
    });
  },

  getDashboardSummary: async (projectId) => {
    return apiRequest(`/api/v1/reports/${projectId}/dashboard-summary`);
  },
};
