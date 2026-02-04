import { useCallback, useRef } from 'react';
import { useChatStore } from '../store/chatStore';
import { useSessionStore } from '@/features/session/store/sessionStore';
import { useDocumentStore } from '@/features/document/store/documentStore';
import { endpoints } from '@/shared/api/endpoints';
import { streamSSE, SSEError } from '@/shared/api/sse';
import type { ConversationState } from '@/shared/types';

export function useStreamingChat() {
  const abortControllerRef = useRef<AbortController | null>(null);

  // Session store
  const sessionId = useSessionStore((state) => state.sessionId);
  const updateFromBackend = useSessionStore((state) => state.updateFromBackend);
  const setSessionLoading = useSessionStore((state) => state.setLoading);

  // Chat store
  const addUserMessage = useChatStore((state) => state.addUserMessage);
  const startAssistantMessage = useChatStore((state) => state.startAssistantMessage);
  const appendToStream = useChatStore((state) => state.appendToStream);
  const finishStream = useChatStore((state) => state.finishStream);
  const setFunctionCall = useChatStore((state) => state.setFunctionCall);
  const updateFunctionCallResult = useChatStore((state) => state.updateFunctionCallResult);
  const clearFunctionCall = useChatStore((state) => state.clearFunctionCall);
  const setError = useChatStore((state) => state.setError);
  const clearFailedMessage = useChatStore((state) => state.clearFailedMessage);
  const setMetadata = useChatStore((state) => state.setMetadata);
  const isStreaming = useChatStore((state) => state.isStreaming);

  // Document store
  const setDocumentContent = useDocumentStore((state) => state.setContent);

  const sendMessage = useCallback(
    async (content: string) => {
      if (isStreaming) return;

      // Abort any existing request
      abortControllerRef.current?.abort();
      abortControllerRef.current = new AbortController();

      // Add user message immediately (optimistic UI)
      addUserMessage(content);

      // Start assistant message for streaming
      startAssistantMessage();
      setSessionLoading(true);

      let fullResponse = '';

      try {
        const stream = streamSSE(
          endpoints.chat.stream,
          { message: content, session_id: sessionId },
          { signal: abortControllerRef.current.signal }
        );

        for await (const event of stream) {
          switch (event.type) {
            case 'message':
              appendToStream(event.content);
              fullResponse += event.content;
              break;

            case 'function_call':
              setFunctionCall(event.name, event.arguments);
              break;

            case 'function_result':
              updateFunctionCallResult(event.result);
              // Small delay before clearing to show completion
              setTimeout(() => clearFunctionCall(), 500);
              break;

            case 'document_update':
              // Update document in real-time as it's being generated
              if (event.content) {
                setDocumentContent(event.content);
              }
              break;

            case 'metadata':
              if (event.token_count_estimated && event.elapsed_time_ms) {
                setMetadata(event.token_count_estimated, event.elapsed_time_ms);
              }
              break;

            case 'error':
              setError(
                {
                  message: event.message,
                  code: event.code,
                  recoverable: event.recoverable,
                  suggestion: event.suggestion,
                },
                content
              );
              break;

            case 'done':
              // Use the full response from done event (more reliable than streamed content)
              const finalResponse = event.response || fullResponse;
              finishStream(finalResponse);
              updateFromBackend(event.state as ConversationState);
              clearFailedMessage(); // Clear any previous failed message on success

              // Debug: log the state to see what's coming from backend
              console.log('[SSE Done] State received:', event.state);
              console.log('[SSE Done] current_document:', event.state?.current_document);

              // If there's a document, store it
              if (event.state?.current_document) {
                setDocumentContent(event.state.current_document);
              }
              break;
          }
        }
      } catch (error) {
        if (error instanceof SSEError) {
          setError(
            {
              message: error.message,
              code: error.code,
              recoverable: error.recoverable,
            },
            content
          );
        } else if (error instanceof Error && error.name !== 'AbortError') {
          setError(
            {
              message: error.message || 'An unexpected error occurred',
              recoverable: true,
            },
            content
          );
        }
        finishStream();
      } finally {
        setSessionLoading(false);
        abortControllerRef.current = null;
      }
    },
    [
      sessionId,
      isStreaming,
      addUserMessage,
      startAssistantMessage,
      appendToStream,
      finishStream,
      setFunctionCall,
      updateFunctionCallResult,
      clearFunctionCall,
      setError,
      clearFailedMessage,
      setMetadata,
      updateFromBackend,
      setDocumentContent,
      setSessionLoading,
    ]
  );

  const cancelStream = useCallback(() => {
    abortControllerRef.current?.abort();
    finishStream();
  }, [finishStream]);

  // Retry the last failed message
  const retryLastMessage = useCallback(async () => {
    const lastFailedMessage = useChatStore.getState().lastFailedMessage;
    if (!lastFailedMessage || isStreaming) return;

    // Abort any existing request
    abortControllerRef.current?.abort();
    abortControllerRef.current = new AbortController();

    // Don't add user message again - it's already there
    // Start assistant message for streaming
    startAssistantMessage();
    setSessionLoading(true);

    let fullResponse = '';

    try {
      const stream = streamSSE(
        endpoints.chat.stream,
        { message: lastFailedMessage, session_id: sessionId },
        { signal: abortControllerRef.current.signal }
      );

      for await (const event of stream) {
        switch (event.type) {
          case 'message':
            appendToStream(event.content);
            fullResponse += event.content;
            break;

          case 'function_call':
            setFunctionCall(event.name, event.arguments);
            break;

          case 'function_result':
            updateFunctionCallResult(event.result);
            setTimeout(() => clearFunctionCall(), 500);
            break;

          case 'document_update':
            if (event.content) {
              setDocumentContent(event.content);
            }
            break;

          case 'metadata':
            if (event.token_count_estimated && event.elapsed_time_ms) {
              setMetadata(event.token_count_estimated, event.elapsed_time_ms);
            }
            break;

          case 'error':
            setError(
              {
                message: event.message,
                code: event.code,
                recoverable: event.recoverable,
                suggestion: event.suggestion,
              },
              lastFailedMessage
            );
            break;

          case 'done':
            const finalResponse = event.response || fullResponse;
            finishStream(finalResponse);
            updateFromBackend(event.state as ConversationState);
            clearFailedMessage();

            if (event.state.current_document) {
              setDocumentContent(event.state.current_document);
            }
            break;
        }
      }
    } catch (error) {
      if (error instanceof SSEError) {
        setError(
          {
            message: error.message,
            code: error.code,
            recoverable: error.recoverable,
          },
          lastFailedMessage
        );
      } else if (error instanceof Error && error.name !== 'AbortError') {
        setError(
          {
            message: error.message || 'An unexpected error occurred',
            recoverable: true,
          },
          lastFailedMessage
        );
      }
      finishStream();
    } finally {
      setSessionLoading(false);
      abortControllerRef.current = null;
    }
  }, [
    sessionId,
    isStreaming,
    startAssistantMessage,
    appendToStream,
    finishStream,
    setFunctionCall,
    updateFunctionCallResult,
    clearFunctionCall,
    setError,
    clearFailedMessage,
    setMetadata,
    updateFromBackend,
    setDocumentContent,
    setSessionLoading,
  ]);

  return {
    sendMessage,
    cancelStream,
    retryLastMessage,
    isStreaming,
  };
}
