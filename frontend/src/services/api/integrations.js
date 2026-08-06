import { apiRequest, API_BASE_URL } from './core';

export const integrations = {
  list: async (projectId) => {
    return apiRequest(`/api/v1/integrations/${projectId}`);
  },

  get: async (projectId, integrationId) => {
    return apiRequest(`/api/v1/integrations/${projectId}/${integrationId}`);
  },

  create: async (projectId, data) => {
    return apiRequest(`/api/v1/integrations/${projectId}/connect`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  update: async (projectId, integrationId, data) => {
    return apiRequest(`/api/v1/integrations/${projectId}/${integrationId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },

  delete: async (projectId, integrationId) => {
    return apiRequest(`/api/v1/integrations/${projectId}/${integrationId}`, {
      method: 'DELETE',
    });
  },

  test: async (projectId, integrationId) => {
    return apiRequest(`/api/v1/integrations/${projectId}/${integrationId}/test`, {
      method: 'POST',
    });
  },

  sync: async (projectId, integrationId) => {
    return apiRequest(`/api/v1/integrations/${projectId}/${integrationId}/sync`, {
      method: 'POST',
    });
  },

  verify: async (projectId, integrationId) => {
    return apiRequest(`/api/v1/integrations/${projectId}/${integrationId}/verify`, {
      method: 'POST',
    });
  },

  debug: async (projectId, integrationId) => {
    return apiRequest(`/api/v1/integrations/${projectId}/${integrationId}/debug`);
  },

  refreshIdentities: async (projectId) => {
    return apiRequest(`/api/v1/integrations/${projectId}/refresh-identities`, {
      method: 'POST',
    });
  },

  testData: async (projectId, data) => {
    return apiRequest(`/api/v1/integrations/${projectId}/test-data`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  // WA-Gateway endpoints (self-hosted WhatsApp gateway)
  waGateway: {
    startSession: async (projectId, integrationId) => {
      return apiRequest(`/api/v1/integrations/${projectId}/whatsapp/${integrationId}/wa-gateway/start-session`, {
        method: 'POST',
      });
    },

    getQR: async (projectId, integrationId) => {
      return apiRequest(`/api/v1/integrations/${projectId}/whatsapp/${integrationId}/wa-gateway/qr`);
    },

    logout: async (projectId, integrationId) => {
      return apiRequest(`/api/v1/integrations/${projectId}/whatsapp/${integrationId}/wa-gateway/logout`, {
        method: 'POST',
      });
    },
  },

  // Meta OAuth
  getMetaAuthUrl: async (projectId, redirectUri) => {
    return apiRequest(`/api/v1/integrations/${projectId}/meta/auth-url?redirect_uri=${encodeURIComponent(redirectUri)}`);
  },

  handleMetaCallback: async (projectId, code, redirectUri, provider) => {
    return apiRequest(`/api/v1/integrations/${projectId}/meta/callback`, {
      method: 'POST',
      body: JSON.stringify({ code, redirect_uri: redirectUri, provider }),
    });
  },

  getLogs: async (projectId, limit = 50) => {
    return apiRequest(`/api/v1/integrations/${projectId}/logs?limit=${limit}`);
  },

  // Social Feed and Comments
  getMetaFeed: async (projectId, limit = 10) => {
    return apiRequest(`/api/v1/integrations/${projectId}/meta/feed?limit=${limit}`);
  },

  getMetaComments: async (projectId, objectId, platform) => {
    return apiRequest(`/api/v1/integrations/${projectId}/meta/comments/${objectId}?platform=${platform}`);
  },

  replyMetaComment: async (projectId, commentId, platform, message) => {
    return apiRequest(`/api/v1/integrations/${projectId}/meta/comments/${commentId}/reply`, {
      method: 'POST',
      body: JSON.stringify({ platform, message }),
    });
  },
};
