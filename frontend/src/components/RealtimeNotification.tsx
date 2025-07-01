import { useState, useEffect } from 'react';
import { type SystemNotification, type StatusChange, type NewArticle } from '../services/websocket';
import './RealtimeNotification.css';

interface RealtimeNotificationProps {
  notification: SystemNotification | StatusChange | NewArticle;
  type: 'system' | 'status' | 'article';
  onDismiss: () => void;
  autoDismiss?: boolean;
  duration?: number;
}

const RealtimeNotification = ({
  notification,
  type,
  onDismiss,
  autoDismiss = true,
  duration = 5000
}: RealtimeNotificationProps) => {
  const [isVisible, setIsVisible] = useState(false);
  const [isDismissing, setIsDismissing] = useState(false);

  useEffect(() => {
    // Animate in
    const timer = setTimeout(() => setIsVisible(true), 100);
    
    // Auto dismiss
    if (autoDismiss) {
      const dismissTimer = setTimeout(() => {
        handleDismiss();
      }, duration);
      
      return () => {
        clearTimeout(timer);
        clearTimeout(dismissTimer);
      };
    }
    
    return () => clearTimeout(timer);
  }, [autoDismiss, duration]);

  const handleDismiss = () => {
    setIsDismissing(true);
    setTimeout(() => {
      onDismiss();
    }, 300); // Wait for exit animation
  };

  const getNotificationContent = () => {
    switch (type) {
      case 'system':
        const sysNotif = notification as SystemNotification;
        return {
          icon: getSystemIcon(sysNotif.level),
          title: sysNotif.title || 'System Update',
          message: sysNotif.message,
          color: getSystemColor(sysNotif.level)
        };
      
      case 'status':
        const statusNotif = notification as StatusChange;
        return {
          icon: '🔄',
          title: 'Status Changed',
          message: `Article "${statusNotif.articleId}" changed from ${statusNotif.oldStatus} to ${statusNotif.newStatus}`,
          color: '#0a4bb6'
        };
      
      case 'article':
        const articleNotif = notification as NewArticle;
        return {
          icon: '📰',
          title: 'New Article',
          message: `New article from ${articleNotif.source}`,
          color: '#f17500'
        };
      
      default:
        return {
          icon: 'ℹ️',
          title: 'Update',
          message: 'New update available',
          color: '#6c757d'
        };
    }
  };

  const getSystemIcon = (level: string) => {
    switch (level) {
      case 'success': return '✅';
      case 'warning': return '⚠️';
      case 'error': return '❌';
      default: return 'ℹ️';
    }
  };

  const getSystemColor = (level: string) => {
    switch (level) {
      case 'success': return '#28a745';
      case 'warning': return '#ffc107';
      case 'error': return '#dc3545';
      default: return '#17a2b8';
    }
  };

  const content = getNotificationContent();

  return (
    <div 
      className={`realtime-notification ${isVisible ? 'visible' : ''} ${isDismissing ? 'dismissing' : ''}`}
      style={{ '--notification-color': content.color } as React.CSSProperties}
    >
      <div className="notification-header">
        <div className="notification-icon">{content.icon}</div>
        <div className="notification-title">{content.title}</div>
        <button 
          onClick={handleDismiss}
          className="dismiss-btn"
          aria-label="Dismiss notification"
        >
          ×
        </button>
      </div>
      
      <div className="notification-message">
        {content.message}
      </div>
      
      <div className="notification-timestamp">
        {new Date().toLocaleTimeString()}
      </div>
      
      {/* Progress bar for auto-dismiss */}
      {autoDismiss && (
        <div className="notification-progress">
          <div 
            className="progress-bar"
            style={{ animationDuration: `${duration}ms` }}
          />
        </div>
      )}
    </div>
  );
};

export default RealtimeNotification; 