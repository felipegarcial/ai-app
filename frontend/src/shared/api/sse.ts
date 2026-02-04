import { API_BASE_URL } from './endpoints';
import type { SSEEvent } from '../types/events';

export class SSEError extends Error {
  code?: string;
  recoverable: boolean;

  constructor(message: string, code?: string, recoverable: boolean = false) {
    super(message);
    this.name = 'SSEError';
    this.code = code;
    this.recoverable = recoverable;
  }
}

interface SSEOptions {
  signal?: AbortSignal;
  onOpen?: () => void;
}

/**
 * Parse SSE line format into event object
 * SSE format:
 * event: <type>
 * data: <json>
 */
function parseSSELine(eventType: string, data: string): SSEEvent | null {
  try {
    const parsed = JSON.parse(data);

    // Handle different event formats
    if (eventType === 'message') {
      // Could be { content: "..." } or { data: "..." } or just the text
      const content = parsed.content ?? parsed.data ?? parsed.text ?? (typeof parsed === 'string' ? parsed : '');
      return { type: 'message', content } as SSEEvent;
    }

    // For other events, merge the parsed data
    return { type: eventType, ...parsed } as SSEEvent;
  } catch {
    // If data is plain text (for message events)
    if (eventType === 'message') {
      return { type: 'message', content: data } as SSEEvent;
    }
    console.error('Failed to parse SSE data:', data);
    return null;
  }
}

/**
 * Stream SSE events from a POST endpoint
 * Uses fetch + ReadableStream since EventSource only supports GET
 */
export async function* streamSSE(
  endpoint: string,
  body: unknown,
  options?: SSEOptions
): AsyncGenerator<SSEEvent, void, unknown> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'text/event-stream',
    },
    body: JSON.stringify(body),
    signal: options?.signal,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new SSEError(
      errorData.message || `Stream request failed with status ${response.status}`,
      errorData.code
    );
  }

  options?.onOpen?.();

  const reader = response.body?.getReader();
  if (!reader) {
    throw new SSEError('Response body is not readable');
  }

  const decoder = new TextDecoder();
  let buffer = '';
  let currentEventType = 'message';

  try {
    while (true) {
      const { done, value } = await reader.read();

      if (done) {
        break;
      }

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');

      // Keep the last incomplete line in the buffer
      buffer = lines.pop() || '';

      for (const line of lines) {
        const trimmedLine = line.trim();

        if (trimmedLine === '') {
          // Empty line - event boundary, reset event type
          currentEventType = 'message';
          continue;
        }

        if (trimmedLine.startsWith('event:')) {
          currentEventType = trimmedLine.slice(6).trim();
          continue;
        }

        if (trimmedLine.startsWith('data:')) {
          const data = trimmedLine.slice(5).trim();
          const event = parseSSELine(currentEventType, data);

          if (event) {
            yield event;

            // If it's an error event, we might want to throw
            if (event.type === 'error' && !event.recoverable) {
              throw new SSEError(event.message, event.code, event.recoverable);
            }
          }
        }
      }
    }

    // Process any remaining buffer
    if (buffer.trim()) {
      if (buffer.startsWith('data:')) {
        const data = buffer.slice(5).trim();
        const event = parseSSELine(currentEventType, data);
        if (event) {
          yield event;
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}

/**
 * Helper to consume SSE stream with callbacks
 */
export async function consumeSSEStream(
  endpoint: string,
  body: unknown,
  callbacks: {
    onMessage?: (content: string) => void;
    onFunctionCall?: (name: string, args: Record<string, unknown>) => void;
    onFunctionResult?: (name: string, result: unknown) => void;
    onDocumentUpdate?: (data: { content: string; section?: string; action?: string }) => void;
    onMetadata?: (metadata: { status: string; token_count_estimated?: number; elapsed_time_ms?: number }) => void;
    onError?: (error: { message: string; code: string; recoverable: boolean; suggestion?: string }) => void;
    onDone?: (data: { state: unknown; response: string }) => void;
  },
  options?: SSEOptions
): Promise<void> {
  const stream = streamSSE(endpoint, body, options);

  for await (const event of stream) {
    switch (event.type) {
      case 'message':
        callbacks.onMessage?.(event.content);
        break;
      case 'function_call':
        callbacks.onFunctionCall?.(event.name, event.arguments);
        break;
      case 'function_result':
        callbacks.onFunctionResult?.(event.name, event.result);
        break;
      case 'document_update':
        callbacks.onDocumentUpdate?.({
          content: event.content,
          section: event.section,
          action: event.action,
        });
        break;
      case 'metadata':
        callbacks.onMetadata?.({
          status: event.status,
          token_count_estimated: event.token_count_estimated,
          elapsed_time_ms: event.elapsed_time_ms,
        });
        break;
      case 'error':
        callbacks.onError?.({
          message: event.message,
          code: event.code,
          recoverable: event.recoverable,
          suggestion: event.suggestion,
        });
        break;
      case 'done':
        callbacks.onDone?.({
          state: event.state,
          response: event.response,
        });
        break;
    }
  }
}
