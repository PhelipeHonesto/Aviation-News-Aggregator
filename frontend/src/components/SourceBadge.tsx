import React from 'react';
import './SourceBadge.css';

interface SourceBadgeProps {
  source: string;
  className?: string;
  showFavicon?: boolean;
}

const SourceBadge: React.FC<SourceBadgeProps> = ({ 
  source, 
  className = '',
  showFavicon = true 
}) => {
  // Extract domain from source for favicon
  const getDomain = (source: string): string => {
    try {
      // If source looks like a URL, extract domain
      if (source.includes('.')) {
        const url = new URL(source.startsWith('http') ? source : `https://${source}`);
        return url.hostname;
      }
      return source;
    } catch {
      return source;
    }
  };

  const domain = getDomain(source);
  const faviconUrl = `https://www.google.com/s2/favicons?domain=${domain}&sz=16`;

  return (
    <div className={`source-badge ${className}`}>
      {showFavicon && (
        <img 
          src={faviconUrl} 
          alt={`${source} favicon`}
          className="source-favicon"
          onError={(e) => {
            // Hide favicon if it fails to load
            (e.target as HTMLImageElement).style.display = 'none';
          }}
        />
      )}
      <span className="source-name">{source}</span>
    </div>
  );
};

export default SourceBadge;
