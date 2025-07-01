import { useState, useRef, useEffect } from 'react';
import './PullToRefresh.css';

interface PullToRefreshProps {
  children: React.ReactNode;
  onRefresh: () => Promise<void>;
  threshold?: number;
}

const PullToRefresh = ({ children, onRefresh, threshold = 80 }: PullToRefreshProps) => {
  const [isPulling, setIsPulling] = useState(false);
  const [pullDistance, setPullDistance] = useState(0);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const startY = useRef(0);
  const currentY = useRef(0);

  const handleTouchStart = (e: TouchEvent) => {
    if (isRefreshing) return;
    
    const scrollTop = containerRef.current?.scrollTop || 0;
    if (scrollTop > 0) return; // Only allow pull when at top
    
    startY.current = e.touches[0].clientY;
    currentY.current = e.touches[0].clientY;
  };

  const handleTouchMove = (e: TouchEvent) => {
    if (isRefreshing) return;
    
    const scrollTop = containerRef.current?.scrollTop || 0;
    if (scrollTop > 0) return;
    
    currentY.current = e.touches[0].clientY;
    const diff = currentY.current - startY.current;
    
    if (diff > 0) {
      e.preventDefault();
      setIsPulling(true);
      setPullDistance(Math.min(diff * 0.5, threshold * 1.5));
    }
  };

  const handleTouchEnd = async () => {
    if (isRefreshing || !isPulling) return;
    
    if (pullDistance >= threshold) {
      setIsRefreshing(true);
      try {
        await onRefresh();
      } catch (error) {
        console.error('Pull to refresh failed:', error);
      } finally {
        setIsRefreshing(false);
      }
    }
    
    setIsPulling(false);
    setPullDistance(0);
  };

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    container.addEventListener('touchstart', handleTouchStart, { passive: false });
    container.addEventListener('touchmove', handleTouchMove, { passive: false });
    container.addEventListener('touchend', handleTouchEnd, { passive: false });

    return () => {
      container.removeEventListener('touchstart', handleTouchStart);
      container.removeEventListener('touchmove', handleTouchMove);
      container.removeEventListener('touchend', handleTouchEnd);
    };
  }, [isRefreshing, isPulling, pullDistance, threshold]);

  const getRefreshIndicator = () => {
    if (isRefreshing) {
      return (
        <div className="refresh-indicator refreshing">
          <div className="refresh-spinner"></div>
          <span>Refreshing...</span>
        </div>
      );
    }
    
    if (isPulling) {
      const progress = Math.min(pullDistance / threshold, 1);
      return (
        <div className="refresh-indicator pulling" style={{ opacity: progress }}>
          <div className="refresh-arrow" style={{ transform: `rotate(${progress * 180}deg)` }}>
            ↓
          </div>
          <span>{pullDistance >= threshold ? 'Release to refresh' : 'Pull to refresh'}</span>
        </div>
      );
    }
    
    return null;
  };

  return (
    <div className="pull-to-refresh-container">
      {getRefreshIndicator()}
      <div 
        ref={containerRef}
        className="pull-to-refresh-content"
        style={{
          transform: isPulling ? `translateY(${pullDistance}px)` : 'translateY(0)',
          transition: isPulling ? 'none' : 'transform 0.3s ease'
        }}
      >
        {children}
      </div>
    </div>
  );
};

export default PullToRefresh; 
