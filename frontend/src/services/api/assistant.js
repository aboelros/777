import { apiRequest, API_BASE_URL } from './core';

export const assistant = {
  query: async (data) => {
    return apiRequest(`/api/v1/assistant/query`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  generateReply: async (data) => {
    return apiRequest(`/api/v1/assistant/generate-reply`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  analyzeSentiment: async (projectId, message) => {
    return apiRequest(`/api/v1/assistant/analyze-sentiment`, {
      method: 'POST',
      body: JSON.stringify({ project_id: projectId, message }),
    });
  },

  usage: async (projectId, days = 30) => {
    return apiRequest(`/api/v1/assistant/usage/${projectId}?days=${days}`);
  },
};
