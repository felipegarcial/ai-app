import type { ConversationState } from './api';

// SSE Event Types from backend
export type SSEEventType =
  | 'message'
  | 'function_call'
  | 'function_result'
  | 'document_update'
  | 'metadata'
  | 'error'
  | 'done';

// Token message event
export interface SSEMessageEvent {
  type: 'message';
  content: string;
}

// Function call event - when LLM invokes a function
export interface SSEFunctionCallEvent {
  type: 'function_call';
  name: string;
  arguments: Record<string, unknown>;
}

// Function result event - result of executed function
export interface SSEFunctionResultEvent {
  type: 'function_result';
  name: string;
  result: unknown;
}

// Document update event - document content changed
export interface SSEDocumentUpdateEvent {
  type: 'document_update';
  content: string;
  section?: string;
  action?: string;
}

// Metadata event - stats about the response
export interface SSEMetadataEvent {
  type: 'metadata';
  status: string;
  token_count_estimated?: number;
  char_count?: number;
  function_calls?: number;
  elapsed_time_ms?: number;
  phase?: string;
  session_id?: string;
  timestamp?: number;
}

// Error event
export interface SSEErrorEvent {
  type: 'error';
  message: string;
  code: string;
  recoverable: boolean;
  suggestion?: string;
}

// Done event - stream completed
export interface SSEDoneEvent {
  type: 'done';
  state: ConversationState;
  response: string;
}

// Union type for all SSE events
export type SSEEvent =
  | SSEMessageEvent
  | SSEFunctionCallEvent
  | SSEFunctionResultEvent
  | SSEDocumentUpdateEvent
  | SSEMetadataEvent
  | SSEErrorEvent
  | SSEDoneEvent;

// Type guard functions
export function isMessageEvent(event: SSEEvent): event is SSEMessageEvent {
  return event.type === 'message';
}

export function isFunctionCallEvent(event: SSEEvent): event is SSEFunctionCallEvent {
  return event.type === 'function_call';
}

export function isFunctionResultEvent(event: SSEEvent): event is SSEFunctionResultEvent {
  return event.type === 'function_result';
}

export function isDocumentUpdateEvent(event: SSEEvent): event is SSEDocumentUpdateEvent {
  return event.type === 'document_update';
}

export function isMetadataEvent(event: SSEEvent): event is SSEMetadataEvent {
  return event.type === 'metadata';
}

export function isErrorEvent(event: SSEEvent): event is SSEErrorEvent {
  return event.type === 'error';
}

export function isDoneEvent(event: SSEEvent): event is SSEDoneEvent {
  return event.type === 'done';
}
