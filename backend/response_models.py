"""
Loud Hawk v2 - API Response Models

Professional Pydantic response models for consistent API responses
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ArticleResponse(BaseModel):
    """Article response model"""
    id: int
    title: str
    url: str
    canonical_url: str
    source: str
    published_at: datetime
    summary: Optional[str] = None
    fetched_at: datetime
    content_hash: str
    score: Optional[float] = Field(None, description="Authority-weighted score")
    authority_score: Optional[float] = Field(None, description="Source authority score")
    recency_score: Optional[float] = Field(None, description="Recency score")
    quality_score: Optional[float] = Field(None, description="Content quality score")


class NewsResponse(BaseModel):
    """News endpoint response model"""
    articles: List[ArticleResponse]
    total_count: int
    limit: int
    offset: int
    next_cursor: Optional[str] = Field(None, description="Cursor for pagination")


class BookmarkResponse(BaseModel):
    """Bookmark response model"""
    id: int
    article_id: int
    user_id: str
    created_at: datetime
    article_title: str
    article_source: str
    article_url: str
    article_published_at: datetime
    article_summary: Optional[str] = None


class BookmarkListResponse(BaseModel):
    """Bookmark list response model"""
    bookmarks: List[BookmarkResponse]
    total_count: int
    limit: int
    offset: int


class SourceHealthResponse(BaseModel):
    """Source health response model"""
    name: str
    enabled: bool
    success_24h: int
    fail_24h: int
    last_ok_at: Optional[datetime] = None
    disabled_reason: Optional[str] = None
    error_streak: int = 0
    success_rate: float = 0.0
    reliability_score: float = 0.0


class SourceHealthListResponse(BaseModel):
    """Source health list response model"""
    sources: List[SourceHealthResponse]
    total_sources: int
    active_sources: int
    grounded_sources: int


class SourceActivityResponse(BaseModel):
    """Source activity response model"""
    articles_last_hour: int
    articles_last_24h: int
    avg_articles_per_hour: float
    last_article_at: Optional[datetime] = None
    optimal_interval_minutes: int
    priority_score: int
    enabled: bool


class SourceActivityListResponse(BaseModel):
    """Source activity list response model"""
    source_activity: dict[str, SourceActivityResponse]


class RankingStatsResponse(BaseModel):
    """Ranking statistics response model"""
    source_rankings: dict[str, dict]
    duplicate_groups: int
    total_articles_analyzed: int


class IngestResponse(BaseModel):
    """Ingest endpoint response model"""
    message: str
    articles_saved: int
    status: str


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    timestamp: datetime
    version: str = "2.0.0"
    sources_active: Optional[int] = None
    last_ingest: Optional[datetime] = None


class SourceToggleResponse(BaseModel):
    """Source toggle response model"""
    message: str
    source_name: str
    enabled: bool


class SearchResponse(BaseModel):
    """Search response model"""
    articles: List[ArticleResponse]
    query: str
    total_count: int
    limit: int
    offset: int


class YouTubeChannelResponse(BaseModel):
    """YouTube channel response model"""
    name: str
    channel_id: str
    category: str
    priority: int
    enabled: bool
    info: Optional[dict] = None


class YouTubeChannelsResponse(BaseModel):
    """YouTube channels response model"""
    channels: List[YouTubeChannelResponse]


class ErrorResponse(BaseModel):
    """Error response model"""
    detail: str
    error_type: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SuccessResponse(BaseModel):
    """Generic success response model"""
    message: str
    status: str = "success"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
