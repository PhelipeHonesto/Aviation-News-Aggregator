import React from 'react';

interface ArticleStatusBadgeProps {
  status: string;
  className?: string;
}

const ArticleStatusBadge: React.FC<ArticleStatusBadgeProps> = ({ status, className = '' }) => {
  const getStatusConfig = (status: string) => {
    switch (status) {
      case 'selected':
        return { 
          text: '🟡 SELECTED', 
          color: '#f17500',
          bgColor: 'rgba(241, 117, 0, 0.1)',
          borderColor: '#f17500'
        };
      case 'edited':
        return { 
          text: '🟢 EDITED', 
          color: '#0a4bb6',
          bgColor: 'rgba(10, 75, 182, 0.1)',
          borderColor: '#0a4bb6'
        };
      case 'exported':
        return { 
          text: '📤 EXPORTED', 
          color: '#28a745',
          bgColor: 'rgba(40, 167, 69, 0.1)',
          borderColor: '#28a745'
        };
      case 'skipped':
        return { 
          text: '🔴 SKIPPED', 
          color: '#d32f2f',
          bgColor: 'rgba(211, 47, 47, 0.1)',
          borderColor: '#d32f2f'
        };
      case 'draft':
        return { 
          text: '🟡 DRAFT', 
          color: '#fbc02d',
          bgColor: 'rgba(251, 192, 45, 0.1)',
          borderColor: '#fbc02d'
        };
      case 'ready':
        return { 
          text: '🟢 READY', 
          color: '#388e3c',
          bgColor: 'rgba(56, 142, 60, 0.1)',
          borderColor: '#388e3c'
        };
      default:
        return { 
          text: 'NEW', 
          color: '#6c757d',
          bgColor: 'rgba(108, 117, 125, 0.1)',
          borderColor: '#6c757d'
        };
    }
  };

  const config = getStatusConfig(status);

  return (
    <span 
      className={`osa-badge ${className}`}
      style={{
        color: config.color,
        backgroundColor: config.bgColor,
        border: `1px solid ${config.borderColor}`,
        padding: 'var(--space-xs) var(--space-md)',
        borderRadius: 'var(--radius-lg)',
        fontSize: '0.75rem',
        fontWeight: '600',
        textTransform: 'uppercase',
        letterSpacing: '0.05em',
        display: 'inline-flex',
        alignItems: 'center',
        whiteSpace: 'nowrap',
        gap: 'var(--space-xs)'
      }}
    >
      {config.text}
    </span>
  );
};

export default ArticleStatusBadge;
