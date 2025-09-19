"""
Loud Hawk v2 - Data Models

Professional data models for aviation news aggregation with:
- Canonical URL deduplication
- Content hash fingerprinting
- Optimized database indexing
"""

from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
import hashlib
import urllib.parse as urlparse


class NewsArticle(SQLModel, table=True):
    """
    Enhanced news article model for professional RSS aggregation
    
    Features:
    - Canonical URL deduplication
    - Content hash fingerprinting
    - Optimized database indexing
    - Source tracking and categorization
    """
    
    id: Optional[int] = Field(default=None, primary_key=True)
    source: str = Field(index=True)  # "FAA", "NTSB", "Airbus", etc.
    title: str = Field(index=True)
    url: str = Field(index=True)  # Original URL
    canonical_url: str = Field(unique=True, index=True)  # Normalized canonical URL
    published_at: datetime = Field(index=True)
    summary: Optional[str] = None
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    
    # For deduplication
    content_hash: str = Field(unique=True, index=True)
    
    @classmethod
    def normalize_url(cls, url: str) -> str:
        """Normalize URL by removing UTM parameters and trailing slashes"""
        try:
            parsed = urlparse.urlparse(url)
            # Remove UTM parameters and other tracking parameters
            query_params = urlparse.parse_qsl(parsed.query, keep_blank_values=False)
            filtered_params = [
                (k, v) for k, v in query_params 
                if not k.lower().startswith(("utm_", "fbclid", "gclid", "ref"))
            ]
            new_query = urlparse.urlencode(filtered_params, doseq=True)
            # Remove trailing slash from path
            path = parsed.path.rstrip("/")
            # Reconstruct URL
            return urlparse.urlunparse((
                parsed.scheme, 
                parsed.netloc.lower(), 
                path, 
                parsed.params, 
                new_query, 
                ""
            ))
        except Exception:
            return url
    
    @classmethod
    def create_hash(cls, title: str, canonical_url: str, published_at: datetime) -> str:
        """Create content hash for deduplication using normalized data"""
        # Use first 120 chars of title and first 10 chars of date for consistent hashing
        title_snippet = title.lower().strip()[:120]
        date_snippet = published_at.strftime("%Y-%m-%d")
        content = f"{canonical_url}|{title_snippet}|{date_snippet}"
        return hashlib.sha256(content.encode()).hexdigest()


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