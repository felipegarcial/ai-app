export interface DocumentState {
  content: string | null;
  isGenerating: boolean;
  isPreviewOpen: boolean;
  generationProgress: number;
}

export interface DocumentMetadata {
  type: 'NDA' | 'EMPLOYMENT';
  generatedAt: Date;
  wordCount: number;
}
