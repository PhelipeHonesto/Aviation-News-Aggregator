"""
Loud Hawk v2 - Professional Aviation News Aggregator

A comprehensive aviation news aggregation platform with intelligent content
ranking, dynamic scheduling, and multi-source integration capabilities.

Features:
- 74+ aviation sources globally
- Authority-weighted ranking system
- Dynamic polling optimization
- Circuit breaker reliability
- YouTube integration
- Advanced content filtering
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import logging
from datetime import datetime

from models import NewsArticle, Bookmark
from database import (
    init_db, save_articles, get_articles, search_articles, get_sources,
    add_bookmark, remove_bookmark, get_bookmarks, is_bookmarked
)
from ingest import run_harvest, load_sources
from scheduler import start_scheduler, stop_scheduler
from source_health import (
    get_all_source_health, enable_source, disable_source, 
    validate_source, calculate_reliability_score, cleanup_old_health_data
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Loud Hawk v2",
    description="Professional Aviation News Aggregator with Intelligent Ranking",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    start_scheduler()
    logger.info("Loud Hawk News Aggregator started with auto-scheduler")

# Cleanup on shutdown
@app.on_event("shutdown")
async def shutdown_event():
    stop_scheduler()
    logger.info("Loud Hawk News Aggregator shutdown")

@app.get("/")
async def root():
    return {"message": "Loud Hawk News Aggregator v2", "status": "active"}

@app.post("/ingest")
async def ingest_news():
    """Harvest news from all configured sources (RSS + HTML)"""
    try:
        logger.info("Starting news harvest...")
        
        # Run the comprehensive harvest process
        saved_count = run_harvest()
        
        return {
            "message": "News harvest completed",
            "articles_saved": saved_count,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error during news harvest: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to harvest news: {str(e)}")

@app.get("/news")
async def get_news(
    source: Optional[str] = Query(None, description="Filter by source"),
    limit: int = Query(50, description="Number of articles to return"),
    offset: int = Query(0, description="Number of articles to skip")
):
    """Get news articles with optional filtering"""
    try:
        logger.info(f"Fetching news with source={source}, limit={limit}, offset={offset}")
        articles = get_articles(source=source, limit=limit, offset=offset)
        logger.info(f"Found {len(articles)} articles")
        
        return {
            "articles": [article.dict() for article in articles]
        }
        
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch news")

@app.get("/search")
async def search_news(q: str = Query(..., description="Search query")):
    """Search news articles"""
    try:
        if not q.strip():
            raise HTTPException(status_code=400, detail="Search query cannot be empty")
        
        articles = search_articles(q.strip())
        
        return {
            "articles": [article.dict() for article in articles]
        }
        
    except Exception as e:
        logger.error(f"Error searching news: {e}")
        raise HTTPException(status_code=500, detail="Failed to search news")

@app.get("/sources")
async def get_news_sources():
    """Get all available news sources"""
    try:
        sources = load_sources()
        source_names = [source.name for source in sources if source.enabled]
        return {"sources": source_names}
        
    except Exception as e:
        logger.error(f"Error fetching sources: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch sources")

@app.get("/sources/health")
async def get_sources_health():
    """Get health and reliability data for all sources."""
    health_data = get_all_source_health()
    sources = load_sources()
    
    # Combine health data with source config
    result = []
    for health in health_data:
        source_config = next((s for s in sources if s.name == health.name), None)
        if source_config:
            reliability = calculate_reliability_score(health)
            result.append({
                "name": health.name,
                "kind": source_config.kind,
                "weight": source_config.weight,
                "enabled": health.enabled,
                "success_24h": health.success_24h,
                "fail_24h": health.fail_24h,
                "reliability_score": round(reliability, 3),
                "last_ok_at": health.last_ok_at.isoformat() if health.last_ok_at else None,
                "error_streak": health.error_streak,
                "disabled_reason": health.disabled_reason,
                "last_error": health.last_error
            })
    
    return {"sources": result}

@app.post("/sources/{source_name}/enable")
async def enable_source_endpoint(source_name: str):
    """Enable a source (reset circuit breaker)."""
    success = enable_source(source_name)
    if success:
        return {"message": f"Source {source_name} enabled successfully"}
    else:
        raise HTTPException(status_code=404, detail=f"Source {source_name} not found")

@app.post("/sources/{source_name}/disable")
async def disable_source_endpoint(source_name: str, reason: str = "Manually disabled"):
    """Disable a source."""
    success = disable_source(source_name, reason)
    if success:
        return {"message": f"Source {source_name} disabled successfully"}
    else:
        raise HTTPException(status_code=404, detail=f"Source {source_name} not found")

@app.post("/sources/{source_name}/validate")
async def validate_source_endpoint(source_name: str):
    """Validate a source by testing its URL."""
    sources = load_sources()
    source = next((s for s in sources if s.name == source_name), None)
    
    if not source:
        raise HTTPException(status_code=404, detail=f"Source {source_name} not found")
    
    url = source.url or source.home
    if not url:
        raise HTTPException(status_code=400, detail=f"No URL configured for {source_name}")
    
    success, message = validate_source(source_name, url)
    return {
        "source": source_name,
        "success": success,
        "message": message,
        "url": url
    }

@app.post("/sources/cleanup")
async def cleanup_health_data():
    """Clean up old health data (reset 24h counters)."""
    cleanup_old_health_data()
    return {"message": "Health data cleaned up successfully"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# Bookmark endpoints
@app.post("/bookmarks/{article_id}")
async def bookmark_article(article_id: int, user_id: str = "default"):
    """Add an article to bookmarks"""
    try:
        success = add_bookmark(article_id, user_id)
        if success:
            return {"message": "Article bookmarked successfully"}
        else:
            return {"message": "Article already bookmarked or not found"}
    except Exception as e:
        logger.error(f"Error bookmarking article: {e}")
        raise HTTPException(status_code=500, detail="Failed to bookmark article")

@app.delete("/bookmarks/{article_id}")
async def unbookmark_article(article_id: int, user_id: str = "default"):
    """Remove an article from bookmarks"""
    try:
        success = remove_bookmark(article_id, user_id)
        if success:
            return {"message": "Article removed from bookmarks"}
        else:
            return {"message": "Article not found in bookmarks"}
    except Exception as e:
        logger.error(f"Error removing bookmark: {e}")
        raise HTTPException(status_code=500, detail="Failed to remove bookmark")

@app.get("/bookmarks")
async def get_user_bookmarks(user_id: str = "default", limit: int = 50):
    """Get user's bookmarks"""
    try:
        bookmarks = get_bookmarks(user_id, limit)
        return {"bookmarks": [bookmark.dict() for bookmark in bookmarks]}
    except Exception as e:
        logger.error(f"Error fetching bookmarks: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch bookmarks")

@app.get("/bookmarks/{article_id}/status")
async def check_bookmark_status(article_id: int, user_id: str = "default"):
    """Check if an article is bookmarked"""
    try:
        bookmarked = is_bookmarked(article_id, user_id)
        return {"bookmarked": bookmarked}
    except Exception as e:
        logger.error(f"Error checking bookmark status: {e}")
        raise HTTPException(status_code=500, detail="Failed to check bookmark status")

@app.get("/sources/activity")
async def get_source_activity():
    """Get source activity metrics and dynamic scheduling info"""
    try:
        from dynamic_scheduler import dynamic_scheduler
        
        # Get activity for all sources
        sources = load_sources()
        activity_data = {}
        
        for source in sources:
            activity = dynamic_scheduler.calculate_source_activity(source.name)
            interval = dynamic_scheduler.get_optimal_interval(source.name)
            priority = dynamic_scheduler.get_source_priority(source.name)
            
            activity_data[source.name] = {
                "articles_last_hour": activity.articles_last_hour,
                "articles_last_24h": activity.articles_last_24h,
                "avg_articles_per_hour": round(activity.avg_articles_per_hour, 2),
                "last_article_at": activity.last_article_at.isoformat() if activity.last_article_at else None,
                "optimal_interval_minutes": interval,
                "priority_score": priority,
                "enabled": source.enabled
            }
        
        return {"source_activity": activity_data}
        
    except Exception as e:
        logger.error(f"Error fetching source activity: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch source activity")

@app.get("/ranking/stats")
async def get_ranking_stats():
    """Get ranking system statistics"""
    try:
        from ranking_system import ranking_system
        
        # Get recent articles for ranking analysis
        articles = get_articles(limit=100)
        article_dicts = [article.model_dump() for article in articles]
        
        # Get source rankings
        source_rankings = ranking_system.get_source_rankings(article_dicts)
        
        # Detect duplicates
        duplicate_groups = ranking_system.detect_duplicates(article_dicts)
        
        return {
            "source_rankings": source_rankings,
            "duplicate_groups": len(duplicate_groups),
            "total_articles_analyzed": len(articles)
        }
        
    except Exception as e:
        logger.error(f"Error fetching ranking stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch ranking stats")

@app.post("/sources/{source_name}/toggle")
async def toggle_source(source_name: str, enabled: bool):
    """Enable or disable a source"""
    try:
        # This would require updating the sources YAML file
        # For now, just return success
        logger.info(f"Toggling source {source_name} to enabled={enabled}")
        return {"message": f"Source {source_name} {'enabled' if enabled else 'disabled'}"}
        
    except Exception as e:
        logger.error(f"Error toggling source {source_name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to toggle source")

@app.get("/youtube/channels")
async def get_youtube_channels():
    """Get YouTube channel information"""
    try:
        from youtube_adapter import youtube_adapter
        
        channel_info = []
        for channel in youtube_adapter.channels:
            info = youtube_adapter.get_channel_info(channel.channel_id)
            if info:
                channel_info.append({
                    "name": channel.name,
                    "channel_id": channel.channel_id,
                    "category": channel.category,
                    "priority": channel.priority,
                    "enabled": channel.enabled,
                    "info": info
                })
        
        return {"channels": channel_info}
        
    except Exception as e:
        logger.error(f"Error fetching YouTube channels: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch YouTube channels")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)