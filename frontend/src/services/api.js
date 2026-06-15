/**
 * API Service for AI Sales Commander
 * Complete implementation with all endpoints
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

// Helper function to get auth token
const getAuthToken = () => {
  const token = localStorage.getItem('access_token');
  console.log('[DEBUG] getAuthToken:', token ? 'Token exists' : 'No token');
  return token;
};

// Helper function for API requests
async function apiRequest(endpoint, options = {}) {
  const token = getAuthToken();

  const config = {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
    },
    ...options,
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

  if (!response.ok) {
    // Handle 401 Unauthorized - redirect to login
    if (response.status === 401) {
      if (!window.location.pathname.includes('/login')) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.replace('/login');
      }
      throw new Error('Authentication required. Please log in again.');
    }

    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

// Auth API
export const auth = {
  login: async (data) => {
    const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Login failed' }));
      throw new Error(error.detail || 'Login failed');
    }

    const result = await response.json();

    // Store the access token if provided
    if (result.access_token) {
      localStorage.setItem('access_token', result.access_token);
    }

    return result;
  },

  getCurrentUser: async () => {
    return apiRequest('/api/v1/auth/me');
  },

  logout: async () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },
};

// Projects API
export const projects = {
  list: async () => {
    return apiRequest('/api/v1/projects');
  },

  get: async (id) => {
    return apiRequest(`/api/v1/projects/${id}`);
  },

  create: async (data) => {
    return apiRequest('/api/v1/projects', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  update: async (id, data) => {
    return apiRequest(`/api/v1/projects/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },

  delete: async (id) => {
    return apiRequest(`/api/v1/projects/${id}`, {
      method: 'DELETE',
    });
  },

  listMembers: async (projectId) => {
    return apiRequest(`/api/v1/projects/${projectId}/members`);
  },

  addMember: async (projectId, email, role = 'worker') => {
    return apiRequest(`/api/v1/projects/${projectId}/members?member_email=${encodeURIComponent(email)}&role=${role}`, {
      method: 'POST',
    });
  },

  updateMemberRole: async (projectId, userId, role) => {
    return apiRequest(`/api/v1/projects/${projectId}/members/${userId}?role=${role}`, {
      method: 'PATCH',
    });
  },

  removeMember: async (projectId, userId) => {
    return apiRequest(`/api/v1/projects/${projectId}/members/${userId}`, {
      method: 'DELETE',
    });
  },
};

// Orders API
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

// Messages API
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

// Reports API
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

// Integrations API
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

// AI Assistant API
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

// Subscriptions API
export const subscriptions = {
  getPlans: async () => {
    return apiRequest('/api/v1/subscriptions/plans');
  },

  getMySubscription: async () => {
    return apiRequest('/api/v1/subscriptions/my-subscription');
  },

  getUsagePercentage: async () => {
    return apiRequest('/api/v1/subscriptions/usage-percentage');
  },

  getUsageAlerts: async () => {
    return apiRequest('/api/v1/subscriptions/usage-alerts');
  },

  getOverages: async () => {
    return apiRequest('/api/v1/subscriptions/overages');
  },

  upgrade: async (data) => {
    return apiRequest('/api/v1/subscriptions/upgrade', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  cancel: async () => {
    return apiRequest('/api/v1/subscriptions/cancel', {
      method: 'POST',
    });
  },
};

// Bot Training API
export const botTraining = {
  getInstructions: async (projectId) => {
    return apiRequest(`/api/v1/bot-training/${projectId}/instructions`);
  },

  createInstruction: async (projectId, data) => {
    return apiRequest(`/api/v1/bot-training/${projectId}/instructions`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  updateInstruction: async (projectId, instructionId, data) => {
    return apiRequest(`/api/v1/bot-training/${projectId}/instructions/${instructionId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  deleteInstruction: async (projectId, instructionId) => {
    return apiRequest(`/api/v1/bot-training/${projectId}/instructions/${instructionId}`, {
      method: 'DELETE',
    });
  },

  toggleInstruction: async (projectId, instructionId) => {
    return apiRequest(`/api/v1/bot-training/${projectId}/instructions/${instructionId}/toggle`, {
      method: 'POST',
    });
  },

  seedInstructions: async (projectId) => {
    return apiRequest(`/api/v1/bot-training/${projectId}/seed-instructions`, {
      method: 'POST',
    });
  },
};

// Social Media API
// Social Media API
export const socialMedia = {
  listAccounts: (projectId) => apiRequest(`/api/v1/social/${projectId}/accounts`),
  getAccounts: (projectId) => apiRequest(`/api/v1/social/${projectId}/accounts`),
  getFeed: (projectId) => apiRequest(`/api/v1/social/${projectId}/feed?limit=20`),
  getStats: (projectId) => apiRequest(`/api/v1/social/${projectId}/stats`),
  listFeed: (projectId, params) => {
    const query = new URLSearchParams(params).toString();
    return apiRequest(`/api/v1/social/${projectId}/feed?${query}`);
  },
  listComments: (projectId, params) => {
    const query = new URLSearchParams(params).toString();
    return apiRequest(`/api/v1/social/${projectId}/comments?${query}`);
  },
  generateResponse: (projectId, commentId, data = {}) => {
    return apiRequest(`/api/v1/social/${projectId}/comments/${commentId}/generate-response`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
  sendResponse: (projectId, commentId, text) => {
    return apiRequest(`/api/v1/social/${projectId}/comments/${commentId}/send-response`, {
      method: 'POST',
      body: JSON.stringify({ response_text: text }),
    });
  },
};

// Deals (Sales Pipeline) API
export const deals = {
  getStages: (projectId) => apiRequest(`/api/v1/deals/${projectId}/stages`),
  createStage: (projectId, data) => apiRequest(`/api/v1/deals/${projectId}/stages`, {
    method: 'POST',
    body: JSON.stringify(data)
  }),
  getDeals: (projectId, params) => {
    const query = new URLSearchParams(params).toString();
    return apiRequest(`/api/v1/deals/${projectId}/deals?${query}`);
  },
  createDeal: (projectId, data) => apiRequest(`/api/v1/deals/${projectId}/deals`, {
    method: 'POST',
    body: JSON.stringify(data)
  }),
  updateDeal: (projectId, dealId, data) => apiRequest(`/api/v1/deals/${projectId}/deals/${dealId}`, {
    method: 'PATCH',
    body: JSON.stringify(data)
  }),
};


// Drip Campaigns API
export const dripCampaigns = {
  getCampaigns: (projectId) => apiRequest(`/api/v1/drip-campaigns/${projectId}/campaigns`),
  createCampaign: (projectId, data) => apiRequest(`/api/v1/drip-campaigns/${projectId}/campaigns`, {
    method: 'POST',
    body: JSON.stringify(data)
  }),
  addStep: (projectId, campaignId, data) => apiRequest(`/api/v1/drip-campaigns/${projectId}/campaigns/${campaignId}/steps`, {
    method: 'POST',
    body: JSON.stringify(data)
  }),
};

// Payments & Invoicing API
export const payments = {
  createLink: (projectId, data) => apiRequest(`/api/v1/payments/${projectId}/payment-links`, {
    method: 'POST',
    body: JSON.stringify(data)
  }),
  getInvoices: (projectId) => apiRequest(`/api/v1/payments/${projectId}/invoices`),
  createInvoice: (projectId, data) => apiRequest(`/api/v1/payments/${projectId}/invoices`, {
    method: 'POST',
    body: JSON.stringify(data)
  }),
};

// Products API
export const products = {
  list: async (projectId) => {
    return apiRequest(`/api/v1/products/${projectId}`);
  },

  get: async (projectId, productId) => {
    return apiRequest(`/api/v1/products/${projectId}/${productId}`);
  },

  create: async (projectId, data) => {
    return apiRequest(`/api/v1/products/${projectId}`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  update: async (projectId, productId, data) => {
    return apiRequest(`/api/v1/products/${projectId}/${productId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  delete: async (projectId, productId) => {
    return apiRequest(`/api/v1/products/${projectId}/${productId}`, {
      method: 'DELETE',
    });
  },

  uploadImage: async (projectId, productId, formData) => {
    // Note: formData should be passed directly as body
    // fetch will automatically set Content-Type to multipart/form-data with boundary
    // customized to NOT set Content-Type header manually if it's FormData
    const token = localStorage.getItem('access_token');
    const response = await fetch(`${API_BASE_URL}/api/v1/products/${projectId}/${productId}/images`, {
      method: 'POST',
      headers: {
        ...(token && { Authorization: `Bearer ${token}` }),
      },
      body: formData,
    });

    if (!response.ok) {
      if (response.status === 401) {
        localStorage.removeItem('access_token');
        window.location.replace('/login');
        throw new Error('Authentication required');
      }
      const error = await response.json().catch(() => ({ detail: 'Request failed' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }
    return response.json();
  },

  deleteImage: async (projectId, productId, index) => {
    return apiRequest(`/api/v1/products/${projectId}/${productId}/images/${index}`, {
      method: 'DELETE',
    });
  },

  updateImage: async (projectId, productId, index, data) => {
    return apiRequest(`/api/v1/products/${projectId}/${productId}/images/${index}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },

  reorderImages: async (projectId, productId, images) => {
    return apiRequest(`/api/v1/products/${projectId}/${productId}/images`, {
      method: 'PUT',
      body: JSON.stringify({ images }),
    });
  },

  bulkUpload: async (projectId, file) => {
    const formData = new FormData();
    formData.append('file', file);

    return apiRequest(`/api/v1/products/${projectId}/bulk-upload`, {
      method: 'POST',
      body: formData,
      headers: {}, // Let browser set content-type for FormData
    });
  },
};

// Knowledge Base API
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

const api = {
  auth: auth,
  projects: projects,
  products: products,
  orders: orders,
  messages: messages,
  reports: reports,
  integrations: integrations,
  assistant: assistant,
  subscriptions: subscriptions,
  botTraining: botTraining,
  socialMedia: socialMedia,
  knowledge: knowledge,
  deals: deals,
  dripCampaigns: dripCampaigns,
  payments: payments,
};

export default api;
