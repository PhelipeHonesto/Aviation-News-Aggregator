import { useEffect } from 'react';
import type { ErrorInfo } from '../utils/errorHandler';
import './ErrorToast.css';

interface ErrorToastProps {
  errorInfo: ErrorInfo;
  isVisible: boolean;
  onClose: () => void;
  onRetry?: () => void;
  duration?: number;
}

const ErrorToast = ({ errorInfo, isVisible, onClose, onRetry, duration = 8000 }: ErrorToastProps) => {
  useEffect(() => {
    if (isVisible && duration > 0) {
      const timer = setTimeout(() => {
        onClose();
      }, duration);
      return () => clearTimeout(timer);
    }
  }, [isVisible, duration, onClose]);

  if (!isVisible) return null;

  return (
    <div className={`error-toast ${isVisible ? 'show' : ''}`}>
      <div className="error-toast-content">
        <div className="error-toast-header">
          <span className="error-toast-icon">❌</span>
          <span className="error-toast-title">{errorInfo.message}</span>
          <button className="error-toast-close" onClick={onClose}>
            ×
          </button>
        </div>
        <div className="error-toast-body">
          <p className="error-toast-suggestion">{errorInfo.suggestion}</p>
          {errorInfo.retryable && onRetry && (
            <button className="error-toast-retry" onClick={onRetry}>
              {errorInfo.action || 'Retry'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default ErrorToast; 