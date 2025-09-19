"""
Loud Hawk v2 - Aviation News Aggregator
Clean, focused FastAPI backend for RSS aggregation
"""
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import logging
from datetime import datetime

from models import NewsArticle, Bookmark
from database import init_db, save_articles, get_articles, search_articles, get_sources, add_bookmark, remove_bookmark, get_bookmarks, is_bookmarked
from ingest import run_harvest, load_sources
from scheduler import start_scheduler, stop_scheduler
from source_health import (
    get_all_source_health, enable_source, disable_source, 
    validate_source, calculate_reliability_score, cleanup_old_health_data
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Loud Hawk News Aggregator",
    description="Aviation news aggregation platform",
    version="2.0.0"
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
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(50, description="Number of articles to return"),
    offset: int = Query(0, description="Number of articles to skip")
):
    """Get news articles with optional filtering"""
    try:
        logger.info(f"Fetching news with source={source}, category={category}, limit={limit}, offset={offset}")
        articles = get_articles(source=source, category=category, limit=limit, offset=offset)
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
                "category": source_config.category,
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)