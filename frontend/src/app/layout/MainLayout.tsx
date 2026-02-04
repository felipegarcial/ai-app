import { type ReactNode } from 'react';
import { Sidebar } from '@/features/session/components/Sidebar';
import { DocumentPreview } from '@/features/document/components/DocumentPreview';
import { DocumentViewButton } from '@/features/document/components/DocumentViewButton';
import { Sheet, SheetContent, SheetTrigger } from '@/shared/components/ui/sheet';
import { Button } from '@/shared/components/ui/button';
import { useIsMobile } from '@/shared/hooks';
import { Menu } from 'lucide-react';

interface MainLayoutProps {
  children: ReactNode;
}

export function MainLayout({ children }: MainLayoutProps) {
  const isMobile = useIsMobile();

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Desktop Sidebar */}
      {!isMobile && (
        <div className="w-72 flex-shrink-0">
          <Sidebar />
        </div>
      )}

      {/* Mobile Sidebar */}
      {isMobile && (
        <Sheet>
          <SheetTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="fixed top-4 left-4 z-50 bg-background/80 backdrop-blur-sm"
            >
              <Menu className="h-5 w-5" />
            </Button>
          </SheetTrigger>
          <SheetContent side="left" className="p-0 w-72">
            <Sidebar />
          </SheetContent>
        </Sheet>
      )}

      {/* Main Content */}
      <main className="flex-1 overflow-hidden">
        {children}
      </main>

      {/* Document Preview Modal */}
      <DocumentPreview />

      {/* Floating Document View Button */}
      <DocumentViewButton />
    </div>
  );
}
