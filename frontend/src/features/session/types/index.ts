import type { Phase, DocumentType, Expertise, ConversationState } from '@/shared/types';

export interface SessionState {
  // Session identification
  sessionId: string;

  // Conversation state
  phase: Phase;
  documentType: DocumentType | null;
  expertise: Expertise | null;
  collectedData: Record<string, unknown>;
  missingFields: string[];

  // UI state
  isLoading: boolean;

  // Actions
  setSessionId: (id: string) => void;
  updateFromBackend: (state: ConversationState) => void;
  resetSession: () => void;
  setLoading: (loading: boolean) => void;
}

export interface ConversationHistoryItem {
  id: string;
  title: string;
  preview: string;
  timestamp: Date;
  documentType: DocumentType | null;
}
