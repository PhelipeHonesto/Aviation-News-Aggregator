import React, { useEffect, useRef, useCallback } from 'react';
import './InfiniteScroll.css';

interface InfiniteScrollProps {
  hasMore: boolean;
  isLoading: boolean;
  onLoadMore: () => void;
  threshold?: number;
  children: React.ReactNode;
  className?: string;
}

const InfiniteScroll: React.FC<InfiniteScrollProps> = ({
  hasMore,
  isLoading,
  onLoadMore,
  threshold = 200,
  children,
  className = ''
}) => {
  const observerRef = useRef<IntersectionObserver | null>(null);
  const sentinelRef = useRef<HTMLDivElement | null>(null);

  const handleIntersection = useCallback((entries: IntersectionObserverEntry[]) => {
    const [entry] = entries;
    if (entry.isIntersecting && hasMore && !isLoading) {
      onLoadMore();
    }
  }, [hasMore, isLoading, onLoadMore]);

  useEffect(() => {
    if (observerRef.current) {
      observerRef.current.disconnect();
    }

    observerRef.current = new IntersectionObserver(handleIntersection, {
      root: null,
      rootMargin: `${threshold}px`,
      threshold: 0.1
    });

    if (sentinelRef.current) {
      observerRef.current.observe(sentinelRef.current);
    }

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, [handleIntersection, threshold]);

  return (
    <div className={`infinite-scroll ${className}`}>
      {children}
      
      {/* Sentinel element for intersection observer */}
      <div ref={sentinelRef} className="infinite-scroll-sentinel">
        {isLoading && hasMore && (
          <div className="infinite-scroll-loading">
            <div className="osa-loading">
              <div className="osa-spinner"></div>
              <span>Loading more articles...</span>
            </div>
          </div>
        )}
        
        {!hasMore && (
          <div className="infinite-scroll-end">
            <p className="osa-caption">You've reached the end of the feed</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default InfiniteScroll;