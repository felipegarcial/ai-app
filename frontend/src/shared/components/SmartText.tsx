import ReactMarkdown from 'react-markdown';
import { memo } from 'react';

interface SmartTextProps {
  content: string;
  className?: string;
}

// Patterns that indicate markdown formatting
const MARKDOWN_PATTERNS = [
  /\*\*[^*]+\*\*/,        // **bold**
  /\*[^*]+\*/,            // *italic*
  /^#+\s/m,               // # headers
  /^\d+\.\s/m,            // 1. numbered list
  /^[-*]\s/m,             // - bullet list
  /\[.+\]\(.+\)/,         // [link](url)
  /`[^`]+`/,              // `code`
  /^>\s/m,                // > blockquote
];

/**
 * Detects if text contains markdown formatting
 */
function hasMarkdown(text: string): boolean {
  return MARKDOWN_PATTERNS.some((pattern) => pattern.test(text));
}

/**
 * SmartText - Renders markdown only if detected, otherwise plain text
 */
export const SmartText = memo(function SmartText({ content, className }: SmartTextProps) {
  if (!content) return null;

  // If markdown detected, render with ReactMarkdown
  if (hasMarkdown(content)) {
    return (
      <div className={className}>
        <ReactMarkdown
          components={{
          // Custom styling for markdown elements
          p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
          strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
          em: ({ children }) => <em className="italic">{children}</em>,
          ul: ({ children }) => <ul className="list-disc list-inside mb-2 space-y-1">{children}</ul>,
          ol: ({ children }) => <ol className="list-decimal list-inside mb-2 space-y-1">{children}</ol>,
          li: ({ children }) => <li className="ml-2">{children}</li>,
          h1: ({ children }) => <h1 className="text-lg font-bold mb-2">{children}</h1>,
          h2: ({ children }) => <h2 className="text-base font-bold mb-2">{children}</h2>,
          h3: ({ children }) => <h3 className="text-sm font-bold mb-1">{children}</h3>,
          code: ({ children }) => (
            <code className="bg-black/10 dark:bg-white/10 px-1 py-0.5 rounded text-xs font-mono">
              {children}
            </code>
          ),
          blockquote: ({ children }) => (
            <blockquote className="border-l-2 border-current/30 pl-3 italic opacity-80">
              {children}
            </blockquote>
          ),
        }}
        >
          {content}
        </ReactMarkdown>
      </div>
    );
  }

  // Plain text - just render as is
  return <span className={className}>{content}</span>;
});
