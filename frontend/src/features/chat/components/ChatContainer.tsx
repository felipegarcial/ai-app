import { useChatStore, selectHasMessages } from '../store/chatStore';
import { useStreamingChat } from '../hooks/useStreamingChat';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';
import { WelcomeScreen } from './WelcomeScreen';
import { ProcessingSteps } from './ProcessingSteps';
import { ResponseMetadata } from './ResponseMetadata';
import { Alert, AlertDescription, AlertTitle } from '@/shared/components/ui/alert';
import { AlertCircle, X, RefreshCw } from 'lucide-react';
import { Button } from '@/shared/components/ui/button';

export function ChatContainer() {
  const hasMessages = useChatStore(selectHasMessages);
  const error = useChatStore((state) => state.error);
  const lastFailedMessage = useChatStore((state) => state.lastFailedMessage);
  const clearError = useChatStore((state) => state.clearError);
  const { retryLastMessage, isStreaming } = useStreamingChat();

  const handleRetry = () => {
    clearError();
    retryLastMessage();
  };

  return (
    <div className="flex flex-col h-full bg-background">
      {/* Error Alert */}
      {error && (
        <div className="px-4 pt-4">
          <Alert variant="destructive" className="relative">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error.message}</AlertDescription>
            {error.suggestion && (
              <p className="text-sm mt-1 opacity-80">{error.suggestion}</p>
            )}
            <div className="flex items-center gap-2 mt-3">
              {error.recoverable && lastFailedMessage && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleRetry}
                  disabled={isStreaming}
                  className="bg-white hover:bg-gray-100"
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Reintentar
                </Button>
              )}
              <Button
                variant="ghost"
                size="sm"
                onClick={clearError}
              >
                <X className="h-4 w-4 mr-2" />
                Cerrar
              </Button>
            </div>
          </Alert>
        </div>
      )}

      {/* Main Content */}
      {hasMessages ? <MessageList /> : <WelcomeScreen />}

      {/* Processing Steps */}
      <ProcessingSteps />

      {/* Response Metadata */}
      <ResponseMetadata />

      {/* Input */}
      <ChatInput />
    </div>
  );
}
