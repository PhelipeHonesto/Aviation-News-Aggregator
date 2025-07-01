import { useEffect, useRef, useCallback, useState } from 'react';
import './InfiniteScroll.css';

interface InfiniteScrollProps {
  children: React.ReactNode;
  onLoadMore: () => Promise<void>;
  hasMore: boolean;
  isLoading: boolean;
  threshold?: number; // Distance from bottom to trigger load (in pixels)
  rootMargin?: string; // CSS margin for intersection observer
}

const InfiniteScroll = ({
  children,
  onLoadMore,
  hasMore,
  isLoading,
  threshold = 100,
  rootMargin = '0px'
}: InfiniteScrollProps) => {
  const [observerTarget, setObserverTarget] = useState<HTMLDivElement | null>(null);
  const loadingRef = useRef<HTMLDivElement>(null);
  const [isIntersecting, setIsIntersecting] = useState(false);

  const handleIntersection = useCallback(
    (entries: IntersectionObserverEntry[]) => {
      const [entry] = entries;
      setIsIntersecting(entry.isIntersecting);
      
      if (entry.isIntersecting && hasMore && !isLoading) {
        onLoadMore();
      }
    },
    [hasMore, isLoading, onLoadMore]
  );

  useEffect(() => {
    if (!observerTarget) return;

    const observer = new IntersectionObserver(handleIntersection, {
      rootMargin: `${threshold}px ${rootMargin}`,
      threshold: 0.1
    });

    observer.observe(observerTarget);

    return () => {
      observer.disconnect();
    };
  }, [observerTarget, handleIntersection, threshold, rootMargin]);

  return (
    <div className="infinite-scroll-container">
      {children}
      
      {/* Observer target for intersection detection */}
      <div
        ref={setObserverTarget}
        className="infinite-scroll-observer"
        style={{ height: '1px' }}
      />
      
      {/* Loading indicator */}
      {isLoading && (
        <div ref={loadingRef} className="infinite-scroll-loading">
          <div className="loading-spinner"></div>
          <span>Loading more articles...</span>
        </div>
      )}
      
      {/* End of content indicator */}
      {!hasMore && !isLoading && (
        <div className="infinite-scroll-end">
          <span>You've reached the end! 🎉</span>
        </div>
      )}
    </div>
  );
};

export default InfiniteScroll; 
