import { useState } from 'react';
import { Button } from '@/shared/components/ui/button';
import { useDocumentStore, selectWordCount } from '../store/documentStore';
import { useSessionStore } from '@/features/session/store/sessionStore';
import { API_BASE_URL, endpoints } from '@/shared/api';
import { Copy, Download, Check, FileText, FileIcon, Loader2 } from 'lucide-react';

type ExportFormat = 'docx' | 'pdf';

export function DocumentActions() {
  const [copied, setCopied] = useState(false);
  const [exporting, setExporting] = useState<ExportFormat | null>(null);

  const content = useDocumentStore((state) => state.content);
  const wordCount = useDocumentStore(selectWordCount);
  const documentType = useSessionStore((state) => state.documentType);
  const collectedData = useSessionStore((state) => state.collectedData);

  const handleCopy = async () => {
    if (!content) return;

    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy:', error);
    }
  };

  const handleDownloadTxt = () => {
    if (!content) return;

    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${documentType || 'document'}_${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleExport = async (format: ExportFormat) => {
    if (!content) return;

    setExporting(format);

    try {
      const response = await fetch(`${API_BASE_URL}${endpoints.export[format]}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content,
          title: `${documentType || 'Legal'} Agreement`,
          metadata: {
            party_a: collectedData.party_a_name || collectedData.partyA || 'Party A',
            party_b: collectedData.party_b_name || collectedData.partyB || 'Party B',
            effective_date: new Date().toISOString().split('T')[0],
          },
        }),
      });

      if (!response.ok) {
        throw new Error(`Export failed: ${response.status}`);
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${documentType || 'document'}_${Date.now()}.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error(`Failed to export ${format}:`, error);
    } finally {
      setExporting(null);
    }
  };

  return (
    <div className="space-y-3 border-t pt-4">
      {/* Word count */}
      <div className="flex items-center justify-between text-sm text-muted-foreground">
        <span>{wordCount.toLocaleString()} words</span>
      </div>

      {/* Action buttons */}
      <div className="flex flex-wrap gap-2">
        {/* Copy */}
        <Button
          variant="outline"
          size="sm"
          onClick={handleCopy}
          disabled={!content}
        >
          {copied ? (
            <>
              <Check className="h-4 w-4 mr-2 text-green-500" />
              Copied!
            </>
          ) : (
            <>
              <Copy className="h-4 w-4 mr-2" />
              Copy
            </>
          )}
        </Button>

        {/* Download TXT */}
        <Button
          variant="outline"
          size="sm"
          onClick={handleDownloadTxt}
          disabled={!content}
        >
          <Download className="h-4 w-4 mr-2" />
          TXT
        </Button>

        {/* Download Word */}
        <Button
          variant="outline"
          size="sm"
          onClick={() => handleExport('docx')}
          disabled={!content || exporting !== null}
          className="text-blue-600 border-blue-200 hover:bg-blue-50 hover:border-blue-300"
        >
          {exporting === 'docx' ? (
            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
          ) : (
            <FileText className="h-4 w-4 mr-2" />
          )}
          Word
        </Button>

        {/* Download PDF */}
        <Button
          variant="outline"
          size="sm"
          onClick={() => handleExport('pdf')}
          disabled={!content || exporting !== null}
          className="text-red-600 border-red-200 hover:bg-red-50 hover:border-red-300"
        >
          {exporting === 'pdf' ? (
            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
          ) : (
            <FileIcon className="h-4 w-4 mr-2" />
          )}
          PDF
        </Button>
      </div>
    </div>
  );
}
