import { useChatStore } from '../store/chatStore';
import { useSessionStore } from '@/features/session/store/sessionStore';
import { cn } from '@/shared/lib/utils';
import {
  Send,
  Brain,
  Sparkles,
  CheckCircle2,
  Loader2
} from 'lucide-react';

interface Step {
  id: string;
  label: string;
  icon: typeof Send;
}

const steps: Step[] = [
  { id: 'sending', label: 'Sending', icon: Send },
  { id: 'processing', label: 'Thinking', icon: Brain },
  { id: 'generating', label: 'Writing', icon: Sparkles },
];

type StepStatus = 'pending' | 'active' | 'completed';

export function ProcessingSteps() {
  const isStreaming = useChatStore((state) => state.isStreaming);
  const currentFunctionCall = useChatStore((state) => state.currentFunctionCall);
  const messages = useChatStore((state) => state.messages);
  const isLoading = useSessionStore((state) => state.isLoading);

  if (!isStreaming && !isLoading) return null;

  const getStepStatus = (stepId: string): StepStatus => {
    const lastMessage = messages[messages.length - 1];
    const hasContent = lastMessage?.role === 'assistant' && lastMessage.content.length > 0;

    switch (stepId) {
      case 'sending':
        return 'completed';
      case 'processing':
        if (currentFunctionCall || hasContent) return 'completed';
        return 'active';
      case 'generating':
        if (hasContent) return 'active';
        if (currentFunctionCall?.status === 'completed') return 'active';
        return 'pending';
      default:
        return 'pending';
    }
  };

  return (
    <div className="flex items-center justify-center gap-2 py-3 px-4">
      {steps.map((step, index) => {
        const status = getStepStatus(step.id);
        const Icon = step.icon;
        const isLast = index === steps.length - 1;

        return (
          <div key={step.id} className="flex items-center gap-2">
            {/* Step */}
            <div className="flex items-center gap-1.5">
              <div
                className={cn(
                  'flex items-center justify-center w-6 h-6 rounded-full transition-all duration-300',
                  status === 'completed' && 'bg-green-500 text-white',
                  status === 'active' && 'bg-purple-700 text-white',
                  status === 'pending' && 'bg-muted text-muted-foreground'
                )}
              >
                {status === 'completed' ? (
                  <CheckCircle2 className="h-3.5 w-3.5" />
                ) : status === 'active' ? (
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                ) : (
                  <Icon className="h-3.5 w-3.5" />
                )}
              </div>
              <span
                className={cn(
                  'text-xs font-medium transition-colors',
                  status === 'completed' && 'text-green-600',
                  status === 'active' && 'text-purple-700',
                  status === 'pending' && 'text-muted-foreground'
                )}
              >
                {step.label}
              </span>
            </div>

            {/* Connector line */}
            {!isLast && (
              <div
                className={cn(
                  'w-8 h-0.5 transition-colors duration-300',
                  status === 'completed' ? 'bg-green-500' : 'bg-muted'
                )}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}
