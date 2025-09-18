import { useEffect, useState, useCallback, useMemo } from 'react';
import ArticleCard from '../components/ArticleCard';
import Toast from '../components/Toast';
import ErrorToast from '../components/ErrorToast';
import LoadingSpinner from '../components/LoadingSpinner';
import PullToRefresh from '../components/PullToRefresh';
import SearchAndFilter from '../components/SearchAndFilter';
import ConnectionStatus from '../components/ConnectionStatus';
import NotificationManager from '../components/NotificationManager';
// WebSocket temporarily disabled
// import { websocketService, type ArticleUpdate, type StatusChange } from '../services/websocket';
import * as api from '../services/api';
import { getErrorInfo } from '../utils/errorHandler';
import { retry } from '../utils/retry';
import { getUniqueSources } from '../utils/filterUtils';
import type { Article } from '../types';
import type { ErrorInfo } from '../utils/errorHandler';

const Feed = () => {
  // Component State
  const [articles, setArticles] = useState<Article[]>([]);
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
      // Try proxy first
      let response = await fetch("/api/news");
      if (!response.ok) throw new Error("Proxy fetch failed");
      let data = await response.json();
      if (!Array.isArray(data)) throw new Error("Response is not an array");
      setArticles(data);
      console.log("Fetched news from /api/news:", data);
    } catch (proxyErr) {
      try {
        // Fallback to direct backend fetch
        let response = await fetch("http://localhost:8000/news");
        if (!response.ok) throw new Error("Direct fetch failed");
        let data = await response.json();
        if (!Array.isArray(data)) throw new Error("Response is not an array");
        setArticles(data);
        console.log("Fetched news from backend:", data);
      } catch (err) {
        console.error("Error fetching news:", err);
        showErrorToast(err, 'loading news');
      }
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

  // Simple polling for updates (temporary replacement for WebSocket)
  useEffect(() => {
    const pollInterval = setInterval(() => {
      loadNews(); // Refresh news every 60 seconds
    }, 60000); // Increased to 60 seconds to reduce server load

    return () => clearInterval(pollInterval);
  }, [loadNews]);

  /**
   * Handles user actions on an article card (e.g., select, edit, post).
   * @param action The type of action to perform.
   * @param storyId The ID of the target article.
   */
  const handleAction = async (action: 'select' | 'edit' | 'export', storyId: string) => {
    setActingArticleId(storyId);

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

  // DEBUG: Log articles and pagination state
  useEffect(() => {
    console.log('[DEBUG] Articles:', articles.length, articles);
  }, [articles]);


  return (
    <div className="osa-container">
      <ConnectionStatus />
      <NotificationManager />
      
      {/* OSA Header Section */}
      <div className="osa-section" style={{ paddingTop: 'var(--space-2xl)' }}>
        <div className="osa-flex-between osa-mb-4">
          <div>
            <h1 className="osa-heading-1">Aviation News</h1>
            <p className="osa-body-large" style={{ color: 'var(--osa-medium-gray)' }}>
              Curate the latest aviation stories with precision and purpose
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
          totalArticles={articles.length}
          filteredCount={articles.length}
          onFilterChange={() => {}}
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
          <PullToRefresh onRefresh={loadNews}>
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
    </div>
  );
};

export default Feed;
