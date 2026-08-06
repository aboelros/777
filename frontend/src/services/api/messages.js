import { apiRequest, API_BASE_URL } from './core';

export const messages = {
  getConversations: async (projectId, params = {}) => {
    const searchParams = new URLSearchParams(params).toString();
    const query = searchParams ? `?${searchParams}` : '';
    return apiRequest(`/api/v1/messages/${projectId}/conversations${query}`);
  },

  getMessages: async (projectId, conversationId, params = {}) => {
    const searchParams = new URLSearchParams(params).toString();
    const query = searchParams ? `?${searchParams}` : '';
    return apiRequest(`/api/v1/messages/${projectId}/conversations/${conversationId}/messages${query}`);
  },

  send: async (projectId, data) => {
    return apiRequest(`/api/v1/messages/${projectId}/send`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  markConversationRead: async (projectId, conversationId) => {
    return apiRequest(`/api/v1/messages/${projectId}/conversations/${conversationId}/read`, {
      method: 'PATCH',
    });
  },

  generateAIReply: async (projectId, data) => {
    return apiRequest(`/api/v1/assistant/generate-reply`, {
      method: 'POST',
      body: JSON.stringify({ project_id: projectId, ...data }),
    });
  },

  stats: async (projectId) => {
    return apiRequest(`/api/v1/messages/${projectId}/stats/summary`);
  },

  clearConversation: async (projectId, conversationId) => {
    return apiRequest(`/api/v1/messages/${projectId}/conversations/${conversationId}`, {
      method: 'DELETE',
    });
  },

  getCustomerProfile: async (projectId, profileId) => {
    return apiRequest(`/api/v1/messages/${projectId}/customers/${profileId}`);
  },

  toggleAI: async (projectId, profileId) => {
    return apiRequest(`/api/v1/messages/${projectId}/customers/${profileId}/toggle-ai`, {
      method: 'POST',
    });
  },
};
