import { ScrollArea } from '@/shared/components/ui/scroll-area';
import { useDocumentStore } from '../store/documentStore';
import { Skeleton } from '@/shared/components/ui/skeleton';

export function DocumentContent() {
  const content = useDocumentStore((state) => state.content);
  const isGenerating = useDocumentStore((state) => state.isGenerating);

  if (isGenerating) {
    return (
      <div className="space-y-4 p-4">
        <Skeleton className="h-6 w-3/4" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-2/3" />
        <Skeleton className="h-6 w-1/2 mt-6" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-3/4" />
      </div>
    );
  }

  if (!content) {
    return (
      <div className="flex items-center justify-center h-full text-muted-foreground">
        No document generated yet
      </div>
    );
  }

  return (
    <ScrollArea className="h-full">
      <div className="p-6">
        <div className="prose prose-sm max-w-none dark:prose-invert">
          <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed text-foreground">
            {content}
          </pre>
        </div>
      </div>
    </ScrollArea>
  );
}
