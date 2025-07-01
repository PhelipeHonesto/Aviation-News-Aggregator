import { useState, useRef } from 'react';
import './SwipeableCard.css';

interface SwipeableCardProps {
  children: React.ReactNode;
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  leftAction?: { label: string; color: string };
  rightAction?: { label: string; color: string };
  disabled?: boolean;
}

const SwipeableCard = ({ 
  children, 
  onSwipeLeft, 
  onSwipeRight, 
  leftAction, 
  rightAction, 
  disabled = false 
}: SwipeableCardProps) => {
  const [isDragging, setIsDragging] = useState(false);
  const [startX, setStartX] = useState(0);
  const [currentX, setCurrentX] = useState(0);
  const [translateX, setTranslateX] = useState(0);
  const cardRef = useRef<HTMLDivElement>(null);

  const handleTouchStart = (e: React.TouchEvent) => {
    if (disabled) return;
    setIsDragging(true);
    setStartX(e.touches[0].clientX);
    setCurrentX(e.touches[0].clientX);
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    if (!isDragging || disabled) return;
    e.preventDefault();
    setCurrentX(e.touches[0].clientX);
    const diff = currentX - startX;
    const clampedDiff = Math.max(-100, Math.min(100, diff));
    setTranslateX(clampedDiff);
  };

  const handleTouchEnd = () => {
    if (!isDragging || disabled) return;
    setIsDragging(false);
    
    const diff = currentX - startX;
    const threshold = 60;

    if (Math.abs(diff) > threshold) {
      if (diff > 0 && onSwipeRight) {
        onSwipeRight();
      } else if (diff < 0 && onSwipeLeft) {
        onSwipeLeft();
      }
    }
    
    setTranslateX(0);
  };

  const getSwipeDirection = () => {
    if (translateX > 20) return 'right';
    if (translateX < -20) return 'left';
    return 'none';
  };

  const swipeDirection = getSwipeDirection();

  return (
    <div className="swipeable-card-container">
      {/* Background Actions */}
      <div className="swipe-actions">
        {leftAction && (
          <div 
            className={`swipe-action left ${swipeDirection === 'left' ? 'visible' : ''}`}
            style={{ backgroundColor: leftAction.color }}
          >
            <span>{leftAction.label}</span>
          </div>
        )}
        {rightAction && (
          <div 
            className={`swipe-action right ${swipeDirection === 'right' ? 'visible' : ''}`}
            style={{ backgroundColor: rightAction.color }}
          >
            <span>{rightAction.label}</span>
          </div>
        )}
      </div>

      {/* Card Content */}
      <div
        ref={cardRef}
        className={`swipeable-card ${isDragging ? 'dragging' : ''}`}
        style={{
          transform: `translateX(${translateX}px)`,
          transition: isDragging ? 'none' : 'transform 0.3s ease'
        }}
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
      >
        {children}
      </div>
    </div>
  );
};

export default SwipeableCard; 
