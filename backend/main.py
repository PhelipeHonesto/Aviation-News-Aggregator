from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    status,
    WebSocket,
    WebSocketDisconnect,
    Path,
)
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from openai import OpenAI
import requests
from typing import List, Any, Optional
import asyncio
from sqlmodel import select, Session
from sqlalchemy import func
import logging

# Local imports
from database import Article, engine, get_all_news, save_all_news, find_news_by_id, init_db
from schemas import ArticleSchema
from agents.aviation_pages_reader import SkyWestAgent
from agents.newsdata_agent import NewsDataAgent
from agents.groundnews_agent import GroundNewsAgent
from agents.institutional_reader import InstitutionalReaderAgent
from services.openai_client import rewrite_article
from services.slack_client import post_article_to_slack
from services.scheduler import start_scheduler, schedule_ingestion_job

# --- Application Setup ---

# Load environment variables from a .env file at the project root
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

app = FastAPI(
    title="OsaCurator API",
    description="API for fetching, curating, and publishing news articles.",
    version="1.0.0",
)

logging.basicConfig(level=logging.INFO)

def ingest_news_job() -> None:
    """Job function to ingest news, used by both API and scheduler."""
    logging.info("[Scheduler] Running news ingestion job...")
    all_new_articles = []
    try:
        logging.info("Fetching news from SkyWest...")
        skywest_articles = SkyWestAgent().fetch()
        logging.info(f"Found {len(skywest_articles)} articles from SkyWest.")
        all_new_articles.extend(skywest_articles)
    except Exception as e:
        logging.error(f"Error fetching news from SkyWest: {e}")
    try:
        logging.info("Fetching news from Newsdata.io...")
        newsdata_articles = NewsDataAgent().fetch()
        logging.info(f"Found {len(newsdata_articles)} articles from Newsdata.io.")
        all_new_articles.extend(newsdata_articles)
    except Exception as e:
        logging.error(f"Error fetching news from Newsdata.io: {e}")
    existing_news = get_all_news()
    existing_links = {article.link for article in existing_news if article.link}
    unique_new_articles = [
        article for article in all_new_articles
        if article.get("link") and article["link"] not in existing_links
    ]
    logging.info(f"Found {len(unique_new_articles)} new unique articles.")
    if unique_new_articles:
        combined_news = [Article(**a) if not isinstance(a, Article) else a for a in (unique_new_articles + [a.dict() if not isinstance(a, dict) else a for a in existing_news])]
        save_all_news([a.dict() if isinstance(a, Article) else a for a in combined_news])
        logging.info(f"Saved {len(unique_new_articles)} new articles to the database.")
    else:
        logging.info("No new articles to save.")

@app.on_event("startup")
def on_startup() -> None:
    """Initialize the database and scheduler on application startup."""
    init_db()
    start_scheduler()
    schedule_ingestion_job(ingest_news_job, interval_minutes=60)

# CORS (Cross-Origin Resource Sharing) middleware allows the frontend
# (running on a different origin) to communicate with this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# --- Dependencies ---

def get_article_dependency(story_id: str) -> Article:
    """
    FastAPI dependency to fetch a single article by its ID.
    Raises a 404 HTTPException if the article is not found.
    """
    article = find_news_by_id(story_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article with ID '{story_id}' not found.",
        )
    return article

# --- API Endpoints ---

@app.get("/", summary="Root Endpoint", tags=["Health"])
def read_root() -> dict:
    """A simple health check endpoint to confirm the API is running."""
    return {"status": "ok", "message": "Welcome to OsaCurator API"}

@app.get("/news", summary="Get All News", response_model=List[ArticleSchema], tags=["News"])
def get_news(
    q: Optional[str] = None,
    source: Optional[str] = None,
    skip: int = 0,
    limit: int = 20
) -> List[ArticleSchema]:
    """
    Returns a list of all news articles, with optional search, filtering, and pagination.
    """
    with Session(engine) as session:
        statement = select(Article)
        if q:
            statement = statement.where(func.lower(Article.title).contains(q.lower()))
        if source:
            statement = statement.where(Article.source == source)
        statement = statement.offset(skip).limit(limit)
        articles = session.exec(statement).all()
        return articles

@app.post("/ingest", summary="Ingest New Articles", tags=["News"])
def ingest_news() -> dict:
    """API endpoint to trigger news ingestion immediately."""
    try:
        ingest_news_job()
        return {"message": "News ingestion triggered."}
    except Exception as e:
        logging.error(f"Error during ingestion: {e}")
        raise HTTPException(status_code=500, detail="Error during ingestion.")

@app.post("/select/{story_id}", summary="Select a Story", tags=["Curation"])
def select_story(article: Article = Depends(get_article_dependency)) -> dict:
    """Marks an article's status as 'selected'."""
    try:
        article.status = "selected"
        with Session(engine) as session:
            session.add(article)
            session.commit()
        return {"message": f"Story {article.id} has been selected."}
    except Exception as e:
        logging.error(f"Error selecting story: {e}")
        raise HTTPException(status_code=500, detail="Error selecting story.")

@app.post("/edit/{story_id}", summary="Rewrite a Story with AI", tags=["Curation"])
def edit_story(article: Article = Depends(get_article_dependency)) -> dict:
    if article.status not in ["selected", "edited"]:
        logging.warning("Article must be 'selected' or 'edited' before sending to AI.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Article must be 'selected' or 'edited' before sending to AI."
        )
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        logging.error("OPENAI_API_KEY is not configured on the server.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OPENAI_API_KEY is not configured on the server."
        )
    try:
        edited_body = rewrite_article(article.title, article.body or "", openai_api_key)
        article.body = edited_body
        article.status = "edited"
        with Session(engine) as session:
            session.add(article)
            session.commit()
        return {"message": f"Story {article.id} has been edited by AI."}
    except Exception as e:
        logging.error(f"An error occurred with the OpenAI API: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred with the OpenAI API: {e}"
        )

def format_slack_message(article: Article) -> dict:
    """Return a Slack message payload for a given article."""
    return {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f":newspaper: {article.title or 'No Title'}",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": article.body or "No content available.",
                },
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Source: *{article.source or 'N/A'}* | <{article.link or '#'}|Read Original>",
                    }
                ],
            },
        ]
    }

@app.post("/slack/{story_id}", summary="Post Story to Slack", tags=["Curation"])
def post_to_slack_endpoint(article: Article = Depends(get_article_dependency)) -> dict:
    if article.status != "edited":
        logging.warning("Article must be 'edited' before posting to Slack.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Article must be 'edited' before posting to Slack."
        )
    slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not slack_webhook_url:
        article.status = "posted"
        with Session(engine) as session:
            session.add(article)
            session.commit()
        return {
            "message": f"Story {article.id} has been marked as posted (Slack webhook not configured)."
        }
    try:
        post_article_to_slack(article, slack_webhook_url)
        article.status = "posted"
        with Session(engine) as session:
            session.add(article)
            session.commit()
        return {"message": f"Story {article.id} has been posted to Slack."}
    except Exception as e:
        logging.error(f"An error occurred posting to Slack: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred posting to Slack: {e}"
        )

# Get a single article by ID
@app.get("/news/{story_id}", response_model=ArticleSchema, tags=["News"])
def get_article(story_id: str = Path(..., description="The ID of the article to retrieve")) -> ArticleSchema:
    article = find_news_by_id(story_id)
    if not article:
        logging.warning(f"Article with ID {story_id} not found.")
        raise HTTPException(status_code=404, detail="Article not found")
    return article

# --- WebSocket Endpoint ---

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await websocket.send_json({"type": "ping", "data": "pong"})
            await asyncio.sleep(10)
    except WebSocketDisconnect:
        logging.info("WebSocket disconnected")
