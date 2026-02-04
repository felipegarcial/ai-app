import { Button } from '@/shared/components/ui/button';
import { useDocumentStore, selectHasDocument } from '../store/documentStore';
import { FileText, Eye } from 'lucide-react';

export function DocumentViewButton() {
  const hasDocument = useDocumentStore(selectHasDocument);
  const openPreview = useDocumentStore((state) => state.openPreview);

  if (!hasDocument) return null;

  return (
    <Button
      onClick={openPreview}
      className="fixed bottom-24 right-6 shadow-lg bg-gradient-to-r from-purple-700 to-indigo-800 hover:from-purple-800 hover:to-indigo-900"
    >
      <Eye className="h-4 w-4 mr-2" />
      View Document
      <FileText className="h-4 w-4 ml-2" />
    </Button>
  );
}
