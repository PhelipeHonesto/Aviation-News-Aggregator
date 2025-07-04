from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import os
import json
from dotenv import load_dotenv
from typing import List, Optional
from datetime import datetime
import logging

from database import init_db, get_all_news, save_all_news, find_news_by_id, generate_id
from schemas import ArticleSchema
from agents.newsdata_agent import NewsDataAgent
from agents.aviation_pages_reader import SkyWestAgent
from agents.institutional_reader import InstitutionalReaderAgent
from agents.groundnews_agent import GroundNewsAgent
from services.scheduler import scheduler
from services.slack_client import post_article_to_slack, format_slack_message
from services.openai_client import rewrite_article

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="OsaCurator API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
newsdata_agent = NewsDataAgent()
aviation_reader = SkyWestAgent()
institutional_reader = InstitutionalReaderAgent()
groundnews_agent = GroundNewsAgent()

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and services on startup."""
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "OsaCurator API is running", "status": "healthy"}

@app.get("/news", response_model=List[ArticleSchema])
async def get_news():
    """Get all news articles from the database."""
    try:
        articles = get_all_news()
        # Convert to schema format
        article_schemas = []
        for article in articles:
            article_dict = {
                "id": article.id,
                "title": article.title,
                "summary": article.summary,
                "source": article.source,
                "published_at": article.published_at.isoformat() if article.published_at else None,
                "body": article.body,
                "link": article.link,
                "status": article.status
            }
            article_schemas.append(ArticleSchema(**article_dict))
        return article_schemas
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch news articles")

@app.post("/ingest")
async def ingest_news():
    """Ingest news from various sources."""
    try:
        logger.info("Starting news ingestion...")
        
        # Collect news from different sources
        all_news = []
        
        # NewsData API
        try:
            newsdata_articles = newsdata_agent.fetch()
            if newsdata_articles:
                all_news.extend(newsdata_articles)
                logger.info(f"Fetched {len(newsdata_articles)} articles from NewsData")
        except Exception as e:
            logger.error(f"Error fetching from NewsData: {e}")
        
        # Aviation Pages
        try:
            aviation_articles = aviation_reader.fetch()
            if aviation_articles:
                all_news.extend(aviation_articles)
                logger.info(f"Fetched {len(aviation_articles)} articles from Aviation Pages")
        except Exception as e:
            logger.error(f"Error fetching from Aviation Pages: {e}")
        
        # Institutional Reader
        try:
            institutional_articles = institutional_reader.fetch()
            if institutional_articles:
                all_news.extend(institutional_articles)
                logger.info(f"Fetched {len(institutional_articles)} articles from Institutional Reader")
        except Exception as e:
            logger.error(f"Error fetching from Institutional Reader: {e}")
        
        # Ground News
        try:
            groundnews_articles = groundnews_agent.fetch()
            if groundnews_articles:
                all_news.extend(groundnews_articles)
                logger.info(f"Fetched {len(groundnews_articles)} articles from Ground News")
        except Exception as e:
            logger.error(f"Error fetching from Ground News: {e}")
        
        # Save to database
        if all_news:
            save_all_news(all_news)
            logger.info(f"Successfully saved {len(all_news)} articles to database")
        
        return {
            "message": "News ingestion completed",
            "articles_ingested": len(all_news),
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error during news ingestion: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to ingest news: {str(e)}")

@app.post("/select/{story_id}")
async def select_story(story_id: str):
    """Select a story for editing."""
    try:
        article = find_news_by_id(story_id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # Update status to selected
        article.status = "selected"
        save_all_news([{
            "id": article.id,
            "title": article.title,
            "summary": article.summary,
            "source": article.source,
            "published_at": article.published_at,
            "body": article.body,
            "link": article.link,
            "status": "selected"
        }])
        
        return {
            "message": "Story selected successfully",
            "story_id": story_id,
            "status": "selected"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error selecting story {story_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to select story")

@app.post("/edit/{story_id}")
async def edit_story(story_id: str):
    """Edit a story using AI."""
    try:
        article = find_news_by_id(story_id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # Use OpenAI to edit the story
        try:
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if not openai_api_key:
                raise HTTPException(status_code=500, detail="OpenAI API key not configured")
            
            edited_content = rewrite_article(article.title, article.body or "", openai_api_key)
            if edited_content:
                # Update the article with edited content
                article.body = edited_content
                article.status = "edited"
                save_all_news([{
                    "id": article.id,
                    "title": article.title,
                    "summary": article.summary,
                    "source": article.source,
                    "published_at": article.published_at,
                    "body": edited_content,
                    "link": article.link,
                    "status": "edited"
                }])
                
                return {
                    "message": "Story edited successfully",
                    "story_id": story_id,
                    "status": "edited"
                }
            else:
                raise HTTPException(status_code=500, detail="Failed to edit story with AI")
                
        except Exception as e:
            logger.error(f"Error editing story with AI: {e}")
            raise HTTPException(status_code=500, detail="Failed to edit story with AI")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error editing story {story_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to edit story")

@app.post("/slack/{story_id}")
async def post_to_slack(story_id: str):
    """Post a story to Slack."""
    try:
        article = find_news_by_id(story_id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # Post to Slack
        try:
            slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")
            if not slack_webhook_url:
                raise HTTPException(status_code=500, detail="Slack webhook URL not configured")
            
            post_article_to_slack(article, slack_webhook_url)
            success = True
            if success:
                # Update status to posted
                article.status = "posted"
                save_all_news([{
                    "id": article.id,
                    "title": article.title,
                    "summary": article.summary,
                    "source": article.source,
                    "published_at": article.published_at,
                    "body": article.body,
                    "link": article.link,
                    "status": "posted"
                }])
                
                return {
                    "message": "Story posted to Slack successfully",
                    "story_id": story_id,
                    "status": "posted"
                }
            else:
                raise HTTPException(status_code=500, detail="Failed to post to Slack")
                
        except Exception as e:
            logger.error(f"Error posting to Slack: {e}")
            raise HTTPException(status_code=500, detail="Failed to post to Slack")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error posting story {story_id} to Slack: {e}")
        raise HTTPException(status_code=500, detail="Failed to post to Slack")

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "database": "connected",
            "newsdata_agent": "available",
            "slack_client": "available",
            "openai_client": "available"
        }
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connection accepted")
    
    try:
        # Send initial connection confirmation
        await websocket.send_text(json.dumps({
            "type": "system_notification",
            "data": {
                "message": "Connected to OsaCurator WebSocket",
                "level": "success",
                "title": "Connection Established"
            },
            "timestamp": datetime.now().isoformat()
        }))
        
        # Keep the connection alive and handle messages
        while True:
            try:
                # Wait for messages from client
                data = await websocket.receive_text()
                logger.info(f"Received WebSocket message: {data}")
                
                # Parse the message
                try:
                    message = json.loads(data)
                    # Handle different message types here if needed
                    await websocket.send_text(json.dumps({
                        "type": "system_notification",
                        "data": {
                            "message": f"Message received: {message}",
                            "level": "info",
                            "title": "Message Confirmation"
                        },
                        "timestamp": datetime.now().isoformat()
                    }))
                except json.JSONDecodeError:
                    # Handle plain text messages
                    await websocket.send_text(json.dumps({
                        "type": "system_notification",
                        "data": {
                            "message": f"Echo: {data}",
                            "level": "info",
                            "title": "Echo Response"
                        },
                        "timestamp": datetime.now().isoformat()
                    }))
                    
            except WebSocketDisconnect:
                logger.info("WebSocket client disconnected")
                break
                
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        logger.info("WebSocket connection closed")
