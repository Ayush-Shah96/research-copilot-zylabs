/**
 * Custom React hooks for API calls and state management.
 */

import { useState, useCallback, useEffect } from 'react';
import { sessionsAPI, workflowAPI, chatAPI } from '../services/api';

/**
 * Hook for making API requests with loading and error handling
 */
export const useApi = (apiCall, options = {}) => {
  const [data, setData] = useState(options.initialData || null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const execute = useCallback(
    async (...args) => {
      setLoading(true);
      setError(null);
      try {
        const response = await apiCall(...args);
        setData(response.data);
        return response.data;
      } catch (err) {
        const errorMessage = err.response?.data?.detail || err.message;
        setError(errorMessage);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [apiCall]
  );

  return { data, loading, error, execute, setData, setError };
};

/**
 * Hook for managing sessions
 */
export const useSession = () => {
  const [sessions, setSessions] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch all sessions
  const fetchSessions = useCallback(async () => {
    setLoading(true);
    try {
      const response = await sessionsAPI.list({});
      setSessions(response.data.sessions || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch session details
  const fetchSessionDetail = useCallback(async (sessionId) => {
    setLoading(true);
    try {
      const response = await sessionsAPI.getDetail(sessionId);
      setCurrentSession(response.data);
      return response.data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Create new session
  const createSession = useCallback(async (sessionData) => {
    setLoading(true);
    try {
      const response = await sessionsAPI.create(sessionData);
      setSessions([response.data, ...sessions]);
      setCurrentSession(response.data);
      return response.data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [sessions]);

  // Delete session
  const deleteSession = useCallback(async (sessionId) => {
    try {
      await sessionsAPI.delete(sessionId);
      setSessions(sessions.filter((s) => s.id !== sessionId));
      if (currentSession?.id === sessionId) {
        setCurrentSession(null);
      }
    } catch (err) {
      setError(err.message);
      throw err;
    }
  }, [sessions, currentSession]);

  return {
    sessions,
    currentSession,
    loading,
    error,
    fetchSessions,
    fetchSessionDetail,
    createSession,
    deleteSession,
    setCurrentSession,
  };
};

/**
 * Hook for workflow execution and monitoring
 */
export const useWorkflow = () => {
  const [progress, setProgress] = useState(null);
  const [state, setState] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch progress
  const fetchProgress = useCallback(async (sessionId) => {
    try {
      const response = await workflowAPI.getProgress(sessionId);
      setProgress(response.data);
      return response.data;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  }, []);

  // Fetch state
  const fetchState = useCallback(async (sessionId) => {
    try {
      const response = await workflowAPI.getState(sessionId);
      setState(response.data);
      return response.data;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  }, []);

  // Start workflow
  const startWorkflow = useCallback(async (sessionId) => {
    setLoading(true);
    try {
      const response = await workflowAPI.start(sessionId);
      return response.data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Retry workflow
  const retryWorkflow = useCallback(async (sessionId) => {
    setLoading(true);
    try {
      const response = await workflowAPI.retry(sessionId);
      return response.data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    progress,
    state,
    loading,
    error,
    fetchProgress,
    fetchState,
    startWorkflow,
    retryWorkflow,
  };
};

/**
 * Hook for chat functionality
 */
export const useChat = (sessionId) => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch chat history
  const fetchHistory = useCallback(async () => {
    if (!sessionId) return;
    try {
      const response = await chatAPI.getHistory(sessionId, { limit: 50 });
      setMessages(response.data.messages || []);
    } catch (err) {
      setError(err.message);
    }
  }, [sessionId]);

  // Send message
  const sendMessage = useCallback(
    async (content) => {
      if (!sessionId) {
        setError('No session selected');
        return;
      }

      setLoading(true);
      try {
        // Add user message optimistically
        const userMessage = {
          id: `temp-${Date.now()}`,
          role: 'user',
          content,
          created_at: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, userMessage]);

        // Send to API
        const response = await chatAPI.send(sessionId, content);
        
        // Update with actual server response and add assistant message
        setMessages((prev) => {
          // Remove the temporary user message
          const filtered = prev.filter((m) => m.id !== userMessage.id);
          // Add the real user message and assistant response
          return [...filtered, userMessage, response.data];
        });
      } catch (err) {
        setError(err.message);
        // Remove the optimistic message on error
        setMessages((prev) => prev.filter((m) => m.id !== userMessage.id));
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [sessionId]
  );

  // Clear history
  const clearHistory = useCallback(async () => {
    if (!sessionId) return;
    try {
      await chatAPI.clearHistory(sessionId);
      setMessages([]);
    } catch (err) {
      setError(err.message);
      throw err;
    }
  }, [sessionId]);

  // Load history on mount
  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  return {
    messages,
    loading,
    error,
    sendMessage,
    clearHistory,
    setMessages,
  };
};
