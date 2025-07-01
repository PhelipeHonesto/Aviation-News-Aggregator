import type { Article } from '../types';
import LoadingSpinner from './LoadingSpinner';
import SwipeableCard from './SwipeableCard';

type ActionType = 'select' | 'edit' | 'post';

interface ArticleCardProps {
    article: Article;
    onAction: (action: ActionType, storyId: string) => void;
    isLoading: boolean;
}

const ArticleCard = ({ article, onAction, isLoading }: ArticleCardProps) => {
    const getStatusTag = (status: string) => {
        switch (status) {
            case 'selected':
                return { text: 'SELECTED', color: '#f17500' };
            case 'edited':
                return { text: 'EDITED', color: '#0a4bb6' };
            case 'posted':
                return { text: 'POSTED', color: '#28a745' };
            default:
                return { text: 'NEW', color: '#6c757d' };
        }
    };

    const statusTag = getStatusTag(article.status);
    const formattedDate = new Date(article.date).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
    });

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
                    rightAction: { label: 'Post', color: '#28a745' }
                };
            case 'posted':
                return {
                    leftAction: { label: 'Rewrite', color: '#6c757d' },
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
        onAction('post', article.id);
    };

    return (
        <SwipeableCard
            onSwipeLeft={handleSwipeLeft}
            onSwipeRight={handleSwipeRight}
            leftAction={leftAction}
            rightAction={rightAction}
            disabled={isLoading}
        >
            <div className="article-card">
                {/* Top Section */}
                <div className="card-top">
                    <div className="tag-chip" style={{ backgroundColor: statusTag.color }}>
                        {statusTag.text}
                    </div>
                    <div className="date-source">
                        <span className="date">{formattedDate}</span>
                        <span className="source">{article.source}</span>
                    </div>
                </div>

                {/* Middle Section */}
                <div className="card-middle">
                    <h2 className="article-title">{article.title}</h2>
                    <p className="article-summary">
                        {article.body
                            ? (article.body.length > 200 ? `${article.body.substring(0, 200)}...` : article.body)
                            : 'No summary available.'
                        }
                    </p>
                </div>

                {/* Bottom Section */}
                <div className="card-bottom">
                    <div className="card-actions">
                        <a 
                            href={article.link} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="read-more-btn"
                        >
                            🔗 Read More
                        </a>
                        
                        <div className="action-buttons">
                            {article.status === 'new' && (
                                <button 
                                    onClick={() => onAction('select', article.id)}
                                    disabled={isLoading}
                                    className={`action-btn select-btn ${isLoading ? 'loading' : ''}`}
                                >
                                    {isLoading ? (
                                        <>
                                            <LoadingSpinner size="small" color="white" />
                                            <span style={{ marginLeft: '8px' }}>Selecting...</span>
                                        </>
                                    ) : (
                                        'Select Story'
                                    )}
                                </button>
                            )}
                            {article.status === 'selected' && (
                                <button 
                                    onClick={() => onAction('edit', article.id)} 
                                    disabled={isLoading}
                                    className={`action-btn edit-btn ${isLoading ? 'loading' : ''}`}
                                >
                                    {isLoading ? (
                                        <>
                                            <LoadingSpinner size="small" color="white" />
                                            <span style={{ marginLeft: '8px' }}>Editing...</span>
                                        </>
                                    ) : (
                                        'Edit with AI'
                                    )}
                                </button>
                            )}
                            {article.status === 'edited' && (
                                <>
                                    <button 
                                        onClick={() => onAction('edit', article.id)} 
                                        disabled={isLoading}
                                        className={`action-btn reedit-btn ${isLoading ? 'loading' : ''}`}
                                    >
                                        {isLoading ? (
                                            <>
                                                <LoadingSpinner size="small" color="white" />
                                                <span style={{ marginLeft: '8px' }}>Editing...</span>
                                            </>
                                        ) : (
                                            'Re-edit'
                                        )}
                                    </button>
                                    <button 
                                        onClick={() => onAction('post', article.id)} 
                                        disabled={isLoading}
                                        className={`action-btn post-btn ${isLoading ? 'loading' : ''}`}
                                    >
                                        {isLoading ? (
                                            <>
                                                <LoadingSpinner size="small" color="white" />
                                                <span style={{ marginLeft: '8px' }}>Posting...</span>
                                            </>
                                        ) : (
                                            'Post to Slack'
                                        )}
                                    </button>
                                </>
                            )}
                            {article.status === 'posted' && (
                                <button 
                                    onClick={() => onAction('select', article.id)} 
                                    disabled={isLoading}
                                    className={`action-btn rewrite-btn ${isLoading ? 'loading' : ''}`}
                                >
                                    {isLoading ? (
                                        <>
                                            <LoadingSpinner size="small" color="white" />
                                            <span style={{ marginLeft: '8px' }}>Rewriting...</span>
                                        </>
                                    ) : (
                                        'Rewrite Story'
                                    )}
                                </button>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </SwipeableCard>
    );
};

export default ArticleCard;
