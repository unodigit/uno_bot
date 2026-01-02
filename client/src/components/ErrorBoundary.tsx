import React, { Component, ReactNode } from 'react';

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

/**
 * Error Boundary component to catch JavaScript errors in child components,
 * display a fallback UI, and log the error for debugging.
 */
class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    // Update state so the next render will show the fallback UI
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Log the error to an error reporting service
    console.error('ErrorBoundary caught an error:', {
      error: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
    });

    // You could also send to an error tracking service here
    // e.g., Sentry, LogRocket, etc.
    if (window.location.hostname !== 'localhost') {
      // In production, could send to monitoring service
      fetch('/api/v1/errors', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: error.message,
          stack: error.stack,
          componentStack: errorInfo.componentStack,
          url: window.location.href,
          timestamp: new Date().toISOString(),
        }),
      }).catch(() => {
        // Silently fail if error reporting itself fails
      });
    }
  }

  componentDidUpdate(prevProps: ErrorBoundaryProps) {
    // Reset error state if children change (useful for recovery)
    if (prevProps.children !== this.props.children && this.state.hasError) {
      this.setState({ hasError: false, error: null });
    }
  }

  handleReset = () => {
    // Allow users to attempt recovery
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      // Render fallback UI
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="error-boundary-fallback">
          <div style={{
            padding: '2rem',
            margin: '2rem',
            border: '2px solid #EF4444',
            borderRadius: '8px',
            backgroundColor: '#FEF2F2',
          }}>
            <h2 style={{ color: '#B91C1C', marginBottom: '1rem' }}>
              ⚠️ Something went wrong
            </h2>
            <p style={{ color: '#78716C', marginBottom: '1rem' }}>
              We encountered an unexpected error. Our team has been notified.
            </p>
            <details style={{ marginBottom: '1rem', color: '#57534E' }}>
              <summary>Technical Details</summary>
              <pre style={{
                marginTop: '0.5rem',
                padding: '0.5rem',
                backgroundColor: '#F5F5F4',
                borderRadius: '4px',
                overflow: 'auto',
                fontSize: '0.875rem',
              }}>
                {this.state.error?.message}
              </pre>
            </details>
            <button
              onClick={this.handleReset}
              style={{
                padding: '0.5rem 1rem',
                backgroundColor: '#DC2626',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
              }}
            >
              Try Again
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
