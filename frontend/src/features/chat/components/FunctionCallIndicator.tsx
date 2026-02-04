import { useChatStore } from '../store/chatStore';
import { Loader2, CheckCircle2, Cog } from 'lucide-react';
import { cn } from '@/shared/lib/utils';

const functionLabels: Record<string, string> = {
  collect_nda_data: 'Collecting NDA information',
  collect_employment_data: 'Collecting employment contract details',
  validate_data: 'Validating information',
  generate_document: 'Generating document',
  update_document: 'Updating document',
};

export function FunctionCallIndicator() {
  const currentFunctionCall = useChatStore((state) => state.currentFunctionCall);

  if (!currentFunctionCall) return null;

  const isCompleted = currentFunctionCall.status === 'completed';
  const label = functionLabels[currentFunctionCall.name] || currentFunctionCall.name;

  return (
    <div
      className={cn(
        'flex items-center gap-3 px-4 py-3 rounded-lg mx-4 mb-2',
        'bg-gradient-to-r from-purple-500/10 to-indigo-500/10',
        'border border-purple-500/20',
        'animate-in fade-in-0 slide-in-from-bottom-2 duration-300'
      )}
    >
      <div
        className={cn(
          'p-2 rounded-full',
          isCompleted ? 'bg-green-500/20' : 'bg-purple-500/20'
        )}
      >
        {isCompleted ? (
          <CheckCircle2 className="h-4 w-4 text-green-500" />
        ) : (
          <Loader2 className="h-4 w-4 text-purple-500 animate-spin" />
        )}
      </div>

      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-foreground">
          {label}
        </p>
        <p className="text-xs text-muted-foreground">
          {isCompleted ? 'Completed' : 'Processing...'}
        </p>
      </div>

      <Cog
        className={cn(
          'h-4 w-4 text-muted-foreground',
          !isCompleted && 'animate-spin'
        )}
      />
    </div>
  );
}
