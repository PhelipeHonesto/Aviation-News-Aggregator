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

type WebSocketEventHandlers = {
  onArticleUpdate?: (update: ArticleUpdate) => void;
  onStatusChange?: (change: StatusChange) => void;
  onNewArticle?: (article: NewArticle) => void;
  onSystemNotification?: (notification: SystemNotification) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
};

class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private eventHandlers: WebSocketEventHandlers = {};
  private isConnecting = false;
  private shouldReconnect = true;

  constructor(private url: string) {}

  connect(handlers: WebSocketEventHandlers = {}) {
    if (this.ws?.readyState === WebSocket.OPEN || this.isConnecting) {
      return;
    }

    this.eventHandlers = handlers;
    this.isConnecting = true;

    try {
      this.ws = new WebSocket(this.url);
      this.setupEventListeners();
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      this.handleConnectionError();
    }
  }

  private setupEventListeners() {
    if (!this.ws) return;

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.isConnecting = false;
      this.reconnectAttempts = 0;
      this.eventHandlers.onConnect?.();
    };

    this.ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        this.handleMessage(message);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    this.ws.onclose = (event) => {
      console.log('WebSocket disconnected:', event.code, event.reason);
      this.isConnecting = false;
      this.eventHandlers.onDisconnect?.();
      
      if (this.shouldReconnect && !event.wasClean) {
        this.scheduleReconnect();
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.eventHandlers.onError?.(error);
    };
  }

  private handleMessage(message: WebSocketMessage) {
    switch (message.type) {
      case 'article_update':
        this.eventHandlers.onArticleUpdate?.(message.data);
        break;
      case 'status_change':
        this.eventHandlers.onStatusChange?.(message.data);
        break;
      case 'new_article':
        this.eventHandlers.onNewArticle?.(message.data);
        break;
      case 'system_notification':
        this.eventHandlers.onSystemNotification?.(message.data);
        break;
      default:
        console.warn('Unknown WebSocket message type:', message.type);
    }
  }

  private scheduleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
    
    console.log(`Scheduling reconnection attempt ${this.reconnectAttempts} in ${delay}ms`);
    
    this.reconnectTimer = setTimeout(() => {
      if (this.shouldReconnect) {
        this.connect(this.eventHandlers);
      }
    }, delay);
  }

  private handleConnectionError() {
    this.isConnecting = false;
    this.eventHandlers.onError?.(new Event('Connection failed'));
    
    if (this.shouldReconnect) {
      this.scheduleReconnect();
    }
  }

  disconnect() {
    this.shouldReconnect = false;
    
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }

    if (this.ws) {
      this.ws.close(1000, 'User initiated disconnect');
      this.ws = null;
    }
  }

  send(message: any) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected');
    }
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  getConnectionState(): string {
    if (!this.ws) return 'disconnected';
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return 'connecting';
      case WebSocket.OPEN:
        return 'connected';
      case WebSocket.CLOSING:
        return 'closing';
      case WebSocket.CLOSED:
        return 'closed';
      default:
        return 'unknown';
    }
  }
}

// Create singleton instance
const wsUrl = import.meta.env.VITE_WS_URL || `ws://${window.location.hostname}:8000/ws`;
export const websocketService = new WebSocketService(wsUrl); 
