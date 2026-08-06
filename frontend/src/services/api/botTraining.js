import { apiRequest, API_BASE_URL } from './core';

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
