import { Component, type ErrorInfo, type ReactNode } from 'react';
import { AlertCircle, RefreshCw, MessageSquare } from 'lucide-react';
import { Button } from './ui/button';
import { Alert, AlertDescription, AlertTitle } from './ui/alert';

interface Props {
  children: ReactNode;
  onReset?: () => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ChatErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ChatErrorBoundary caught an error:', error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
    this.props.onReset?.();
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center h-full p-8 gap-4">
          <div className="p-4 bg-destructive/10 rounded-full">
            <MessageSquare className="h-12 w-12 text-destructive" />
          </div>

          <Alert variant="destructive" className="max-w-md">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Chat Error</AlertTitle>
            <AlertDescription>
              The chat encountered an error and couldn't recover.
              {this.state.error && (
                <span className="block mt-1 text-xs opacity-75">
                  {this.state.error.message}
                </span>
              )}
            </AlertDescription>
          </Alert>

          <Button onClick={this.handleReset}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Restart Chat
          </Button>
        </div>
      );
    }

    return this.props.children;
  }
}
