import { useChatStore } from '../store/chatStore';
import { Clock, Zap } from 'lucide-react';

export function ResponseMetadata() {
  const lastTokenCount = useChatStore((state) => state.lastTokenCount);
  const lastElapsedTime = useChatStore((state) => state.lastElapsedTime);
  const isStreaming = useChatStore((state) => state.isStreaming);
  const hasMessages = useChatStore((state) => state.messages.length > 0);

  // Don't show while streaming or if no data
  if (isStreaming || !hasMessages || (!lastTokenCount && !lastElapsedTime)) {
    return null;
  }

  const formatTime = (ms: number): string => {
    if (ms < 1000) return `${Math.round(ms)}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
  };

  return (
    <div className="flex items-center justify-center gap-4 py-2 text-xs text-muted-foreground border-t bg-muted/30">
      {lastTokenCount && lastTokenCount > 0 && (
        <div className="flex items-center gap-1">
          <Zap className="h-3 w-3" />
          <span>~{lastTokenCount} tokens</span>
        </div>
      )}
      {lastElapsedTime && lastElapsedTime > 0 && (
        <div className="flex items-center gap-1">
          <Clock className="h-3 w-3" />
          <span>{formatTime(lastElapsedTime)}</span>
        </div>
      )}
    </div>
  );
}
