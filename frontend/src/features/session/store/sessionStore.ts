import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Phase, DocumentType, Expertise, ConversationState } from '@/shared/types';

interface SessionState {
  // Session identification
  sessionId: string;

  // Conversation state from backend
  phase: Phase;
  documentType: DocumentType | null;
  expertise: Expertise | null;
  collectedData: Record<string, unknown>;
  missingFields: string[];

  // UI state
  isLoading: boolean;
}

interface SessionActions {
  setSessionId: (id: string) => void;
  updateFromBackend: (state: ConversationState) => void;
  resetSession: () => void;
  setLoading: (loading: boolean) => void;
}

type SessionStore = SessionState & SessionActions;

const generateSessionId = (): string => {
  return crypto.randomUUID();
};

const initialState: SessionState = {
  sessionId: generateSessionId(),
  phase: 'intake',
  documentType: null,
  expertise: null,
  collectedData: {},
  missingFields: [],
  isLoading: false,
};

export const useSessionStore = create<SessionStore>()(
  persist(
    (set) => ({
      ...initialState,

      setSessionId: (id) => set({ sessionId: id }),

      updateFromBackend: (backendState) =>
        set({
          phase: backendState.phase,
          documentType: backendState.document_type,
          expertise: backendState.expertise,
          collectedData: backendState.collected_data,
          missingFields: backendState.missing_fields,
        }),

      resetSession: () =>
        set({
          ...initialState,
          sessionId: generateSessionId(),
        }),

      setLoading: (loading) => set({ isLoading: loading }),
    }),
    {
      name: 'legal-doc-session',
      partialize: (state) => ({
        sessionId: state.sessionId,
      }),
    }
  )
);

// Selectors for common derived state
export const selectIsIntakePhase = (state: SessionStore) => state.phase === 'intake';
export const selectHasDocument = (state: SessionStore) => state.phase === 'revision';
export const selectProgress = (state: SessionStore) => {
  const phases: Phase[] = ['intake', 'clarification', 'generation', 'revision'];
  return ((phases.indexOf(state.phase) + 1) / phases.length) * 100;
};
