import LoadingSpinner from './LoadingSpinner';
import './LoadMoreButton.css';

interface LoadMoreButtonProps {
  onLoadMore: () => Promise<void>;
  hasMore: boolean;
  isLoading: boolean;
  totalLoaded: number;
  totalAvailable: number;
}

const LoadMoreButton = ({
  onLoadMore,
  hasMore,
  isLoading,
  totalLoaded,
  totalAvailable
}: LoadMoreButtonProps) => {
  if (!hasMore) {
    return (
      <div className="load-more-end">
        <span>All {totalAvailable} articles loaded! 🎉</span>
      </div>
    );
  }

  return (
    <div className="load-more-container">
      <div className="load-more-info">
        <span>
          Showing {totalLoaded} of {totalAvailable} articles
        </span>
      </div>
      
      <button
        onClick={onLoadMore}
        disabled={isLoading}
        className="load-more-btn"
      >
        {isLoading ? (
          <>
            <LoadingSpinner size="small" color="white" />
            <span>Loading...</span>
          </>
        ) : (
          <>
            <span>Load More Articles</span>
            <span className="load-more-count">
              (+{Math.min(20, totalAvailable - totalLoaded)})
            </span>
          </>
        )}
      </button>
    </div>
  );
};

export default LoadMoreButton; 
