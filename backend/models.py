from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
import hashlib


class NewsArticle(SQLModel, table=True):
    """Simple news article model for RSS aggregation"""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    source: str = Field(index=True)  # "FAA", "NTSB", "Airbus", etc.
    title: str = Field(index=True)
    url: str = Field(unique=True, index=True)
    published_at: datetime = Field(index=True)
    summary: Optional[str] = None
    category: Optional[str] = Field(index=True)  # "Safety", "Airlines", "OEMs", "Regulation"
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    
    # For deduplication
    content_hash: str = Field(index=True)
    
    @classmethod
    def create_hash(cls, title: str, source: str, published_at: datetime) -> str:
        """Create content hash for deduplication"""
        content = f"{title.lower()}|{source.lower()}|{published_at.date()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


class Bookmark(SQLModel, table=True):
    """Bookmarks for saved articles"""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    article_id: int = Field(foreign_key="newsarticle.id", index=True)
    user_id: str = Field(default="default", index=True)  # For future multi-user support
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # For quick access without joins
    article_title: str = Field(index=True)
    article_source: str = Field(index=True)
    article_url: str = Field(index=True)
    article_published_at: datetime = Field(index=True)
    article_summary: Optional[str] = None
    article_category: Optional[str] = None