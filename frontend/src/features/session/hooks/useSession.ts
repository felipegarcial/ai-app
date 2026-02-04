import { useCallback } from 'react';
import { useSessionStore } from '../store/sessionStore';
import { useChatStore } from '@/features/chat/store/chatStore';
import { useDocumentStore } from '@/features/document/store/documentStore';
import { apiClient, endpoints } from '@/shared/api';
import type { StateResponse } from '@/shared/types';

/**
 * Hook for managing session operations
 */
export function useSession() {
  const sessionId = useSessionStore((state) => state.sessionId);
  const updateFromBackend = useSessionStore((state) => state.updateFromBackend);
  const resetSession = useSessionStore((state) => state.resetSession);
  const setLoading = useSessionStore((state) => state.setLoading);

  const resetChat = useChatStore((state) => state.reset);
  const resetDocument = useDocumentStore((state) => state.reset);

  /**
   * Fetch current session state from backend
   */
  const fetchState = useCallback(async () => {
    setLoading(true);
    try {
      const response = await apiClient.get<StateResponse>(
        endpoints.chat.state,
        { session_id: sessionId }
      );
      updateFromBackend(response.state);
      return response.state;
    } catch (error) {
      console.error('Failed to fetch session state:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [sessionId, updateFromBackend, setLoading]);

  /**
   * Reset the current session
   */
  const reset = useCallback(async () => {
    setLoading(true);
    try {
      await apiClient.post(endpoints.chat.reset, { session_id: sessionId });
    } catch (error) {
      console.error('Failed to reset session on backend:', error);
    } finally {
      resetSession();
      resetChat();
      resetDocument();
      setLoading(false);
    }
  }, [sessionId, resetSession, resetChat, resetDocument, setLoading]);

  return {
    sessionId,
    fetchState,
    reset,
  };
}
