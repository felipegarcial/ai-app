export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000';

export const endpoints = {
  chat: {
    send: '/api/chat/',
    stream: '/api/chat/stream',
    state: '/api/chat/state',
    reset: '/api/chat/reset',
  },
  document: {
    generate: '/api/generate-document',
  },
  export: {
    docx: '/api/export/docx',
    pdf: '/api/export/pdf',
    preview: '/api/export/preview',
  },
} as const;

// Helper to build full URL
export function buildUrl(endpoint: string, params?: Record<string, string>): string {
  const url = new URL(`${API_BASE_URL}${endpoint}`);
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      url.searchParams.append(key, value);
    });
  }
  return url.toString();
}
