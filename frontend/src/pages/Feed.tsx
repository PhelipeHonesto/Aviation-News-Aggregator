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
import './Feed.css';

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
      const response = await fetch("/api/news");
      const data = await response.json();
      console.log("Fetched news:", data);
      setArticles(data);
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

  // Simple polling for updates (temporary replacement for WebSocket)
  useEffect(() => {
    const pollInterval = setInterval(() => {
      loadNews(); // Refresh news every 30 seconds
    }, 30000);

    return () => clearInterval(pollInterval);
  }, [loadNews]);

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

  // DEBUG: Log articles and pagination state
  useEffect(() => {
    console.log('[DEBUG] Articles:', articles.length);
  }, [articles]);


  return (
    <div className="feed-page">
      <ConnectionStatus />
      <NotificationManager />
      <SearchAndFilter
        availableSources={availableSources}
        totalArticles={articles.length}
        filteredCount={articles.length}
        onFilterChange={() => {}}
      />
      {isLoading('loading_feed') && articles.length === 0 ? (
        <div className="loading-container">
          <LoadingSpinner size="large" />
          <p>Loading news feed...</p>
        </div>
      ) : (
        <PullToRefresh onRefresh={loadNews}>
          <div className="articles-container">
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
              <div className="no-articles">No articles found.</div>
            )}
          </div>
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
