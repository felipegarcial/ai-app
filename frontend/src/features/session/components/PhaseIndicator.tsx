import { Badge } from '@/shared/components/ui/badge';
import { useSessionStore } from '../store/sessionStore';
import type { Phase } from '@/shared/types';
import { FileText, MessageSquare, Sparkles, PenLine } from 'lucide-react';

const phaseConfig: Record<Phase, { label: string; icon: typeof FileText; className: string }> = {
  intake: {
    label: 'Getting Started',
    icon: MessageSquare,
    className: 'bg-blue-500/20 text-white border-blue-500/30',
  },
  clarification: {
    label: 'Clarifying Details',
    icon: Sparkles,
    className: 'bg-amber-500/20 text-white border-amber-500/30',
  },
  generation: {
    label: 'Generating Document',
    icon: FileText,
    className: 'bg-purple-500/20 text-white border-purple-500/30',
  },
  revision: {
    label: 'Review & Revise',
    icon: PenLine,
    className: 'bg-emerald-500/20 text-white border-emerald-500/30',
  },
};

export function PhaseIndicator() {
  const phase = useSessionStore((state) => state.phase);
  const config = phaseConfig[phase];
  const Icon = config.icon;

  return (
    <div className="px-3 py-2">
      <p className="text-xs text-white/60 mb-2 font-medium uppercase tracking-wider">
        Current Phase
      </p>
      <Badge variant="outline" className={`${config.className} gap-1.5 py-1.5 px-3`}>
        <Icon className="h-3.5 w-3.5" />
        {config.label}
      </Badge>
    </div>
  );
}
