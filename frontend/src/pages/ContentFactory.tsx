import React, { useState, useEffect } from 'react';
import type { Article } from '../types';
import { api } from '../services/api';
import LoudHawkLogo from '../components/LoudHawkLogo';
import './ContentFactory.css';

interface SocialDraft {
  id: string;
  article_id: string;
  platform: string;
  hook: string;
  bullets: string;
  why: string;
  caption: string;
  x_post?: string;
  tiktok_script?: string;
  alt_text?: string;
  attribution: string;
  tags?: string;
  status: string;
  created_at: string;
  updated_at: string;
}

const ContentFactory: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'inbox' | 'drafts' | 'exports'>('inbox');
  const [inboxArticles, setInboxArticles] = useState<Article[]>([]);
  const [drafts, setDrafts] = useState<SocialDraft[]>([]);
  const [exports, setExports] = useState<SocialDraft[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedPlatform, setSelectedPlatform] = useState<string>('instagram');
  const [error, setError] = useState<string | null>(null);

  // Load data based on active tab
  useEffect(() => {
    console.log('ContentFactory: useEffect triggered, activeTab:', activeTab);
    loadTabData();
  }, [activeTab]);

  const loadTabData = async () => {
    console.log('ContentFactory: loadTabData called for tab:', activeTab);
    setLoading(true);
    setError(null);
    try {
      switch (activeTab) {
        case 'inbox':
          console.log('ContentFactory: Fetching inbox data...');
          const inboxData = await api.getInbox();
          console.log('ContentFactory: Inbox data received:', inboxData);
          setInboxArticles(inboxData.articles);
          break;
        case 'drafts':
          console.log('ContentFactory: Fetching drafts data...');
          const draftsData = await api.getDrafts();
          console.log('ContentFactory: Drafts data received:', draftsData);
          setDrafts(draftsData.drafts);
          break;
        case 'exports':
          console.log('ContentFactory: Fetching exports data...');
          const exportsData = await api.getExports();
          console.log('ContentFactory: Exports data received:', exportsData);
          setExports(exportsData.exports);
          break;
      }
    } catch (error) {
      console.error(`ContentFactory: Error loading ${activeTab}:`, error);
      setError(`Failed to load ${activeTab}: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectArticle = async (articleId: string) => {
    try {
      await api.selectArticle(articleId);
      loadTabData(); // Refresh inbox
    } catch (error) {
      console.error('Error selecting article:', error);
    }
  };

  const handleCreateDraft = async (articleId: string, platform: string) => {
    try {
      await api.createContentDraft(articleId, platform);
      loadTabData(); // Refresh drafts
    } catch (error) {
      console.error('Error creating draft:', error);
    }
  };

  const handleApproveDraft = async (draftId: string) => {
    try {
      await api.approveDraft(draftId);
      loadTabData(); // Refresh drafts
    } catch (error) {
      console.error('Error approving draft:', error);
    }
  };

  const handleExportDraft = async (draftId: string, platform: string) => {
    try {
      await api.exportDraft(draftId, platform);
      loadTabData(); // Refresh exports
    } catch (error) {
      console.error('Error exporting draft:', error);
    }
  };

  console.log('ContentFactory: Rendering component, activeTab:', activeTab, 'loading:', loading, 'error:', error);

  return (
    <div style={{ padding: '20px', background: 'white', minHeight: '100vh' }}>
      {/* Simple Test */}
      <h1 style={{ color: 'red', fontSize: '24px' }}>Content Factory Test Page</h1>
      <p>If you can see this, the component is rendering!</p>
      
      {/* Debug Info */}
      <div style={{ background: '#f0f0f0', padding: '10px', margin: '10px 0', border: '1px solid #ccc' }}>
        <strong>Debug Info:</strong> Tab: {activeTab}, Loading: {loading ? 'Yes' : 'No'}, 
        Articles: {inboxArticles.length}, Error: {error || 'None'}
      </div>
      
      {/* Header */}
      <div className="content-factory-header">
        <LoudHawkLogo size="large" variant="news" color="orange" />
        <h1>Loud Hawk Content Factory</h1>
        <p>Internal content production workflow</p>
      </div>

      {/* Tabs */}
      <div className="content-factory-tabs">
        <button 
          className={`content-factory-tab ${activeTab === 'inbox' ? 'active' : ''}`}
          onClick={() => setActiveTab('inbox')}
        >
          📥 Inbox <span className="badge">{inboxArticles.length}</span>
        </button>
        <button 
          className={`content-factory-tab ${activeTab === 'drafts' ? 'active' : ''}`}
          onClick={() => setActiveTab('drafts')}
        >
          ✏️ Drafts <span className="badge">{drafts.length}</span>
        </button>
        <button 
          className={`content-factory-tab ${activeTab === 'exports' ? 'active' : ''}`}
          onClick={() => setActiveTab('exports')}
        >
          📤 Exports <span className="badge">{exports.length}</span>
        </button>
      </div>

      {/* Content */}
      <div className="content-factory-tab-content">
        {error && (
          <div style={{ background: '#ffebee', color: '#c62828', padding: '10px', margin: '10px 0', border: '1px solid #f44336' }}>
            <strong>Error:</strong> {error}
          </div>
        )}
        {loading ? (
          <div className="content-factory-loading">
            <div className="content-factory-spinner"></div>
            Loading...
          </div>
        ) : (
          <>
            {activeTab === 'inbox' && (
              <InboxView 
                articles={inboxArticles}
                onSelectArticle={handleSelectArticle}
                onCreateDraft={handleCreateDraft}
                selectedPlatform={selectedPlatform}
                onPlatformChange={setSelectedPlatform}
              />
            )}
            {activeTab === 'drafts' && (
              <DraftsView 
                drafts={drafts}
                onApproveDraft={handleApproveDraft}
                onExportDraft={handleExportDraft}
              />
            )}
            {activeTab === 'exports' && (
              <ExportsView exports={exports} />
            )}
          </>
        )}
      </div>
    </div>
  );
};

// Inbox View Component
const InboxView: React.FC<{
  articles: Article[];
  onSelectArticle: (id: string) => void;
  onCreateDraft: (id: string, platform: string) => void;
  selectedPlatform: string;
  onPlatformChange: (platform: string) => void;
}> = ({ articles, onSelectArticle, onCreateDraft, selectedPlatform, onPlatformChange }) => (
  <div className="inbox-list">
    <div className="inbox-controls" style={{ marginBottom: 'var(--space-lg)' }}>
      <h2 style={{ color: 'var(--loud-black)', marginBottom: 'var(--space-md)' }}>New Articles</h2>
      <div className="platform-selector" style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)' }}>
        <label style={{ color: 'var(--loud-gray-dark)', fontWeight: '600' }}>Platform:</label>
        <select 
          value={selectedPlatform} 
          onChange={(e) => onPlatformChange(e.target.value)}
          style={{ 
            padding: 'var(--space-xs) var(--space-sm)', 
            border: '1px solid var(--loud-gray-light)', 
            borderRadius: '6px',
            backgroundColor: 'var(--loud-white)',
            color: 'var(--loud-black)'
          }}
        >
          <option value="instagram">Instagram</option>
          <option value="x">X (Twitter)</option>
          <option value="tiktok">TikTok</option>
        </select>
      </div>
    </div>
    
    {articles.length === 0 ? (
      <div className="content-factory-empty">
        <h3>No articles in inbox</h3>
        <p>Articles will appear here as they are ingested from news sources.</p>
      </div>
    ) : (
      articles.map((article) => (
        <div key={article.id} className="inbox-article">
          <div className="inbox-article-header">
            <h3 className="inbox-article-title">{article.title}</h3>
            <div className="inbox-article-meta">
              <span className="inbox-article-category">{article.category}</span>
              <span className="inbox-article-source">{article.source}</span>
              <span className="inbox-article-date">
                {new Date(article.published_at).toLocaleDateString()}
              </span>
            </div>
          </div>
          <p className="inbox-article-summary">{article.summary}</p>
          <div className="inbox-article-actions">
            <button 
              className="osa-btn osa-btn-secondary osa-btn-sm"
              onClick={() => onSelectArticle(article.id)}
            >
              Select
            </button>
            <button 
              className="osa-btn osa-btn-primary osa-btn-sm"
              onClick={() => onCreateDraft(article.id, selectedPlatform)}
            >
              Draft for {selectedPlatform.toUpperCase()}
            </button>
          </div>
        </div>
      ))
    )}
  </div>
);

// Drafts View Component
const DraftsView: React.FC<{
  drafts: SocialDraft[];
  onApproveDraft: (id: string) => void;
  onExportDraft: (id: string, platform: string) => void;
}> = ({ drafts, onApproveDraft, onExportDraft }) => (
  <div className="drafts-list">
    <h2 style={{ color: 'var(--loud-black)', marginBottom: 'var(--space-lg)' }}>Content Drafts</h2>
    
    {drafts.length === 0 ? (
      <div className="content-factory-empty">
        <h3>No drafts yet</h3>
        <p>Create drafts from articles in the inbox to see them here.</p>
      </div>
    ) : (
      drafts.map((draft) => (
        <div key={draft.id} className="draft-card">
          <div className="draft-header">
            <h3 className="draft-hook">{draft.hook}</h3>
            <div className="draft-meta">
              <span className="draft-platform">{draft.platform}</span>
              <span className={`draft-status ${draft.status}`}>{draft.status}</span>
            </div>
          </div>
          <div className="draft-bullets">
            <h4>Key Points:</h4>
            <ul>
              {JSON.parse(draft.bullets || '[]').map((bullet: string, index: number) => (
                <li key={index}>{bullet}</li>
              ))}
            </ul>
          </div>
          <div className="draft-why">
            <h4>Why it matters:</h4>
            <p>{draft.why}</p>
          </div>
          <p className="draft-caption">{draft.caption}</p>
          <div className="draft-actions">
            {draft.status === 'drafted' && (
              <button 
                className="osa-btn osa-btn-primary osa-btn-sm"
                onClick={() => onApproveDraft(draft.id)}
              >
                Approve
              </button>
            )}
            {draft.status === 'approved' && (
              <button 
                className="osa-btn osa-btn-accent osa-btn-sm"
                onClick={() => onExportDraft(draft.id, draft.platform)}
              >
                Export
              </button>
            )}
          </div>
        </div>
      ))
    )}
  </div>
);

// Exports View Component
const ExportsView: React.FC<{ exports: SocialDraft[] }> = ({ exports }) => (
  <div className="exports-list">
    <h2 style={{ color: 'var(--loud-black)', marginBottom: 'var(--space-lg)' }}>Exported Content</h2>
    
    {exports.length === 0 ? (
      <div className="content-factory-empty">
        <h3>No exports yet</h3>
        <p>Export approved drafts to see them here.</p>
      </div>
    ) : (
      exports.map((export_item) => (
        <div key={export_item.id} className="export-card">
          <div className="export-header">
            <h3 className="export-title">{export_item.hook}</h3>
            <div className="export-meta">
              <span className="export-platform">{export_item.platform}</span>
              <span className="export-status">{export_item.status}</span>
            </div>
          </div>
          <p className="export-caption">{export_item.caption}</p>
          {export_item.x_post && (
            <div style={{ 
              backgroundColor: 'var(--loud-cream)', 
              padding: 'var(--space-md)', 
              borderRadius: '8px', 
              marginBottom: 'var(--space-md)' 
            }}>
              <h4 style={{ color: 'var(--loud-black)', marginBottom: 'var(--space-sm)' }}>X Post:</h4>
              <p style={{ color: 'var(--loud-gray-dark)', margin: 0 }}>{export_item.x_post}</p>
            </div>
          )}
          {export_item.tiktok_script && (
            <div style={{ 
              backgroundColor: 'var(--loud-cream)', 
              padding: 'var(--space-md)', 
              borderRadius: '8px', 
              marginBottom: 'var(--space-md)' 
            }}>
              <h4 style={{ color: 'var(--loud-black)', marginBottom: 'var(--space-sm)' }}>TikTok Script:</h4>
              <p style={{ color: 'var(--loud-gray-dark)', margin: 0, whiteSpace: 'pre-line' }}>{export_item.tiktok_script}</p>
            </div>
          )}
          <div className="export-actions">
            <button 
              className="osa-btn osa-btn-secondary osa-btn-sm"
              onClick={() => navigator.clipboard.writeText(export_item.caption)}
            >
              Copy Caption
            </button>
            <button className="osa-btn osa-btn-primary osa-btn-sm">
              Download Assets
            </button>
          </div>
        </div>
      ))
    )}
  </div>
);

export default ContentFactory;

