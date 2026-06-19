/**
 * API client for communication with the backend.
 */

import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Add response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Session APIs
export const sessionsAPI = {
  /**
   * Create a new research session
   */
  create: (data) => apiClient.post('/sessions', data),

  /**
   * Get list of sessions with pagination
   */
  list: (params) => apiClient.get('/sessions', { params }),

  /**
   * Get detailed session information
   */
  getDetail: (sessionId) => apiClient.get(`/sessions/${sessionId}`),

  /**
   * Update session
   */
  update: (sessionId, data) => apiClient.put(`/sessions/${sessionId}`, data),

  /**
   * Delete session
   */
  delete: (sessionId) => apiClient.delete(`/sessions/${sessionId}`),
};

// Workflow APIs
export const workflowAPI = {
  /**
   * Start workflow execution
   */
  start: (sessionId) => apiClient.post('/workflows/start', { session_id: sessionId }),

  /**
   * Get workflow progress
   */
  getProgress: (sessionId) => apiClient.get(`/workflows/${sessionId}/progress`),

  /**
   * Get workflow state
   */
  getState: (sessionId) => apiClient.get(`/workflows/${sessionId}/state`),

  /**
   * Retry failed workflow
   */
  retry: (sessionId) => apiClient.post(`/workflows/${sessionId}/retry`),
};

// Chat APIs
export const chatAPI = {
  /**
   * Send chat message
   */
  send: (sessionId, content) =>
    apiClient.post(`/sessions/${sessionId}/chat`, { content }),

  /**
   * Get chat history
   */
  getHistory: (sessionId, params) =>
    apiClient.get(`/sessions/${sessionId}/chat`, { params }),

  /**
   * Delete chat message
   */
  deleteMessage: (sessionId, messageId) =>
    apiClient.delete(`/sessions/${sessionId}/chat/${messageId}`),

  /**
   * Clear chat history
   */
  clearHistory: (sessionId) =>
    apiClient.post(`/sessions/${sessionId}/chat/clear`),
};

// Health check
export const healthAPI = {
  check: () => apiClient.get('/health'),
};

export default apiClient;
