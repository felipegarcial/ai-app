import { useState } from 'react';
import { Button } from '@/shared/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/shared/components/ui/dialog';
import { useSessionStore } from '../store/sessionStore';
import { useChatStore } from '@/features/chat/store/chatStore';
import { useDocumentStore } from '@/features/document/store/documentStore';
import { apiClient, endpoints } from '@/shared/api';
import { RotateCcw, Loader2 } from 'lucide-react';

export function ResetButton() {
  const [open, setOpen] = useState(false);
  const [isResetting, setIsResetting] = useState(false);

  const sessionId = useSessionStore((state) => state.sessionId);
  const resetSession = useSessionStore((state) => state.resetSession);
  const resetChat = useChatStore((state) => state.reset);
  const resetDocument = useDocumentStore((state) => state.reset);

  const handleReset = async () => {
    setIsResetting(true);

    try {
      // Call backend to reset session
      await apiClient.post(endpoints.chat.reset, { session_id: sessionId });
    } catch (error) {
      // Continue with local reset even if backend fails
      console.error('Failed to reset session on backend:', error);
    }

    // Reset all local stores
    resetSession();
    resetChat();
    resetDocument();

    setIsResetting(false);
    setOpen(false);
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button
          variant="outline"
          className="w-full bg-white/10 border-white/20 text-white hover:bg-white/20 hover:text-white"
        >
          <RotateCcw className="h-4 w-4 mr-2" />
          New Conversation
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Start New Conversation?</DialogTitle>
          <DialogDescription>
            This will clear your current conversation and all collected data.
            You'll start fresh with a new document request.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter className="gap-2 sm:gap-0">
          <Button variant="outline" onClick={() => setOpen(false)}>
            Cancel
          </Button>
          <Button
            variant="destructive"
            onClick={handleReset}
            disabled={isResetting}
          >
            {isResetting ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Resetting...
              </>
            ) : (
              <>
                <RotateCcw className="h-4 w-4 mr-2" />
                Reset
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
