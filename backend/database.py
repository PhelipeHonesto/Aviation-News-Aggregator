"""
Loud Hawk v2 - Database Operations
Simple, focused database operations for news aggregation
"""
import os
from sqlmodel import SQLModel, create_engine, Session
from models import NewsArticle, Bookmark
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./loudhawk.db")
engine = create_engine(DATABASE_URL, echo=False)

def init_db():
    """Initialize database tables"""
    try:
        SQLModel.metadata.create_all(engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

def get_session():
    """Get database session"""
    return Session(engine)

def save_articles(articles: List[NewsArticle]):
    """Save articles to database with deduplication"""
    with get_session() as session:
        saved_count = 0
        duplicate_count = 0
        
        for article in articles:
            try:
                # Check if article already exists
                existing = session.query(NewsArticle).filter(
                    NewsArticle.content_hash == article.content_hash
                ).first()
                
                if existing:
                    duplicate_count += 1
                    continue
                
                session.add(article)
                saved_count += 1
                
            except Exception as e:
                logger.error(f"Error saving article {article.title}: {e}")
                continue
        
        session.commit()
        logger.info(f"Saved {saved_count} new articles, {duplicate_count} duplicates skipped")
        return saved_count

def get_articles(
    source: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> List[NewsArticle]:
    """Get articles with optional filtering"""
    with get_session() as session:
        query = session.query(NewsArticle)
        
        if source:
            query = query.filter(NewsArticle.source == source)
        if category:
            query = query.filter(NewsArticle.category == category)
        
        return query.order_by(
            NewsArticle.published_at.desc()
        ).offset(offset).limit(limit).all()

def search_articles(query: str, limit: int = 50) -> List[NewsArticle]:
    """Search articles by title and summary"""
    with get_session() as session:
        search_term = f"%{query.lower()}%"
        
        return session.query(NewsArticle).filter(
            NewsArticle.title.ilike(search_term) |
            NewsArticle.summary.ilike(search_term)
        ).order_by(
            NewsArticle.published_at.desc()
        ).limit(limit).all()

def get_sources() -> List[str]:
    """Get all unique sources"""
    with get_session() as session:
        return [row[0] for row in session.query(NewsArticle.source).distinct().all()]

# Bookmark functions
def add_bookmark(article_id: int, user_id: str = "default") -> bool:
    """Add an article to bookmarks"""
    with get_session() as session:
        try:
            # Check if already bookmarked
            existing = session.query(Bookmark).filter(
                Bookmark.article_id == article_id,
                Bookmark.user_id == user_id
            ).first()
            
            if existing:
                return False  # Already bookmarked
            
            # Get article details
            article = session.query(NewsArticle).filter(NewsArticle.id == article_id).first()
            if not article:
                return False
            
            # Create bookmark
            bookmark = Bookmark(
                article_id=article_id,
                user_id=user_id,
                article_title=article.title,
                article_source=article.source,
                article_url=article.url,
                article_published_at=article.published_at,
                article_summary=article.summary,
                article_category=article.category
            )
            
            session.add(bookmark)
            session.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error adding bookmark: {e}")
            return False

def remove_bookmark(article_id: int, user_id: str = "default") -> bool:
    """Remove an article from bookmarks"""
    with get_session() as session:
        try:
            bookmark = session.query(Bookmark).filter(
                Bookmark.article_id == article_id,
                Bookmark.user_id == user_id
            ).first()
            
            if bookmark:
                session.delete(bookmark)
                session.commit()
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error removing bookmark: {e}")
            return False

def get_bookmarks(user_id: str = "default", limit: int = 50) -> List[Bookmark]:
    """Get user's bookmarks"""
    with get_session() as session:
        return session.query(Bookmark).filter(
            Bookmark.user_id == user_id
        ).order_by(
            Bookmark.created_at.desc()
        ).limit(limit).all()

def is_bookmarked(article_id: int, user_id: str = "default") -> bool:
    """Check if article is bookmarked"""
    with get_session() as session:
        bookmark = session.query(Bookmark).filter(
            Bookmark.article_id == article_id,
            Bookmark.user_id == user_id
        ).first()
        return bookmark is not None