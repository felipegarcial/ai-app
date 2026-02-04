import { MainLayout } from './layout/MainLayout';
import { ChatContainer } from '@/features/chat/components/ChatContainer';
import { TooltipProvider } from '@/shared/components/ui/tooltip';
import { ErrorBoundary } from '@/shared/components/ErrorBoundary';
import { ChatErrorBoundary } from '@/shared/components/ChatErrorBoundary';
import { useChatStore } from '@/features/chat';
import { useSessionStore } from '@/features/session';

function App() {
  const resetChat = useChatStore((state) => state.reset);
  const resetSession = useSessionStore((state) => state.resetSession);

  const handleChatReset = () => {
    resetChat();
    resetSession();
  };

  return (
    <ErrorBoundary>
      <TooltipProvider>
        <MainLayout>
          <ChatErrorBoundary onReset={handleChatReset}>
            <ChatContainer />
          </ChatErrorBoundary>
        </MainLayout>
      </TooltipProvider>
    </ErrorBoundary>
  );
}

export default App;
