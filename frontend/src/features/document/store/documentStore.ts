import { create } from 'zustand';

interface DocumentState {
  // Document content
  content: string | null;

  // Generation state
  isGenerating: boolean;
  generationProgress: number;

  // UI state
  isPreviewOpen: boolean;
}

interface DocumentActions {
  setContent: (content: string | null) => void;
  appendContent: (chunk: string) => void;
  setIsGenerating: (isGenerating: boolean) => void;
  setGenerationProgress: (progress: number) => void;
  openPreview: () => void;
  closePreview: () => void;
  togglePreview: () => void;
  reset: () => void;
}

type DocumentStore = DocumentState & DocumentActions;

const initialState: DocumentState = {
  content: null,
  isGenerating: false,
  generationProgress: 0,
  isPreviewOpen: false,
};

export const useDocumentStore = create<DocumentStore>((set) => ({
  ...initialState,

  setContent: (content) => set({ content }),

  appendContent: (chunk) =>
    set((state) => ({
      content: (state.content || '') + chunk,
    })),

  setIsGenerating: (isGenerating) =>
    set({
      isGenerating,
      generationProgress: isGenerating ? 0 : 100,
    }),

  setGenerationProgress: (progress) => set({ generationProgress: progress }),

  openPreview: () => set({ isPreviewOpen: true }),

  closePreview: () => set({ isPreviewOpen: false }),

  togglePreview: () =>
    set((state) => ({ isPreviewOpen: !state.isPreviewOpen })),

  reset: () => set(initialState),
}));

// Selectors
export const selectHasDocument = (state: DocumentStore) =>
  state.content !== null && state.content.length > 0;

export const selectWordCount = (state: DocumentStore) => {
  if (!state.content) return 0;
  return state.content.split(/\s+/).filter(Boolean).length;
};
