import React from 'react';

interface LoudHawkLogoProps {
  size?: 'small' | 'medium' | 'large' | 'xlarge';
  variant?: 'full' | 'icon' | 'text' | 'news';
  color?: 'orange' | 'white' | 'black' | 'cream' | 'purple';
  className?: string;
}

const LoudHawkLogo: React.FC<LoudHawkLogoProps> = ({ 
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
    orange: 'var(--loud-orange)',
    white: 'var(--loud-white)',
    black: 'var(--loud-black)',
    cream: 'var(--loud-cream)',
    purple: 'var(--loud-purple)'
  };

  const currentSize = sizeMap[size];
  const currentColor = colorMap[color];

  const HawkIcon = () => (
    <svg 
      width={currentSize.width} 
      height={currentSize.height} 
      viewBox="0 0 200 100" 
      fill="none"
      className={className}
    >
      {/* Loud Hawk Icon - Geometric, looking toward horizon/future */}
      <g fill={currentColor}>
        {/* Hawk head - geometric, attentive */}
        <path d="M20 25C20 20 25 15 30 15C35 15 40 20 40 25C40 30 35 35 30 35C25 35 20 30 20 25Z" stroke="currentColor" strokeWidth="2" fill="none"/>
        
        {/* Beak - sharp, pointing right (horizon) */}
        <path d="M40 25L50 20L45 25L50 30L40 25Z" fill={currentColor}/>
        
        {/* Eye - attentive, geometric */}
        <circle cx="32" cy="23" r="2" fill={currentColor}/>
        
        {/* Body - robust, geometric */}
        <path d="M30 35C30 40 35 45 40 45C45 45 50 40 50 35" stroke="currentColor" strokeWidth="3" fill="none"/>
        
        {/* Wings - layered, geometric, dynamic */}
        <path d="M25 40L35 35L30 50L25 40Z" fill={currentColor}/>
        <path d="M35 35L45 30L40 50L35 35Z" fill={currentColor}/>
        <path d="M30 50L40 45L35 60L30 50Z" fill={currentColor}/>
        
        {/* Tail feathers - geometric */}
        <path d="M50 35L60 30L55 50L50 35Z" fill={currentColor}/>
        <path d="M55 50L65 45L60 65L55 50Z" fill={currentColor}/>
        
        {/* Legs - standing firm, geometric */}
        <path d="M35 45L35 55L30 60L40 60L35 55Z" fill={currentColor}/>
        <path d="M45 45L45 55L40 60L50 60L45 55Z" fill={currentColor}/>
        
        {/* "LH" Letters - geometric, bold */}
        {/* L */}
        <rect x="70" y="20" width="4" height="30" fill={currentColor}/>
        <rect x="70" y="45" width="15" height="4" fill={currentColor}/>
        
        {/* H */}
        <rect x="90" y="20" width="4" height="30" fill={currentColor}/>
        <rect x="100" y="20" width="4" height="30" fill={currentColor}/>
        <rect x="90" y="40" width="14" height="4" fill={currentColor}/>
        
        {/* Arrow in K - pointing right (horizon/future) */}
        <path d="M120 25L130 20L125 25L130 30L120 25Z" fill={currentColor}/>
        <path d="M125 30L135 25L130 30L135 35L125 30Z" fill={currentColor}/>
        <path d="M130 35L140 30L135 35L140 40L130 35Z" fill={currentColor}/>
      </g>
    </svg>
  );

  const LogoText = () => (
    <div className={`loud-hawk-brand ${className}`} style={{ color: currentColor, display: 'flex', alignItems: 'center', gap: 'var(--space-md)' }}>
      <HawkIcon />
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
        <div style={{ 
          fontFamily: 'var(--font-secondary)',
          fontWeight: '700',
          fontSize: currentSize.fontSize,
          lineHeight: 1.1,
          letterSpacing: '0.02em'
        }}>
          LOUD HAWK NEWS
        </div>
        <div style={{ 
          fontFamily: 'var(--font-secondary)', 
          fontSize: '0.65em', 
          fontWeight: '400',
          opacity: 0.9,
          marginTop: '2px',
          letterSpacing: '0.01em'
        }}>
          Aviation News + Community
        </div>
      </div>
    </div>
  );

  const NewsVariant = () => (
    <div className={`loud-hawk-news-brand ${className}`} style={{ color: currentColor, display: 'flex', alignItems: 'center', gap: 'var(--space-md)' }}>
      <HawkIcon />
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
        <div style={{ 
          fontFamily: 'var(--font-secondary)', 
          fontWeight: '700', 
          fontSize: currentSize.fontSize,
          lineHeight: 1.1,
          letterSpacing: '0.02em'
        }}>
          LOUD HAWK NEWS
        </div>
        <div style={{ 
          fontFamily: 'var(--font-secondary)', 
          fontSize: '0.65em', 
          fontWeight: '400',
          opacity: 0.9,
          marginTop: '2px',
          letterSpacing: '0.01em'
        }}>
          Aviation News + Community
        </div>
      </div>
    </div>
  );

  if (variant === 'icon') {
    return <HawkIcon />;
  }

  if (variant === 'text') {
    return (
      <div className={className} style={{ color: currentColor, textAlign: 'left' }}>
        <div style={{ 
          fontFamily: 'var(--font-secondary)', 
          fontWeight: '700', 
          fontSize: currentSize.fontSize,
          lineHeight: 1.1,
          letterSpacing: '0.02em'
        }}>
          LOUD HAWK NEWS
        </div>
        <div style={{ 
          fontFamily: 'var(--font-secondary)', 
          fontSize: '0.65em', 
          fontWeight: '400',
          opacity: 0.9,
          marginTop: '2px',
          letterSpacing: '0.01em'
        }}>
          Aviation News + Community
        </div>
      </div>
    );
  }

  if (variant === 'news') {
    return <NewsVariant />;
  }

  return <LogoText />;
};

export default LoudHawkLogo;