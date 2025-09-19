import React, { useState, useEffect, useCallback } from 'react';
import type { Article, NewsResponse, Bookmark, SourceHealth } from '../types';
import { api } from '../services/api';

const NewsTerminal: React.FC = () => {
  const [articles, setArticles] = useState<Article[]>([]);
  const [sources, setSources] = useState<string[]>([]);
  const [selectedSource, setSelectedSource] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [lastIngest, setLastIngest] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [ingesting, setIngesting] = useState<boolean>(false);
  const [bookmarks, setBookmarks] = useState<Bookmark[]>([]);
  const [bookmarkedArticles, setBookmarkedArticles] = useState<Set<number>>(new Set());
  const [sourceHealth, setSourceHealth] = useState<SourceHealth[]>([]);

  // Load initial data
  useEffect(() => {
    loadArticles();
    loadSources();
    loadBookmarks();
    loadSourceHealth();
    // Set up auto-refresh every 5 minutes
    const interval = setInterval(() => {
      loadArticles();
      loadSources();
      loadBookmarks();
      loadSourceHealth();
    }, 5 * 60 * 1000);

    return () => clearInterval(interval);
  }, []);

  const loadArticles = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response: NewsResponse = await api.getNews({
        source: selectedSource || undefined,
        q: searchQuery || undefined,
        limit: 100
      });
      setArticles(response.articles);
    } catch (error) {
      console.error('Error loading articles:', error);
      setError('Failed to load articles. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [selectedSource, searchQuery]);

  const loadSources = async () => {
    try {
      const response = await api.getSources();
      setSources(response.sources);
    } catch (error) {
      console.error('Error loading sources:', error);
      setError('Failed to load sources.');
    }
  };

  const loadBookmarks = async () => {
    try {
      const response = await api.getBookmarks();
      setBookmarks(response.bookmarks);
      // Update the set of bookmarked article IDs for quick lookup
      const bookmarkedIds = new Set(response.bookmarks.map(b => b.article_id));
      setBookmarkedArticles(bookmarkedIds);
    } catch (error) {
      console.error('Error loading bookmarks:', error);
    }
  };

  const loadSourceHealth = async () => {
    try {
      const response = await api.getSourceHealth();
      setSourceHealth(response.sources);
    } catch (error) {
      console.error('Error loading source health:', error);
    }
  };

  const toggleBookmark = async (articleId: number) => {
    try {
      const isBookmarked = bookmarkedArticles.has(articleId);
      
      if (isBookmarked) {
        await api.removeBookmark(articleId);
        setBookmarkedArticles(prev => {
          const newSet = new Set(prev);
          newSet.delete(articleId);
          return newSet;
        });
        setBookmarks(prev => prev.filter(b => b.article_id !== articleId));
      } else {
        await api.addBookmark(articleId);
        setBookmarkedArticles(prev => new Set([...prev, articleId]));
        // Reload bookmarks to get the full bookmark data
        await loadBookmarks();
      }
    } catch (error) {
      console.error('Error toggling bookmark:', error);
      setError('Failed to update bookmark.');
    }
  };

  // Effect to reload articles when source or search query changes
  useEffect(() => {
    loadArticles();
  }, [selectedSource, searchQuery, loadArticles]);

  const handleIngest = async () => {
    try {
      setIngesting(true);
      setError(null);
      await api.ingestNews();
      setLastIngest(new Date().toLocaleTimeString());
      await loadArticles();
    } catch (error) {
      console.error('Error ingesting news:', error);
      setError('Failed to sync news. Please check your connection.');
    } finally {
      setIngesting(false);
    }
  };

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));

    if (diffInMinutes < 1) return 'just now';
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    if (diffInMinutes < 24 * 60) return `${Math.floor(diffInMinutes / 60)}h ago`;
    return date.toLocaleDateString();
  };

  const getSourceHealthStatus = (sourceName: string) => {
    const health = sourceHealth.find(s => s.name === sourceName);
    if (!health) return { status: 'unknown', color: 'gray', tooltip: 'No health data available' };
    
    if (!health.enabled) {
      return { 
        status: 'disabled', 
        color: 'red', 
        tooltip: `Disabled: ${health.disabled_reason || 'Unknown reason'}` 
      };
    }
    
    if (health.error_streak >= 3) {
      return { 
        status: 'failed', 
        color: 'red', 
        tooltip: `Failed last ${health.error_streak} fetches. Last error: ${health.last_error || 'Unknown'}` 
      };
    }
    
    if (health.reliability_score >= 0.9) {
      return { 
        status: 'excellent', 
        color: 'green', 
        tooltip: `Excellent reliability (${Math.round(health.reliability_score * 100)}%). Last updated: ${health.last_ok_at ? formatTimeAgo(health.last_ok_at) : 'Never'}` 
      };
    }
    
    if (health.reliability_score >= 0.7) {
      return { 
        status: 'good', 
        color: 'yellow', 
        tooltip: `Good reliability (${Math.round(health.reliability_score * 100)}%). Last updated: ${health.last_ok_at ? formatTimeAgo(health.last_ok_at) : 'Never'}` 
      };
    }
    
    return { 
      status: 'poor', 
      color: 'red', 
      tooltip: `Poor reliability (${Math.round(health.reliability_score * 100)}%). Last updated: ${health.last_ok_at ? formatTimeAgo(health.last_ok_at) : 'Never'}` 
    };
  };


  return (
    <div className="terminal-layout">
      {/* Header */}
      <div className="terminal-header">
        <div className="logo">
          <div className="logo-text">
            <div className="logo-loud">LOUD</div>
            <div className="logo-hawk">HAWK</div>
          </div>
        </div>
        
        <div className="search-bar">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            placeholder="Search aviation news..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
        </div>
        
        <div className="header-actions">
          <button 
            onClick={handleIngest}
            className="sync-button"
            disabled={ingesting || loading}
          >
            {ingesting ? 'Syncing...' : 'Sync'}
          </button>
          {lastIngest && (
            <span className="last-sync">Last: {lastIngest}</span>
          )}
        </div>
      </div>

      {/* Left Sidebar - Sources */}
      <div className="sidebar">
        <div className="sidebar-section">
          <h3 className="section-title">Sources</h3>
          <div className="source-list">
            <div 
              className={`source-item ${selectedSource === null ? 'active' : ''}`}
              onClick={() => setSelectedSource(null)}
            >
              <div className="source-info">
                <span className="source-name">All Sources</span>
                <span className="source-count">{articles.length}</span>
              </div>
              <div className="reliability-dot reliability-green"></div>
            </div>
            {sources.map(source => {
              const healthStatus = getSourceHealthStatus(source);
              const health = sourceHealth.find(s => s.name === source);
              const isDisabled = healthStatus.status === 'disabled' || healthStatus.status === 'failed';
              
              return (
                <div 
                  key={source} 
                  className={`source-item ${selectedSource === source ? 'active' : ''} ${isDisabled ? 'disabled' : ''}`}
                  onClick={() => !isDisabled && setSelectedSource(source)}
                  title={healthStatus.tooltip}
                >
                  <div className="source-info">
                    <span className="source-name">{source}</span>
                    <div className="source-meta">
                      <span className="source-count">
                        {articles.filter(a => a.source === source).length}
                      </span>
                      {health?.last_ok_at && (
                        <span className="source-timestamp">
                          {formatTimeAgo(health.last_ok_at)}
                        </span>
                      )}
                    </div>
                  </div>
                  <div className={`reliability-dot reliability-${healthStatus.color}`}></div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Main Content - News Feed */}
      <div className="main-content">
        {error && (
          <div className="error-message">
            <div className="error-icon">⚠️</div>
            <div className="error-text">{error}</div>
            <button 
              onClick={() => {
                setError(null);
                loadArticles();
              }}
              className="retry-button"
            >
              Retry
            </button>
          </div>
        )}
        
        {loading ? (
          <div className="loading">
            <div className="loading-spinner"></div>
            Loading aviation news...
          </div>
        ) : articles.length === 0 ? (
            <div className="loading">
              No articles found. Try syncing news or adjusting filters.
            </div>
          ) : (
            <div className="news-feed">
              {articles.map(article => (
                <div 
                  key={article.id} 
                  className="article-card"
                >
                  <div className="article-header">
                    <div className="article-meta">
                      <span className="source-badge">{article.source}</span>
                      <span className="article-time">{formatTimeAgo(article.published_at.toString())}</span>
                    </div>
                  </div>
                  <div className="article-title-row">
                    <h3 className="article-title">{article.title}</h3>
                    <button
                      className={`bookmark-button ${bookmarkedArticles.has(Number(article.id)) ? 'bookmarked' : ''}`}
                      onClick={() => toggleBookmark(Number(article.id))}
                      title={bookmarkedArticles.has(Number(article.id)) ? 'Remove from bookmarks' : 'Add to bookmarks'}
                    >
                      ⭐
                    </button>
                  </div>
                  {article.summary && <p className="article-summary">{article.summary}</p>}
                  <a 
                    href={article.url} 
                    target="_blank" 
                    rel="noopener noreferrer" 
                    className="article-link"
                  >
                    Read Full Article →
                  </a>
                </div>
              ))}
            </div>
          )}
      </div>

      {/* Right Panel - Tools */}
      <div className="right-panel">
        <div className="panel-section">
          <h3 className="section-title">Bookmarks</h3>
          <div className="bookmarks-list">
            {bookmarks.length === 0 ? (
              <p className="empty-state">No bookmarks yet</p>
            ) : (
              bookmarks.slice(0, 5).map(bookmark => (
                <div key={bookmark.id} className="bookmark-item">
                  <div className="bookmark-source">{bookmark.article_source}</div>
                  <div className="bookmark-title">{bookmark.article_title}</div>
                  <div className="bookmark-meta">
                    {formatTimeAgo(bookmark.article_published_at)}
                    <a 
                      href={bookmark.article_url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="bookmark-link"
                    >
                      Read →
                    </a>
                  </div>
                </div>
              ))
            )}
            {bookmarks.length > 5 && (
              <div className="bookmark-more">
                +{bookmarks.length - 5} more bookmarks
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
};

export default NewsTerminal;