import type { Article } from '../types';
import ReactMarkdown from 'react-markdown';
import LoadingSpinner from './LoadingSpinner';
import SwipeableCard from './SwipeableCard';
import ArticleStatusBadge from './ArticleStatusBadge';
import SourceBadge from './SourceBadge';

type ActionType = 'select' | 'edit' | 'export' | 'social-draft';

interface ArticleCardProps {
    article: Article;
    onAction: (action: ActionType, storyId: string) => void;
    isLoading: boolean;
}

const ArticleCard = ({ article, onAction, isLoading }: ArticleCardProps) => {
    const formattedDate = article.published_at
        ? new Date(article.published_at).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
        })
        : '';

    // Determine swipe actions based on article status
    const getSwipeActions = () => {
        if (isLoading) return { leftAction: undefined, rightAction: undefined };
        
        switch (article.status) {
            case 'new':
                return {
                    leftAction: { label: 'Select', color: '#f17500' },
                    rightAction: undefined
                };
            case 'selected':
                return {
                    leftAction: { label: 'Edit', color: '#0a4bb6' },
                    rightAction: undefined
                };
            case 'edited':
                return {
                    leftAction: { label: 'Re-edit', color: '#0a4bb6' },
                    rightAction: { label: 'Export', color: '#28a745' }
                };
            case 'exported':
                return {
                    leftAction: { label: 'Re-edit', color: '#6c757d' },
                    rightAction: undefined
                };
            default:
                return { leftAction: undefined, rightAction: undefined };
        }
    };

    const { leftAction, rightAction } = getSwipeActions();

    const handleSwipeLeft = () => {
        if (isLoading) return;
        switch (article.status) {
            case 'new':
                onAction('select', article.id);
                break;
            case 'selected':
                onAction('edit', article.id);
                break;
            case 'edited':
                onAction('edit', article.id);
                break;
            case 'posted':
                onAction('select', article.id);
                break;
        }
    };

    const handleSwipeRight = () => {
        if (isLoading || article.status !== 'edited') return;
        onAction('export', article.id);
    };

    return (
        <SwipeableCard
            onSwipeLeft={handleSwipeLeft}
            onSwipeRight={handleSwipeRight}
            leftAction={leftAction}
            rightAction={rightAction}
            disabled={isLoading}
        >
            <div className="osa-card" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                {/* OSA Card Header */}
                <div className="osa-card-header">
                    <div className="osa-flex-between osa-mb-2">
                        <ArticleStatusBadge status={article.status || 'new'} />
                        <div className="osa-caption">
                            {formattedDate}
                        </div>
                    </div>
                    <SourceBadge 
                        source={article.source} 
                        className="compact"
                    />
                </div>

                {/* OSA Card Content */}
                <div style={{ flex: 1, marginBottom: 'var(--space-lg)' }}>
                    <div className="osa-flex-between osa-mb-2">
                        <h3 className="osa-heading-4" style={{ 
                            display: '-webkit-box',
                            WebkitLineClamp: 3,
                            WebkitBoxOrient: 'vertical',
                            overflow: 'hidden',
                            lineHeight: '1.4',
                            flex: 1,
                            margin: 0
                        }}>
                            {article.title}
                        </h3>
                        {article.category && (
                            <span className="osa-badge" style={{
                                backgroundColor: 'var(--loud-orange)',
                                color: 'var(--loud-white)',
                                fontSize: '0.7rem',
                                padding: '2px 8px',
                                marginLeft: 'var(--space-sm)',
                                flexShrink: 0
                            }}>
                                {article.category}
                            </span>
                        )}
                    </div>
                    
                    {/* Markdown Preview */}
                    <div className="osa-body" style={{ 
                        display: '-webkit-box',
                        WebkitLineClamp: 4,
                        WebkitBoxOrient: 'vertical',
                        overflow: 'hidden',
                        color: 'var(--loud-black)'
                    }}>
                        <ReactMarkdown>
                            {article.body || article.summary || 'No content available'}
                        </ReactMarkdown>
                    </div>
                </div>

                {/* OSA Card Actions */}
                <div className="osa-flex-between" style={{ marginTop: 'auto' }}>
                    <a 
                        href={article.link} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="osa-btn osa-btn-ghost osa-btn-sm"
                        style={{ textDecoration: 'none' }}
                    >
                        🔗 Read More
                    </a>
                    
                    <div className="osa-flex" style={{ gap: 'var(--space-sm)' }}>
                        {/* Action Buttons */}
                        {article.status === 'new' && (
                            <button 
                                onClick={() => onAction('select', article.id)}
                                disabled={isLoading}
                                className="osa-btn osa-btn-primary osa-btn-sm"
                            >
                                {isLoading ? (
                                    <div className="osa-loading">
                                        <div className="osa-spinner"></div>
                                    </div>
                                ) : (
                                    'Select'
                                )}
                            </button>
                        )}
                        
                        {(article.status === 'selected' || article.status === 'edited') && (
                            <button
                                onClick={() => onAction('edit', article.id)}
                                disabled={isLoading}
                                className="osa-btn osa-btn-secondary osa-btn-sm"
                            >
                                {isLoading ? (
                                    <div className="osa-loading">
                                        <div className="osa-spinner"></div>
                                    </div>
                                ) : (
                                    'Edit'
                                )}
                            </button>
                        )}
                        
                        {article.status === 'edited' && (
                            <button 
                                onClick={() => onAction('export', article.id)} 
                                disabled={isLoading}
                                className="osa-btn osa-btn-primary osa-btn-sm"
                            >
                                {isLoading ? (
                                    <div className="osa-loading">
                                        <div className="osa-spinner"></div>
                                    </div>
                                ) : (
                                    'Export'
                                )}
                            </button>
                        )}
                        
                        {(article.status === 'new' || article.status === 'selected' || article.status === 'edited') && (
                            <button 
                                onClick={() => onAction('social-draft', article.id)} 
                                disabled={isLoading}
                                className="osa-btn osa-btn-accent osa-btn-sm"
                                style={{ backgroundColor: 'var(--loud-orange)', color: 'var(--loud-white)' }}
                            >
                                {isLoading ? (
                                    <div className="osa-loading">
                                        <div className="osa-spinner"></div>
                                    </div>
                                ) : (
                                    '📱 Social'
                                )}
                            </button>
                        )}
                        
                        {article.status === 'exported' && (
                            <button 
                                onClick={() => onAction('select', article.id)} 
                                disabled={isLoading}
                                className="osa-btn osa-btn-ghost osa-btn-sm"
                            >
                                {isLoading ? (
                                    <div className="osa-loading">
                                        <div className="osa-spinner"></div>
                                    </div>
                                ) : (
                                    'Re-select'
                                )}
                            </button>
                        )}
                    </div>
                </div>
            </div>
        </SwipeableCard>
    );
};

export default ArticleCard;
