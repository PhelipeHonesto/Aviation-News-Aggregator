import { useEffect, useState, useCallback, useMemo } from 'react';
import ArticleCard from '../components/ArticleCard';
import Toast from '../components/Toast';
import ErrorToast from '../components/ErrorToast';
import LoadingSpinner from '../components/LoadingSpinner';
import PullToRefresh from '../components/PullToRefresh';
import SearchAndFilter, { type FilterOptions } from '../components/SearchAndFilter';
import InfiniteScroll from '../components/InfiniteScroll';
import Pagination from '../components/Pagination';
import LoadMoreButton from '../components/LoadMoreButton';
import PaginationModeSelector from '../components/PaginationModeSelector';
import { usePagination, type PaginationMode } from '../hooks/usePagination';
import * as api from '../services/api';
import { getErrorInfo } from '../utils/errorHandler';
import { retry } from '../utils/retry';
import { getUniqueSources } from '../utils/filterUtils';
import type { Article } from '../types';
import type { ErrorInfo } from '../utils/errorHandler';
import './Feed.css';

const Feed = () => {
  // Component State
  const [articles, setArticles] = useState<Article[]>([]);
  const [actingArticleId, setActingArticleId] = useState<string | null>(null);
  const [filters, setFilters] = useState<FilterOptions>({
    search: '',
    status: [],
    sources: [],
    dateRange: {
      start: '',
      end: ''
    },
    sortBy: 'date',
    sortOrder: 'desc'
  });
  const [paginationMode, setPaginationMode] = useState<PaginationMode>('infinite');
  
  // Toast notification state
  const [toast, setToast] = useState<{
    message: string;
    type: 'success' | 'error' | 'info';
    isVisible: boolean;
  }>({
    message: '',
    type: 'info',
    isVisible: false
  });

  // Error handling state
  const [errorToast, setErrorToast] = useState<{
    errorInfo: ErrorInfo;
    isVisible: boolean;
  }>({
    errorInfo: {
      message: '',
      suggestion: '',
      retryable: false
    },
    isVisible: false
  });

  /**
   * Fetches all news from the API and updates the component's state.
   * This function is memoized with useCallback to prevent re-creation on every render.
   */
  const showToast = (message: string, type: 'success' | 'error' | 'info') => {
    setToast({ message, type, isVisible: true });
  };

  const hideToast = () => {
    setToast(prev => ({ ...prev, isVisible: false }));
  };

  const showErrorToast = (error: any, context: string) => {
    const errorInfo = getErrorInfo(error, context);
    setErrorToast({ errorInfo, isVisible: true });
  };

  const hideErrorToast = () => {
    setErrorToast(prev => ({ ...prev, isVisible: false }));
  };

  const handleRetry = (retryFn: () => Promise<void>) => {
    hideErrorToast();
    retryFn();
  };

  const loadNews = useCallback(async () => {
    setActingArticleId('loading_feed');
    try {
      const articles = await retry(() => api.getNews(), {
        maxAttempts: 3,
        baseDelay: 1000
      });
      setArticles(articles);
    } catch (err) {
      showErrorToast(err, 'loading news');
    } finally {
      setActingArticleId(null);
    }
  }, []);

  const retryLoadNews = () => {
    handleRetry(loadNews);
  };

  // Load news once when the component mounts.
  useEffect(() => {
    loadNews();
  }, [loadNews]);

  /**
   * Triggers the backend to ingest new articles from all sources,
   * then reloads the news feed to display them.
   */
  const handleIngestNews = async () => {
    setActingArticleId('ingesting');
    showToast('Ingesting new articles...', 'info');
    try {
      const response = await retry(() => api.ingestNews(), {
        maxAttempts: 2,
        baseDelay: 2000
      });
      showToast(response.message, 'success');
      loadNews(); // Refresh the feed
    } catch (err: any) {
      showErrorToast(err, 'ingesting news');
    } finally {
      setActingArticleId(null);
    }
  };

  const retryIngestNews = () => {
    handleRetry(handleIngestNews);
  };

  // Get unique sources for filter options
  const availableSources = useMemo(() => {
    return getUniqueSources(articles);
  }, [articles]);

  // Pagination system
  const pagination = usePagination(articles, filters, {
    mode: paginationMode,
    itemsPerPage: 20
  });

  const handleFilterChange = (newFilters: FilterOptions) => {
    setFilters(newFilters);
  };

  const handlePaginationModeChange = (mode: PaginationMode) => {
    setPaginationMode(mode);
  };

  /**
   * Handles user actions on an article card (e.g., select, edit, post).
   * @param action The type of action to perform.
   * @param storyId The ID of the target article.
   */
  const handleAction = async (action: 'select' | 'edit' | 'post', storyId: string) => {
    setActingArticleId(storyId);

    // Maps action types to their respective API calls and UI messages.
    const actionMap = {
      select: { apiCall: api.selectStory, loadingMessage: 'Selecting story...' },
      edit: { apiCall: api.editStory, loadingMessage: 'Editing with AI...' },
      post: { apiCall: api.postToSlack, loadingMessage: 'Posting to Slack...' },
    };

    try {
      const currentAction = actionMap[action];
      showToast(currentAction.loadingMessage, 'info');
      
      const response = await retry(() => currentAction.apiCall(storyId), {
        maxAttempts: 2,
        baseDelay: 1500
      });
      showToast(response.message, 'success');

      // After a successful action, reload all news to reflect the change.
      loadNews();
    } catch (err: any) {
      showErrorToast(err, `performing ${action} action`);
    } finally {
      setActingArticleId(null);
    }
  };

  /**
   * A helper function to determine if an action is currently in progress.
   * Used to disable buttons and show loading indicators.
   * @param id The optional ID of a specific article to check.
   * @returns boolean indicating if the UI should be in a loading state.
   */
  const isLoading = (id?: string) => {
    if (!actingArticleId) return false;
    // General loading states
    if (actingArticleId === 'loading_feed' || actingArticleId === 'ingesting') return true;
    // Specific article loading state
    if (id) return actingArticleId === id;
    return false;
  };

  return (
    <div>
      <div className="feed-header">
        <h1>News Feed</h1>
        <button onClick={handleIngestNews} disabled={isLoading()}>
          {isLoading('ingesting') ? (
            <>
              <LoadingSpinner size="small" color="white" />
              <span style={{ marginLeft: '8px' }}>Ingesting...</span>
            </>
          ) : isLoading('loading_feed') ? (
            <>
              <LoadingSpinner size="small" color="white" />
              <span style={{ marginLeft: '8px' }}>Loading...</span>
            </>
          ) : (
            'Update News'
          )}
        </button>
      </div>

      {/* Pagination Mode Selector */}
      <PaginationModeSelector
        currentMode={paginationMode}
        onModeChange={handlePaginationModeChange}
        totalItems={pagination.totalItems}
      />

      {/* Search and Filter Component */}
      <SearchAndFilter
        onFilterChange={handleFilterChange}
        availableSources={availableSources}
        totalArticles={articles.length}
        filteredCount={pagination.totalItems}
      />
      
      {/* Display a loading message or the list of articles */}
      {isLoading('loading_feed') && articles.length === 0 ? (
        <div className="loading-container">
          <LoadingSpinner size="large" />
          <p>Loading news feed...</p>
        </div>
      ) : (
        <PullToRefresh onRefresh={loadNews}>
          {/* Render articles based on pagination mode */}
          {pagination.currentItems.length > 0 ? (
            <>
              {/* Infinite Scroll Mode */}
              {paginationMode === 'infinite' && (
                <InfiniteScroll
                  onLoadMore={pagination.loadMore}
                  hasMore={pagination.hasMore}
                  isLoading={pagination.isLoading}
                >
                  <div className="articles-container">
                    {pagination.currentItems.map((article: Article) => (
                      <ArticleCard 
                        key={article.id} 
                        article={article} 
                        onAction={handleAction}
                        isLoading={isLoading(article.id)}
                      />
                    ))}
                  </div>
                </InfiniteScroll>
              )}

              {/* Traditional Pagination Mode */}
              {paginationMode === 'pagination' && (
                <>
                  <div className="articles-container">
                    {pagination.currentItems.map((article: Article) => (
                      <ArticleCard 
                        key={article.id} 
                        article={article} 
                        onAction={handleAction}
                        isLoading={isLoading(article.id)}
                      />
                    ))}
                  </div>
                  <Pagination
                    currentPage={pagination.currentPage}
                    totalPages={pagination.totalPages}
                    onPageChange={pagination.goToPage}
                    totalItems={pagination.totalItems}
                    itemsPerPage={pagination.itemsPerPage}
                  />
                </>
              )}

              {/* Load More Mode */}
              {paginationMode === 'load-more' && (
                <>
                  <div className="articles-container">
                    {pagination.currentItems.map((article: Article) => (
                      <ArticleCard 
                        key={article.id} 
                        article={article} 
                        onAction={handleAction}
                        isLoading={isLoading(article.id)}
                      />
                    ))}
                  </div>
                  <LoadMoreButton
                    onLoadMore={pagination.loadMore}
                    hasMore={pagination.hasMore}
                    isLoading={pagination.isLoading}
                    totalLoaded={pagination.currentItems.length}
                    totalAvailable={pagination.totalItems}
                  />
                </>
              )}
            </>
          ) : articles.length > 0 ? (
            <div className="no-results">
              <div className="no-results-icon">🔍</div>
              <h3>No articles found</h3>
              <p>Try adjusting your search criteria or filters</p>
            </div>
          ) : null}
        </PullToRefresh>
      )}

      {/* Toast notifications */}
      <Toast
        message={toast.message}
        type={toast.type}
        isVisible={toast.isVisible}
        onClose={hideToast}
      />

      {/* Error toast with retry functionality */}
      <ErrorToast
        errorInfo={errorToast.errorInfo}
        isVisible={errorToast.isVisible}
        onClose={hideErrorToast}
        onRetry={
          errorToast.errorInfo.retryable 
            ? (errorToast.errorInfo.message.includes('loading news') ? retryLoadNews : retryIngestNews)
            : undefined
        }
      />
    </div>
  );
};

export default Feed;
