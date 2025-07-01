import { useEffect, useState, useCallback } from 'react';
import ArticleCard from '../components/ArticleCard';
import Toast from '../components/Toast';
import LoadingSpinner from '../components/LoadingSpinner';
import * as api from '../services/api';
import type { Article } from '../types';
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

  const loadNews = useCallback(() => {
    setActingArticleId('loading_feed');
    api.getNews()
      .then(setArticles)
      .catch((err) => {
        if (err instanceof Error && err.message.includes('Failed to fetch')) {
          showToast('Could not connect to the backend. Please ensure the server is running and try again.', 'error');
        } else {
          showToast('Could not load news. Please try again later.', 'error');
        }
      })
      .finally(() => setActingArticleId(null));
  }, []);

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
      const response = await api.ingestNews();
      showToast(response.message, 'success');
      loadNews(); // Refresh the feed
    } catch (err: any) {
      const errorMessage = err.message || 'An unknown error occurred during ingestion.';
      if (errorMessage.includes('Failed to fetch')) {
        showToast('Could not connect to the backend. Please ensure the server is running and try again.', 'error');
      } else {
        showToast(errorMessage, 'error');
      }
    } finally {
      setActingArticleId(null);
    }
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
      
      const response = await currentAction.apiCall(storyId);
      showToast(response.message, 'success');

      // After a successful action, reload all news to reflect the change.
      loadNews();
    } catch (err: any) {
      const errorMessage = err.message || `An unknown error occurred while performing action: ${action}.`;
      if (errorMessage.includes('Failed to fetch')) {
        showToast('Could not connect to the backend. Please ensure the server is running and try again.', 'error');
      } else {
        showToast(errorMessage, 'error');
      }
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
      
      {/* Display a loading message or the list of articles */}
      {isLoading('loading_feed') && articles.length === 0 ? (
        <div className="loading-container">
          <LoadingSpinner size="large" />
          <p>Loading news feed...</p>
        </div>
      ) : (
        <div className="articles-container">
          {articles.map(article => (
            <ArticleCard 
              key={article.id} 
              article={article} 
              onAction={handleAction}
              isLoading={isLoading(article.id)}
            />
          ))}
        </div>
      )}

      {/* Toast notifications */}
      <Toast
        message={toast.message}
        type={toast.type}
        isVisible={toast.isVisible}
        onClose={hideToast}
      />
    </div>
  );
};

export default Feed;
