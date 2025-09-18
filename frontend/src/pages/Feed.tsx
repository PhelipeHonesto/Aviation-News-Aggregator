import { useEffect, useState, useCallback, useMemo, useRef } from 'react';
import ArticleCard from '../components/ArticleCard';
import Toast from '../components/Toast';
import ErrorToast from '../components/ErrorToast';
import LoadingSpinner from '../components/LoadingSpinner';
import PullToRefresh from '../components/PullToRefresh';
import SearchAndFilter from '../components/SearchAndFilter';
import ConnectionStatus from '../components/ConnectionStatus';
import NotificationManager from '../components/NotificationManager';
import CategoryFilter from '../components/CategoryFilter';
import SourceBadge from '../components/SourceBadge';
import InfiniteScroll from '../components/InfiniteScroll';
import SocialDraftEditor from '../components/SocialDraftEditor';
import { websocketService, type ArticleUpdate, type StatusChange } from '../services/websocket';
import * as api from '../services/api';
import type { NewsResponse, NewsParams } from '../services/api';
import { getErrorInfo } from '../utils/errorHandler';
import { retry } from '../utils/retry';
import { getUniqueSources } from '../utils/filterUtils';
import type { Article } from '../types';
import type { ErrorInfo } from '../utils/errorHandler';

const Feed = () => {
  // Component State
  const [articles, setArticles] = useState<Article[]>([]);
  const [pagination, setPagination] = useState<NewsResponse['pagination'] | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [filters, setFilters] = useState<NewsParams>({});
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [actingArticleId, setActingArticleId] = useState<string | null>(null);
  
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

  // Social draft state
  const [socialDraftArticle, setSocialDraftArticle] = useState<Article | null>(null);

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

  const loadNews = useCallback(async (page: number = 1, reset: boolean = true) => {
    setActingArticleId('loading_feed');
    try {
      const params: NewsParams = {
        ...filters,
        q: searchQuery || undefined,
        category: selectedCategory || undefined,
        page,
        page_size: 20
      };
      
      const response = await api.getNews(params);
      
      if (reset || page === 1) {
        setArticles(response.articles);
      } else {
        setArticles(prev => [...prev, ...response.articles]);
      }
      
      setPagination(response.pagination);
      setCurrentPage(page);
      
      console.log("Fetched news:", response.articles);
    } catch (err) {
      console.error("Error fetching news:", err);
      showErrorToast(err, 'loading news');
    } finally {
      setActingArticleId(null);
    }
  }, [filters, searchQuery, selectedCategory, showErrorToast]);

  const retryLoadNews = () => {
    handleRetry(loadNews);
  };

  // Debounce timer for search
  const searchTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  
  // Handle search query changes with debounce
  const handleSearchChange = useCallback((query: string) => {
    setSearchQuery(query);
    setCurrentPage(1);
    
    // Clear previous timeout
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }
    
    // Set new timeout for API call
    searchTimeoutRef.current = setTimeout(() => {
      loadNews(1, true);
    }, 500); // 500ms delay
  }, []); // No dependencies - loadNews is stable

  // Handle category filter changes
  const handleCategoryChange = useCallback((category: string | null) => {
    setSelectedCategory(category);
    setCurrentPage(1);
    loadNews(1, true);
  }, []); // No dependencies - loadNews is stable

  // Handle infinite scroll load more
  const handleLoadMore = useCallback(() => {
    if (pagination?.has_next && !isLoading('loading_feed')) {
      loadNews(currentPage + 1, false);
    }
  }, [pagination, currentPage, loadNews]);

  // Load news once when the component mounts.
  useEffect(() => {
    loadNews(1, true);
  }, []); // Empty dependency array - run only once on mount
  
  // Cleanup search timeout on unmount
  useEffect(() => {
    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
    };
  }, []);

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
      loadNews(1, true); // Refresh the feed
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

  // WebSocket connection and live updates
  useEffect(() => {
    // Connect to WebSocket for live updates (optional)
    const connectWebSocket = async () => {
      try {
        await websocketService.connect();
        console.log('WebSocket connected for live updates');
      } catch (error) {
        console.warn('WebSocket not available, continuing without real-time updates:', error);
        // Don't throw - just continue without WebSocket
      }
    };

    // Only try to connect if WebSocket is supported
    if (typeof WebSocket !== 'undefined') {
      connectWebSocket();
    } else {
      console.warn('WebSocket not supported in this environment');
    }

    // Set up WebSocket message handlers
    const handleWebSocketMessage = (message: any) => {
      console.log('WebSocket message received:', message);
      
      switch (message.type) {
        case 'article_update':
          // Refresh the news feed when articles are updated
          loadNews(1, true);
          break;
        case 'status_change':
          // Update specific article status
          const statusChange = message.data as StatusChange;
          setArticles(prevArticles => 
            prevArticles.map(article => 
              article.id === statusChange.articleId 
                ? { ...article, status: statusChange.newStatus }
                : article
            )
          );
          break;
        case 'new_article':
          // Add new article to the list
          const newArticle = message.data.article;
          setArticles(prevArticles => [newArticle, ...prevArticles]);
          showToast('New article received!', 'info');
          break;
        case 'system_notification':
          // Show system notifications
          const notification = message.data;
          showToast(notification.message, notification.level);
          break;
        default:
          console.log('Unknown WebSocket message type:', message.type);
      }
    };

    websocketService.on('message', handleWebSocketMessage);

    // Fallback polling every 5 minutes (300 seconds)
    const pollInterval = setInterval(() => {
      loadNews(1, true); // Refresh news every 5 minutes
    }, 300000);

    return () => {
      clearInterval(pollInterval);
      websocketService.off('message', handleWebSocketMessage);
      websocketService.disconnect();
    };
  }, [showToast]); // Removed loadNews dependency to prevent circular updates

  /**
   * Handles user actions on an article card (e.g., select, edit, post).
   * @param action The type of action to perform.
   * @param storyId The ID of the target article.
   */
  const handleAction = async (action: 'select' | 'edit' | 'export' | 'social-draft', storyId: string) => {
    setActingArticleId(storyId);

    // Handle social draft action specially
    if (action === 'social-draft') {
      const article = articles.find(a => a.id === storyId);
      if (article) {
        setSocialDraftArticle(article);
        setActingArticleId(null);
      }
      return;
    }

    // Maps action types to their respective API calls and UI messages.
    const actionMap = {
      select: { apiCall: api.selectStory, loadingMessage: 'Selecting story...' },
      edit: { apiCall: api.editStory, loadingMessage: 'Marking as edited...' },
      export: { apiCall: api.exportStory, loadingMessage: 'Exporting story...' },
    };

    try {
      const currentAction = actionMap[action];
      showToast(currentAction.loadingMessage, 'info');
      
      const response = await retry(() => currentAction.apiCall(storyId), {
        maxAttempts: 2,
        baseDelay: 1500
      });
      
      // Handle export action specially
      if (action === 'export' && response.content) {
        // Download the exported content as a markdown file
        const blob = new Blob([response.content], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `article-${storyId}.md`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        showToast('Story exported and downloaded!', 'success');
      } else {
        showToast(response.message, 'success');
      }

                // After a successful action, reload all news to reflect the change.
                loadNews(1, true);
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

  // DEBUG: Log articles and pagination state (disabled to reduce noise)
  // useEffect(() => {
  //   console.log('[DEBUG] Articles:', articles.length, articles);
  // }, [articles]);


  return (
    <div className="osa-container">
      <ConnectionStatus />
      <NotificationManager />
      
      {/* OSA Header Section */}
      <div className="osa-section" style={{ paddingTop: 'var(--space-2xl)' }}>
        <div className="osa-flex-between osa-mb-4">
          <div>
            <h1 className="osa-heading-1">Loud Hawk News</h1>
            <p className="osa-body-large" style={{ color: 'var(--loud-gray-dark)' }}>
              Aviation news + community for pilots, students, and aviation enthusiasts
            </p>
          </div>
          <button 
            onClick={handleIngestNews}
            disabled={isLoading('ingesting')}
            className="osa-btn osa-btn-primary osa-btn-lg"
          >
            {isLoading('ingesting') ? (
              <div className="osa-loading">
                <div className="osa-spinner"></div>
                <span>Ingesting...</span>
              </div>
            ) : (
              <>
                🔄 Ingest News
              </>
            )}
          </button>
        </div>
        
                <SearchAndFilter
                  availableSources={availableSources}
                  totalArticles={pagination?.total_count || articles.length}
                  filteredCount={articles.length}
                  onFilterChange={() => {}}
                  onSearchChange={handleSearchChange}
                />
                
                <CategoryFilter
                  selectedCategory={selectedCategory}
                  onCategoryChange={handleCategoryChange}
                  className="osa-mb-4"
                />
      </div>

      {/* Articles Section */}
      <div className="osa-section" style={{ paddingTop: 0 }}>
        {isLoading('loading_feed') && articles.length === 0 ? (
          <div className="osa-flex-center" style={{ padding: 'var(--space-3xl) 0' }}>
            <div className="osa-text-center">
              <div className="osa-loading osa-mb-3">
                <div className="osa-spinner" style={{ width: '40px', height: '40px' }}></div>
              </div>
              <p className="osa-body-large">Loading aviation news...</p>
            </div>
          </div>
                ) : (
                  <PullToRefresh onRefresh={() => loadNews(1, true)}>
                    <InfiniteScroll
                      hasMore={pagination?.has_next || false}
                      isLoading={isLoading('loading_feed')}
                      onLoadMore={handleLoadMore}
                    >
                      <div className="osa-grid osa-grid-2">
                        {articles.length > 0 ? (
                          articles.map((article: Article) => (
                            <ArticleCard
                              key={article.id}
                              article={article}
                              onAction={handleAction}
                              isLoading={isLoading(article.id)}
                            />
                          ))
                        ) : (
                          <div className="osa-card osa-text-center" style={{ gridColumn: '1 / -1' }}>
                            <div style={{ fontSize: '4rem', marginBottom: 'var(--space-lg)' }}>📰</div>
                            <h3 className="osa-heading-3 osa-mb-2">No articles found</h3>
                            <p className="osa-body">Click "Ingest News" to fetch the latest aviation stories</p>
                          </div>
                        )}
                      </div>
                    </InfiniteScroll>
                  </PullToRefresh>
                )}
      </div>

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

      {/* Social Draft Editor Modal */}
      {socialDraftArticle && (
        <SocialDraftEditor
          article={socialDraftArticle}
          onClose={() => setSocialDraftArticle(null)}
          onStatusChange={(status) => {
            // Update the article status in the articles list
            setArticles(prevArticles => 
              prevArticles.map(article => 
                article.id === socialDraftArticle.id 
                  ? { ...article, status }
                  : article
              )
            );
            showToast(`Article status updated to ${status}`, 'success');
          }}
        />
      )}
    </div>
  );
};

export default Feed;
