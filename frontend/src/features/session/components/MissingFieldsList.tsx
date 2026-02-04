import { Card, CardContent, CardHeader, CardTitle } from '@/shared/components/ui/card';
import { Badge } from '@/shared/components/ui/badge';
import { useSessionStore } from '../store/sessionStore';
import { AlertCircle, Circle } from 'lucide-react';

function formatFieldName(field: string): string {
  return field
    .replace(/_/g, ' ')
    .replace(/([A-Z])/g, ' $1')
    .replace(/^./, (str) => str.toUpperCase())
    .trim();
}

export function MissingFieldsList() {
  const missingFields = useSessionStore((state) => state.missingFields);

  if (missingFields.length === 0) {
    return null;
  }

  return (
    <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
      <CardHeader className="pb-2 pt-3 px-3">
        <CardTitle className="text-sm font-medium text-white flex items-center justify-between">
          <span className="flex items-center gap-2">
            <AlertCircle className="h-4 w-4 text-amber-400" />
            Missing Fields
          </span>
          <Badge variant="secondary" className="bg-white/20 text-white text-xs">
            {missingFields.length}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="px-3 pb-3">
        <ul className="space-y-1.5">
          {missingFields.map((field) => (
            <li
              key={field}
              className="flex items-center gap-2 text-xs text-white/70"
            >
              <Circle className="h-1.5 w-1.5 fill-amber-400 text-amber-400" />
              {formatFieldName(field)}
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}
