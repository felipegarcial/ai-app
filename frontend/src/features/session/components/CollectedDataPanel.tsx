import { Card, CardContent, CardHeader, CardTitle } from '@/shared/components/ui/card';
import { ScrollArea } from '@/shared/components/ui/scroll-area';
import { useSessionStore } from '../store/sessionStore';
import { Database, ChevronRight } from 'lucide-react';

function formatValue(value: unknown): string {
  if (value === null || value === undefined) return '—';
  if (typeof value === 'boolean') return value ? 'Yes' : 'No';
  if (typeof value === 'object') return JSON.stringify(value);
  return String(value);
}

function formatKey(key: string): string {
  return key
    .replace(/_/g, ' ')
    .replace(/([A-Z])/g, ' $1')
    .replace(/^./, (str) => str.toUpperCase())
    .trim();
}

export function CollectedDataPanel() {
  const collectedData = useSessionStore((state) => state.collectedData);
  const documentType = useSessionStore((state) => state.documentType);
  const expertise = useSessionStore((state) => state.expertise);

  const entries = Object.entries(collectedData);
  const hasData = entries.length > 0 || documentType || expertise;

  return (
    <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
      <CardHeader className="pb-2 pt-3 px-3">
        <CardTitle className="text-sm font-medium text-white flex items-center gap-2">
          <Database className="h-4 w-4" />
          Collected Data
        </CardTitle>
      </CardHeader>
      <CardContent className="px-3 pb-3">
        {!hasData ? (
          <p className="text-xs text-white/50 italic">
            No data collected yet. Start a conversation to begin.
          </p>
        ) : (
          <ScrollArea className="max-h-48">
            <div className="space-y-2">
              {documentType && (
                <DataRow label="Document Type" value={documentType} />
              )}
              {expertise && (
                <DataRow label="Expertise Level" value={expertise} />
              )}
              {entries.map(([key, value]) => (
                <DataRow key={key} label={formatKey(key)} value={formatValue(value)} />
              ))}
            </div>
          </ScrollArea>
        )}
      </CardContent>
    </Card>
  );
}

function DataRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-start gap-2 text-xs">
      <ChevronRight className="h-3 w-3 text-white/40 mt-0.5 flex-shrink-0" />
      <div className="min-w-0">
        <span className="text-white/60">{label}:</span>{' '}
        <span className="text-white font-medium break-words">{value}</span>
      </div>
    </div>
  );
}
