import { useState, useEffect } from 'react';
import { websocketService } from '../services/websocket';
import './ConnectionStatus.css';

interface ConnectionStatusProps {
  showDetails?: boolean;
}

const ConnectionStatus = ({ showDetails = false }: ConnectionStatusProps) => {
  const [connectionState, setConnectionState] = useState(websocketService.getConnectionState());
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  useEffect(() => {
    const updateConnectionState = () => {
      setConnectionState(websocketService.getConnectionState());
      setLastUpdate(new Date());
    };

    // Update immediately
    updateConnectionState();

    // Set up interval to check connection state
    const interval = setInterval(updateConnectionState, 2000);

    return () => clearInterval(interval);
  }, []);

  const getStatusInfo = () => {
    switch (connectionState) {
      case 'connected':
        return {
          label: 'Connected',
          icon: '🟢',
          color: '#28a745',
          description: 'Real-time updates active'
        };
      case 'connecting':
        return {
          label: 'Connecting',
          icon: '🟡',
          color: '#ffc107',
          description: 'Establishing connection...'
        };
      case 'disconnected':
        return {
          label: 'Disconnected',
          icon: '🔴',
          color: '#dc3545',
          description: 'No real-time updates'
        };
      case 'closing':
        return {
          label: 'Disconnecting',
          icon: '🟠',
          color: '#fd7e14',
          description: 'Closing connection...'
        };
      default:
        return {
          label: 'Unknown',
          icon: '⚪',
          color: '#6c757d',
          description: 'Connection state unknown'
        };
    }
  };

  const statusInfo = getStatusInfo();

  return (
    <div className="connection-status">
      <div className="status-indicator" style={{ '--status-color': statusInfo.color } as React.CSSProperties}>
        <span className="status-icon">{statusInfo.icon}</span>
        <span className="status-label">{statusInfo.label}</span>
      </div>
      
      {showDetails && (
        <div className="status-details">
          <span className="status-description">{statusInfo.description}</span>
          {lastUpdate && (
            <span className="last-update">
              Last check: {lastUpdate.toLocaleTimeString()}
            </span>
          )}
        </div>
      )}
    </div>
  );
};

export default ConnectionStatus; 