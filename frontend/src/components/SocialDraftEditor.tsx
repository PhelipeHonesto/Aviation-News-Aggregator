import React, { useState, useEffect } from 'react';
import { createSocialDraft, getSocialDraft, updateSocialDraft, approveSocialDraft, markSocialDraftPosted, type SocialDraft, type SocialDraftUpdate } from '../services/api';
import type { Article } from '../types';

interface SocialDraftEditorProps {
  article: Article;
  onClose: () => void;
  onStatusChange: (status: string) => void;
}

const SocialDraftEditor: React.FC<SocialDraftEditorProps> = ({ article, onClose, onStatusChange }) => {
  const [draft, setDraft] = useState<SocialDraft | null>(null);
  const [loading, setLoading] = useState(false);
  const [editing, setEditing] = useState(false);
  const [editedDraft, setEditedDraft] = useState<SocialDraftUpdate>({});
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDraft();
  }, [article.id]);

  const loadDraft = async () => {
    try {
      setLoading(true);
      const existingDraft = await getSocialDraft(article.id);
      setDraft(existingDraft);
    } catch (err) {
      // Draft doesn't exist yet, that's okay
      setDraft(null);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateDraft = async () => {
    try {
      setLoading(true);
      setError(null);
      const newDraft = await createSocialDraft(article.id, {
        tone: 'LoudHawk-NewsBomb',
        max_bullets: 5
      });
      setDraft(newDraft);
      onStatusChange('drafted');
    } catch (err: any) {
      setError(err.message || 'Failed to create social draft');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = () => {
    if (draft) {
      setEditedDraft({
        hook: draft.hook,
        bullets: draft.bullets,
        why: draft.why,
        caption: draft.caption,
        alt_text: draft.alt_text,
        tags: draft.tags,
        attribution: draft.attribution
      });
      setEditing(true);
    }
  };

  const handleSave = async () => {
    if (!draft) return;
    
    try {
      setLoading(true);
      setError(null);
      const updatedDraft = await updateSocialDraft(draft.id, editedDraft);
      setDraft(updatedDraft);
      setEditing(false);
    } catch (err: any) {
      setError(err.message || 'Failed to update social draft');
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async () => {
    if (!draft) return;
    
    try {
      setLoading(true);
      setError(null);
      await approveSocialDraft(draft.id);
      onStatusChange('approved');
      setDraft({ ...draft, status: 'approved' });
    } catch (err: any) {
      setError(err.message || 'Failed to approve social draft');
    } finally {
      setLoading(false);
    }
  };

  const handleMarkPosted = async () => {
    if (!draft) return;
    
    try {
      setLoading(true);
      setError(null);
      await markSocialDraftPosted(draft.id);
      onStatusChange('posted');
      setDraft({ ...draft, status: 'posted' });
    } catch (err: any) {
      setError(err.message || 'Failed to mark as posted');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  if (loading && !draft) {
    return (
      <div className="osa-modal-overlay">
        <div className="osa-modal">
          <div className="osa-modal-header">
            <h2>Social Media Draft</h2>
            <button onClick={onClose} className="osa-btn-close">×</button>
          </div>
          <div className="osa-modal-body">
            <div className="osa-loading">Creating social draft...</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="osa-modal-overlay">
      <div className="osa-modal social-draft-modal">
        <div className="osa-modal-header">
          <h2>Social Media Draft</h2>
          <button onClick={onClose} className="osa-btn-close">×</button>
        </div>
        <div className="osa-modal-body">
          {error && (
            <div className="osa-error-message">
              {error}
            </div>
          )}

          {!draft ? (
            <div className="osa-draft-creation">
              <h3>Create Social Media Draft</h3>
              <p>Generate an Instagram-ready "News Bomb" from this article using AI.</p>
              <div className="osa-article-preview">
                <h4>{article.title}</h4>
                <p className="osa-source">{article.source}</p>
                <p className="osa-category">{article.category}</p>
              </div>
              <button 
                onClick={handleCreateDraft} 
                disabled={loading}
                className="osa-btn osa-btn-primary"
              >
                {loading ? 'Creating...' : 'Create Draft'}
              </button>
            </div>
          ) : (
            <div className="osa-draft-content">
              <div className="osa-draft-header">
                <h3>Draft Status: <span className={`osa-status-${draft.status}`}>{draft.status}</span></h3>
                <div className="osa-draft-actions">
                  {draft.status === 'drafted' && (
                    <>
                      <button onClick={handleEdit} className="osa-btn osa-btn-secondary">
                        Edit
                      </button>
                      <button onClick={handleApprove} disabled={loading} className="osa-btn osa-btn-primary">
                        Approve
                      </button>
                    </>
                  )}
                  {draft.status === 'approved' && (
                    <button onClick={handleMarkPosted} disabled={loading} className="osa-btn osa-btn-success">
                      Mark as Posted
                    </button>
                  )}
                </div>
              </div>

              {editing ? (
                <div className="osa-draft-editor">
                  <div className="osa-form-group">
                    <label>Hook (≤90 chars)</label>
                    <input
                      type="text"
                      value={editedDraft.hook || ''}
                      onChange={(e) => setEditedDraft({ ...editedDraft, hook: e.target.value })}
                      maxLength={90}
                      className="osa-input"
                    />
                    <small>{editedDraft.hook?.length || 0}/90 characters</small>
                  </div>

                  <div className="osa-form-group">
                    <label>Bullets</label>
                    {editedDraft.bullets?.map((bullet, index) => (
                      <input
                        key={index}
                        type="text"
                        value={bullet}
                        onChange={(e) => {
                          const newBullets = [...(editedDraft.bullets || [])];
                          newBullets[index] = e.target.value;
                          setEditedDraft({ ...editedDraft, bullets: newBullets });
                        }}
                        className="osa-input"
                        placeholder={`Bullet ${index + 1}`}
                      />
                    ))}
                  </div>

                  <div className="osa-form-group">
                    <label>Why it matters</label>
                    <textarea
                      value={editedDraft.why || ''}
                      onChange={(e) => setEditedDraft({ ...editedDraft, why: e.target.value })}
                      className="osa-textarea"
                      rows={3}
                    />
                  </div>

                  <div className="osa-form-group">
                    <label>Caption</label>
                    <textarea
                      value={editedDraft.caption || ''}
                      onChange={(e) => setEditedDraft({ ...editedDraft, caption: e.target.value })}
                      className="osa-textarea"
                      rows={6}
                    />
                  </div>

                  <div className="osa-form-group">
                    <label>Alt Text</label>
                    <textarea
                      value={editedDraft.alt_text || ''}
                      onChange={(e) => setEditedDraft({ ...editedDraft, alt_text: e.target.value })}
                      className="osa-textarea"
                      rows={2}
                    />
                  </div>

                  <div className="osa-form-actions">
                    <button onClick={() => setEditing(false)} className="osa-btn osa-btn-secondary">
                      Cancel
                    </button>
                    <button onClick={handleSave} disabled={loading} className="osa-btn osa-btn-primary">
                      {loading ? 'Saving...' : 'Save Changes'}
                    </button>
                  </div>
                </div>
              ) : (
                <div className="osa-draft-display">
                  <div className="osa-draft-section">
                    <h4>Hook</h4>
                    <p className="osa-hook">{draft.hook}</p>
                  </div>

                  <div className="osa-draft-section">
                    <h4>Bullets</h4>
                    <ul className="osa-bullets">
                      {draft.bullets.map((bullet, index) => (
                        <li key={index}>{bullet}</li>
                      ))}
                    </ul>
                  </div>

                  <div className="osa-draft-section">
                    <h4>Why it matters</h4>
                    <p>{draft.why}</p>
                  </div>

                  <div className="osa-draft-section">
                    <h4>Caption</h4>
                    <div className="osa-caption-container">
                      <pre className="osa-caption">{draft.caption}</pre>
                      <button 
                        onClick={() => copyToClipboard(draft.caption)}
                        className="osa-btn osa-btn-small"
                      >
                        Copy
                      </button>
                    </div>
                  </div>

                  <div className="osa-draft-section">
                    <h4>Alt Text</h4>
                    <p className="osa-alt-text">{draft.alt_text}</p>
                  </div>

                  <div className="osa-draft-section">
                    <h4>Attribution</h4>
                    <p className="osa-attribution">{draft.attribution}</p>
                  </div>

                  <div className="osa-draft-section">
                    <h4>Tags</h4>
                    <div className="osa-tags">
                      {draft.tags.map((tag, index) => (
                        <span key={index} className="osa-tag">{tag}</span>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SocialDraftEditor;
