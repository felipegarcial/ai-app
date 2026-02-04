import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/shared/components/ui/dialog';
import { useDocumentStore, selectHasDocument } from '../store/documentStore';
import { useSessionStore } from '@/features/session/store/sessionStore';
import { DocumentContent } from './DocumentContent';
import { DocumentActions } from './DocumentActions';
import { FileText } from 'lucide-react';

export function DocumentPreview() {
  const isOpen = useDocumentStore((state) => state.isPreviewOpen);
  const closePreview = useDocumentStore((state) => state.closePreview);
  const hasDocument = useDocumentStore(selectHasDocument);
  const documentType = useSessionStore((state) => state.documentType);

  const title = documentType === 'NDA'
    ? 'Non-Disclosure Agreement'
    : documentType === 'EMPLOYMENT'
      ? 'Employment Contract'
      : 'Legal Document';

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && closePreview()}>
      <DialogContent className="max-w-4xl h-[80vh] flex flex-col">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5 text-purple-600" />
            {title}
          </DialogTitle>
        </DialogHeader>

        <div className="flex-1 min-h-0 border rounded-lg bg-muted/30">
          <DocumentContent />
        </div>

        {hasDocument && <DocumentActions />}
      </DialogContent>
    </Dialog>
  );
}
