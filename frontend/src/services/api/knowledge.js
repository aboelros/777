import { apiRequest, API_BASE_URL } from './core';

export const knowledge = {
  list: async (projectId) => {
    return apiRequest(`/api/v1/knowledge/${projectId}`);
  },

  create: async (projectId, data) => {
    return apiRequest(`/api/v1/knowledge/${projectId}`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  update: async (projectId, itemId, data) => {
    return apiRequest(`/api/v1/knowledge/${projectId}/${itemId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },

  delete: async (projectId, itemId) => {
    return apiRequest(`/api/v1/knowledge/${projectId}/${itemId}`, {
      method: 'DELETE',
    });
  },
};
