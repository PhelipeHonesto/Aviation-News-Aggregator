import React from 'react';

interface ErrorBoundaryState {
  error?: Error;
}

interface ErrorBoundaryProps {
  children: React.ReactNode;
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { error: undefined };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.error) {
      return (
        <div style={{ 
          padding: '20px', 
          fontFamily: 'sans-serif',
          background: '#fff',
          color: '#222',
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <h2 style={{ color: '#e74c3c', marginBottom: '16px' }}>🚨 UI Crashed</h2>
          <div style={{ 
            background: '#f8f9fa', 
            padding: '16px', 
            borderRadius: '8px',
            border: '1px solid #dee2e6',
            maxWidth: '600px',
            width: '100%'
          }}>
            <h3 style={{ marginTop: 0, color: '#495057' }}>Error Details:</h3>
            <pre style={{ 
              whiteSpace: 'pre-wrap', 
              fontSize: '14px',
              color: '#dc3545',
              background: '#fff5f5',
              padding: '12px',
              borderRadius: '4px',
              border: '1px solid #fecaca'
            }}>
              {String(this.state.error)}
            </pre>
            <p style={{ marginBottom: 0, color: '#6c757d' }}>
              Open DevTools → Console for full stack trace.
            </p>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
