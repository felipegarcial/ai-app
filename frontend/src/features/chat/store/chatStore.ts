import { create } from 'zustand';
import type { Message, FunctionCall, ChatError } from '../types';

interface ChatState {
  // Messages
  messages: Message[];

  // Streaming state
  isStreaming: boolean;
  streamingMessageId: string | null;

  // Function calls
  currentFunctionCall: FunctionCall | null;
  functionCallHistory: FunctionCall[];

  // Error state
  error: ChatError | null;
  lastFailedMessage: string | null;

  // Metadata
  lastTokenCount: number | null;
  lastElapsedTime: number | null;
}

interface ChatActions {
  // Message actions
  addUserMessage: (content: string) => string;
  startAssistantMessage: () => string;
  appendToStream: (token: string) => void;
  finishStream: (finalContent?: string) => void;

  // Function call actions
  setFunctionCall: (name: string, args: Record<string, unknown>) => void;
  updateFunctionCallResult: (result: unknown) => void;
  clearFunctionCall: () => void;

  // Error actions
  setError: (error: ChatError, failedMessage?: string) => void;
  clearError: () => void;
  clearFailedMessage: () => void;

  // Metadata actions
  setMetadata: (tokenCount: number, elapsedTime: number) => void;

  // General actions
  clearMessages: () => void;
  reset: () => void;
}

type ChatStore = ChatState & ChatActions;

const initialState: ChatState = {
  messages: [],
  isStreaming: false,
  streamingMessageId: null,
  currentFunctionCall: null,
  functionCallHistory: [],
  error: null,
  lastFailedMessage: null,
  lastTokenCount: null,
  lastElapsedTime: null,
};

export const useChatStore = create<ChatStore>((set, get) => ({
  ...initialState,

  addUserMessage: (content) => {
    const id = crypto.randomUUID();
    const message: Message = {
      id,
      role: 'user',
      content,
      timestamp: new Date(),
    };

    set((state) => ({
      messages: [...state.messages, message],
      error: null, // Clear any previous errors
    }));

    return id;
  },

  startAssistantMessage: () => {
    const id = crypto.randomUUID();
    const message: Message = {
      id,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      isStreaming: true,
    };

    set((state) => ({
      messages: [...state.messages, message],
      isStreaming: true,
      streamingMessageId: id,
    }));

    return id;
  },

  appendToStream: (token) => {
    const { streamingMessageId } = get();
    if (!streamingMessageId) return;

    set((state) => ({
      messages: state.messages.map((msg) =>
        msg.id === streamingMessageId
          ? { ...msg, content: msg.content + token }
          : msg
      ),
    }));
  },

  finishStream: (finalContent) => {
    const { streamingMessageId } = get();
    if (!streamingMessageId) return;

    set((state) => ({
      messages: state.messages.map((msg) =>
        msg.id === streamingMessageId
          ? {
              ...msg,
              content: finalContent ?? msg.content,
              isStreaming: false,
            }
          : msg
      ),
      isStreaming: false,
      streamingMessageId: null,
    }));
  },

  setFunctionCall: (name, args) => {
    const functionCall: FunctionCall = {
      id: crypto.randomUUID(),
      name,
      arguments: args,
      status: 'executing',
      timestamp: new Date(),
    };

    set({ currentFunctionCall: functionCall });
  },

  updateFunctionCallResult: (result) => {
    set((state) => {
      if (!state.currentFunctionCall) return state;

      const completedCall: FunctionCall = {
        ...state.currentFunctionCall,
        result,
        status: 'completed',
      };

      return {
        currentFunctionCall: completedCall,
        functionCallHistory: [...state.functionCallHistory, completedCall],
      };
    });
  },

  clearFunctionCall: () => {
    set({ currentFunctionCall: null });
  },

  setError: (error, failedMessage) => {
    set({
      error,
      isStreaming: false,
      streamingMessageId: null,
      lastFailedMessage: failedMessage ?? null,
    });
  },

  clearError: () => {
    set({ error: null });
  },

  clearFailedMessage: () => {
    set({ lastFailedMessage: null });
  },

  setMetadata: (tokenCount, elapsedTime) => {
    set({
      lastTokenCount: tokenCount,
      lastElapsedTime: elapsedTime,
    });
  },

  clearMessages: () => {
    set({
      messages: [],
      functionCallHistory: [],
      error: null,
    });
  },

  reset: () => {
    set(initialState);
  },
}));

// Selectors
export const selectLastMessage = (state: ChatStore) =>
  state.messages[state.messages.length - 1];

export const selectHasMessages = (state: ChatStore) =>
  state.messages.length > 0;

export const selectIsWaitingForResponse = (state: ChatStore) =>
  state.isStreaming || state.currentFunctionCall?.status === 'executing';
