// Conversation phases
export type Phase = 'intake' | 'clarification' | 'generation' | 'revision';

// Document types supported
export type DocumentType = 'NDA' | 'EMPLOYMENT';

// User expertise levels
export type Expertise = 'beginner' | 'intermediate' | 'expert';

// Conversation state from backend
export interface ConversationState {
  phase: Phase;
  document_type: DocumentType | null;
  expertise: Expertise | null;
  collected_data: Record<string, unknown>;
  missing_fields: string[];
  current_document: string | null;
}

// Chat API request
export interface ChatRequest {
  message: string;
  session_id: string;
}

// Chat API response (non-streaming)
export interface ChatResponse {
  response: string;
  state: ConversationState;
}

// Reset session request
export interface ResetRequest {
  session_id: string;
}

// Reset session response
export interface ResetResponse {
  success: boolean;
  session_id: string;
}

// State query response
export interface StateResponse {
  state: ConversationState;
  session_id: string;
}

// Generate document request
export interface GenerateDocumentRequest {
  session_id: string;
}
