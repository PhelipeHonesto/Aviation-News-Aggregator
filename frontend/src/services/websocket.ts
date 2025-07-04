export interface WebSocketMessage {
  type: 'article_update' | 'status_change' | 'new_article' | 'system_notification';
  data: any;
  timestamp: string;
}

export interface ArticleUpdate {
  id: string;
  status: string;
  title?: string;
  body?: string;
}

export interface StatusChange {
  articleId: string;
  oldStatus: string;
  newStatus: string;
  timestamp: string;
}

export interface NewArticle {
  article: any;
  source: string;
}

export interface SystemNotification {
  message: string;
  level: 'info' | 'success' | 'warning' | 'error';
  title?: string;
}

// WebSocketService class temporarily disabled
// class WebSocketService {
//   // ... implementation temporarily removed
// }

// Create singleton instance - TEMPORARILY DISABLED
// const wsUrl = import.meta.env.VITE_WS_URL || `ws://${window.location.hostname}:${window.location.port}/ws`;
// export const websocketService = new WebSocketService(wsUrl);

// Temporary mock service for development
export const websocketService = {
  connect: () => console.log('WebSocket temporarily disabled'),
  disconnect: () => console.log('WebSocket temporarily disabled'),
  send: () => console.log('WebSocket temporarily disabled'),
  isConnected: () => false,
  getConnectionState: () => 'disabled'
}; 
