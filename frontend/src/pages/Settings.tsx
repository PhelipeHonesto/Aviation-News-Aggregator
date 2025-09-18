import React, { useState, useEffect } from 'react';
import LoadingSpinner from '../components/LoadingSpinner';
import Toast from '../components/Toast';
import * as api from '../services/api';

interface Stats {
  total_articles: number;
  status_breakdown: Record<string, number>;
  source_breakdown: Record<string, number>;
  last_updated: string;
}

const Settings = () => {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState<{
    message: string;
    type: 'success' | 'error' | 'info';
    isVisible: boolean;
  }>({
    message: '',
    type: 'info',
    isVisible: false
  });

  const showToast = (message: string, type: 'success' | 'error' | 'info') => {
    setToast({ message, type, isVisible: true });
  };

  const hideToast = () => {
    setToast(prev => ({ ...prev, isVisible: false }));
  };

  const loadStats = async () => {
    try {
      setLoading(true);
      const data: Stats = await api.getStats();
      setStats(data);
    } catch (error) {
      console.error('Error loading stats:', error);
      showToast('Failed to load statistics', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleIngestNews = async () => {
    try {
      showToast('Ingesting news...', 'info');
      await api.ingestNews();
      showToast('News ingestion completed successfully!', 'success');
      loadStats(); // Refresh stats
    } catch (error) {
      console.error('Error ingesting news:', error);
      showToast('Failed to ingest news', 'error');
    }
  };

  useEffect(() => {
    loadStats();
  }, []);

  if (loading) {
    return (
      <div className="settings-page">
        <div className="loading-container">
          <LoadingSpinner size="large" />
          <p>Loading settings...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="osa-container">
      <div className="osa-section" style={{ paddingTop: 'var(--space-2xl)' }}>
        {/* OSA Header */}
        <div className="osa-flex-between osa-mb-4">
          <div>
            <h1 className="osa-heading-1">Settings & Analytics</h1>
            <p className="osa-body-large" style={{ color: 'var(--osa-medium-gray)' }}>
              Monitor your news curation performance and configure preferences
            </p>
          </div>
          <button 
            onClick={handleIngestNews}
            className="osa-btn osa-btn-primary osa-btn-lg"
          >
            🔄 Ingest News
          </button>
        </div>

        {/* Statistics Cards */}
        {stats && (
          <div className="osa-grid osa-grid-3 osa-mb-4">
            <div className="osa-card osa-text-center">
              <div className="osa-card-header">
                <h3 className="osa-card-title">Total Articles</h3>
              </div>
              <div className="osa-heading-2" style={{ color: 'var(--osa-orange)' }}>
                {stats.total_articles}
              </div>
            </div>
            
            <div className="osa-card">
              <div className="osa-card-header">
                <h3 className="osa-card-title">Status Breakdown</h3>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
                {Object.entries(stats.status_breakdown).map(([status, count]) => (
                  <div key={status} className="osa-flex-between">
                    <span className="osa-body-small" style={{ textTransform: 'capitalize' }}>
                      {status}
                    </span>
                    <span className="osa-badge osa-badge-new" style={{ 
                      background: 'var(--osa-orange)', 
                      color: 'white',
                      border: 'none'
                    }}>
                      {count}
                    </span>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="osa-card">
              <div className="osa-card-header">
                <h3 className="osa-card-title">Top Sources</h3>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
                {Object.entries(stats.source_breakdown)
                  .sort(([,a], [,b]) => b - a)
                  .slice(0, 5)
                  .map(([source, count]) => (
                    <div key={source} className="osa-flex-between">
                      <span className="osa-body-small" style={{ 
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                        maxWidth: '150px'
                      }}>
                        {source}
                      </span>
                      <span className="osa-badge osa-badge-new" style={{ 
                        background: 'var(--osa-blue)', 
                        color: 'white',
                        border: 'none'
                      }}>
                        {count}
                      </span>
                    </div>
                  ))}
              </div>
            </div>
          </div>
        )}

        {/* Application Settings */}
        <div className="osa-card">
          <div className="osa-card-header">
            <h3 className="osa-card-title">Application Settings</h3>
            <p className="osa-card-subtitle">Configure your news curation preferences</p>
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-lg)' }}>
            <div className="osa-flex-between" style={{ alignItems: 'center' }}>
              <label className="osa-body" style={{ fontWeight: '500' }}>
                Auto-refresh interval
              </label>
              <select 
                defaultValue="60"
                style={{ minWidth: '150px' }}
              >
                <option value="30">30 seconds</option>
                <option value="60">1 minute</option>
                <option value="300">5 minutes</option>
                <option value="600">10 minutes</option>
              </select>
            </div>
            
            <div className="osa-flex-between" style={{ alignItems: 'center' }}>
              <label className="osa-body" style={{ fontWeight: '500' }}>
                Default article status
              </label>
              <select 
                defaultValue="new"
                style={{ minWidth: '150px' }}
              >
                <option value="new">New</option>
                <option value="selected">Selected</option>
                <option value="edited">Edited</option>
              </select>
            </div>
          </div>
        </div>

        {/* Last Updated */}
        {stats && (
          <div className="osa-text-center osa-mt-4">
            <p className="osa-caption">
              Last updated: {new Date(stats.last_updated).toLocaleString()}
            </p>
          </div>
        )}
      </div>

      <Toast
        message={toast.message}
        type={toast.type}
        isVisible={toast.isVisible}
        onClose={hideToast}
      />
    </div>
  );
};

export default Settings;
