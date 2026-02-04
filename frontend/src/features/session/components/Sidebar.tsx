import { PhaseIndicator } from './PhaseIndicator';
import { CollectedDataPanel } from './CollectedDataPanel';
import { MissingFieldsList } from './MissingFieldsList';
import { ResetButton } from './ResetButton';
import { Separator } from '@/shared/components/ui/separator';
import { ScrollArea } from '@/shared/components/ui/scroll-area';
import { Scale } from 'lucide-react';

export function Sidebar() {
  return (
    <aside className="flex flex-col h-full bg-gradient-to-b from-slate-950 to-purple-950">
      {/* Logo */}
      <div className="p-4 flex items-center gap-2">
        <div className="p-2 bg-white/20 rounded-lg">
          <Scale className="h-6 w-6 text-white" />
        </div>
        <div>
          <h1 className="text-lg font-bold text-white">LegalDoc</h1>
          <p className="text-xs text-white/60">AI Document Generator</p>
        </div>
      </div>

      <Separator className="bg-white/20" />

      {/* Phase Indicator */}
      <div className="pt-4">
        <PhaseIndicator />
      </div>

      {/* Scrollable Content */}
      <ScrollArea className="flex-1 px-3 py-4">
        <div className="space-y-4">
          <CollectedDataPanel />
          <MissingFieldsList />
        </div>
      </ScrollArea>

      {/* Footer */}
      <div className="p-4 mt-auto">
        <ResetButton />

        {/* Attribution */}
        <p className="text-xs text-white/40 text-center mt-4">
          Powered by AI
        </p>
      </div>
    </aside>
  );
}
