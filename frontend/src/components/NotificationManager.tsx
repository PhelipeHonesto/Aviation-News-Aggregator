import { useState, useEffect } from 'react';
import { 
  websocketService, 
  type SystemNotification, 
  type StatusChange, 
  type NewArticle 
} from '../services/websocket';
import RealtimeNotification from './RealtimeNotification';
import './NotificationManager.css';

interface NotificationItem {
  id: string;
  notification: SystemNotification | StatusChange | NewArticle;
  type: 'system' | 'status' | 'article';
  timestamp: Date;
}

const NotificationManager = () => {
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const handlers = {
      onSystemNotification: (notification: SystemNotification) => {
        addNotification(notification, 'system');
      },
      onStatusChange: (change: StatusChange) => {
        addNotification(change, 'status');
      },
      onNewArticle: (article: NewArticle) => {
        addNotification(article, 'article');
      },
      onConnect: () => {
        addNotification({
          message: 'Real-time connection established',
          level: 'success',
          title: 'Connected'
        }, 'system');
      },
      onDisconnect: () => {
        addNotification({
          message: 'Real-time connection lost',
          level: 'warning',
          title: 'Disconnected'
        }, 'system');
      },
      onError: () => {
        addNotification({
          message: 'Connection error occurred',
          level: 'error',
          title: 'Error'
        }, 'system');
      }
    };

    websocketService.connect(handlers);

    return () => {
      websocketService.disconnect();
    };
  }, []);

  const addNotification = (
    notification: SystemNotification | StatusChange | NewArticle,
    type: 'system' | 'status' | 'article'
  ) => {
    const id = `${type}-${Date.now()}-${Math.random()}`;
    const newNotification: NotificationItem = {
      id,
      notification,
      type,
      timestamp: new Date()
    };

    setNotifications(prev => {
      const updated = [newNotification, ...prev.slice(0, 4)]; // Keep max 5 notifications
      return updated;
    });

    // Show notification area
    setIsVisible(true);
  };

  const removeNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
    
    // Hide notification area if no notifications
    if (notifications.length <= 1) {
      setTimeout(() => setIsVisible(false), 300);
    }
  };

  const clearAllNotifications = () => {
    setNotifications([]);
    setIsVisible(false);
  };

  if (!isVisible || notifications.length === 0) {
    return null;
  }

  return (
    <div className="notification-manager">
      <div className="notification-header">
        <h3>Live Updates</h3>
        <button 
          onClick={clearAllNotifications}
          className="clear-all-btn"
          aria-label="Clear all notifications"
        >
          Clear All
        </button>
      </div>
      
      <div className="notifications-list">
        {notifications.map((item) => (
          <RealtimeNotification
            key={item.id}
            notification={item.notification}
            type={item.type}
            onDismiss={() => removeNotification(item.id)}
            autoDismiss={item.type === 'system' ? (item.notification as SystemNotification).level !== 'error' : true}
            duration={item.type === 'system' && (item.notification as SystemNotification).level === 'error' ? 8000 : 5000}
          />
        ))}
      </div>
    </div>
  );
};

export default NotificationManager; 
