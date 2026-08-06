import { apiRequest, API_BASE_URL } from './core';

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
