import React from 'react';

interface OSALogoProps {
  size?: 'small' | 'medium' | 'large' | 'xlarge';
  variant?: 'full' | 'icon' | 'text';
  color?: 'orange' | 'white' | 'black' | 'gray';
  className?: string;
}

const OSALogo: React.FC<OSALogoProps> = ({ 
  size = 'medium', 
  variant = 'full', 
  color = 'orange',
  className = '' 
}) => {
  const sizeMap = {
    small: { width: 32, height: 32, fontSize: '0.75rem' },
    medium: { width: 48, height: 48, fontSize: '1rem' },
    large: { width: 64, height: 64, fontSize: '1.25rem' },
    xlarge: { width: 96, height: 96, fontSize: '1.5rem' }
  };

  const colorMap = {
    orange: '#FF6B35',
    white: '#FFFFFF',
    black: '#2C2C2C',
    gray: '#6C757D'
  };

  const currentSize = sizeMap[size];
  const currentColor = colorMap[color];

  const LogoIcon = () => (
    <svg 
      width={currentSize.width} 
      height={currentSize.height} 
      viewBox="0 0 200 100" 
      fill="none"
      className={className}
    >
      {/* Top horizontal lines - thicker and more prominent */}
      <rect x="20" y="15" width="160" height="6" fill={currentColor} rx="3"/>
      <rect x="20" y="25" width="160" height="6" fill={currentColor} rx="3"/>
      
      {/* The "-852-" stylized numbers - exact match to the image */}
      <g fill={currentColor}>
        {/* Hyphen before 8 */}
        <rect x="25" y="45" width="15" height="5" rx="2"/>
        
        {/* Number 8 - segmented, digital display style */}
        <rect x="50" y="35" width="18" height="8" rx="1"/>
        <rect x="50" y="47" width="18" height="8" rx="1"/>
        <rect x="50" y="59" width="18" height="8" rx="1"/>
        
        {/* Number 5 - very angular, segmented design */}
        <rect x="80" y="35" width="18" height="8" rx="1"/>
        <rect x="80" y="47" width="9" height="8" rx="1"/>
        <rect x="80" y="59" width="18" height="8" rx="1"/>
        <rect x="89" y="71" width="9" height="8" rx="1"/>
        
        {/* Number 2 - angular, segmented */}
        <rect x="110" y="35" width="18" height="8" rx="1"/>
        <rect x="110" y="47" width="9" height="8" rx="1"/>
        <rect x="110" y="59" width="18" height="8" rx="1"/>
        <rect x="110" y="71" width="9" height="8" rx="1"/>
        
        {/* Hyphen after 2 */}
        <rect x="140" y="45" width="15" height="5" rx="2"/>
      </g>
      
      {/* Bottom horizontal lines */}
      <rect x="20" y="75" width="160" height="6" fill={currentColor} rx="3"/>
      <rect x="20" y="85" width="160" height="6" fill={currentColor} rx="3"/>
      
      {/* Registered trademark symbol - positioned like in the image */}
      <circle cx="170" cy="30" r="4" fill={currentColor}/>
      <text x="170" y="33" textAnchor="middle" fontSize="5" fill="white" fontWeight="bold">®</text>
    </svg>
  );

  const LogoText = () => (
    <div className={`osa-nav-brand ${className}`} style={{ color: currentColor, display: 'flex', alignItems: 'center', gap: 'var(--space-md)' }}>
      <LogoIcon />
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
        <div style={{ 
          fontFamily: 'var(--font-primary)', 
          fontWeight: '800', 
          fontSize: currentSize.fontSize,
          lineHeight: 1.1,
          letterSpacing: '0.02em'
        }}>
          Orange Sunshine Aviation
        </div>
        <div style={{ 
          fontFamily: 'var(--font-secondary)', 
          fontSize: '0.65em', 
          fontWeight: '400',
          opacity: 0.9,
          marginTop: '2px',
          letterSpacing: '0.01em'
        }}>
          Runway to your future
        </div>
      </div>
    </div>
  );

  if (variant === 'icon') {
    return <LogoIcon />;
  }

  if (variant === 'text') {
    return (
      <div className={className} style={{ color: currentColor, textAlign: 'left' }}>
        <div style={{ 
          fontFamily: 'var(--font-primary)', 
          fontWeight: '800', 
          fontSize: currentSize.fontSize,
          lineHeight: 1.1,
          letterSpacing: '0.02em'
        }}>
          Orange Sunshine Aviation
        </div>
        <div style={{ 
          fontFamily: 'var(--font-secondary)', 
          fontSize: '0.65em', 
          fontWeight: '400',
          opacity: 0.9,
          marginTop: '2px',
          letterSpacing: '0.01em'
        }}>
          Runway to your future
        </div>
      </div>
    );
  }

  return <LogoText />;
};

export default OSALogo;
