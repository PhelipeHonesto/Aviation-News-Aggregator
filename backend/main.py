from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    status,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from openai import OpenAI
import requests
from typing import List, Any
import asyncio

# Local imports
from . import database
from .database import Article
from .agents.aviation_pages_reader import fetch_skywest_news
from .agents.newsdata_agent import fetch_newsdata_news

# --- Application Setup ---

# Load environment variables from a .env file at the project root
load_dotenv(dotenv_path=database.DB_PATH.replace('news.db', '.env'))

app = FastAPI(
    title="OsaCurator API",
    description="API for fetching, curating, and publishing news articles.",
    version="1.0.0",
)


@app.on_event("startup")
def on_startup() -> None:
    """Initialize the database on application startup."""
    database.init_db()

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
    article = database.find_news_by_id(story_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article with ID '{story_id}' not found.",
        )
    return article

# --- API Endpoints ---

@app.get("/", summary="Root Endpoint", tags=["Health"])
def read_root():
    """A simple health check endpoint to confirm the API is running."""
    return {"status": "ok", "message": "Welcome to OsaCurator API"}

@app.get("/news", summary="Get All News", response_model=List[Article], tags=["News"])
def get_news():
    """
    Returns a list of all news articles, sorted by date in descending order.
    """
    news = database.get_all_news()
    return sorted(news, key=lambda x: x.date or "", reverse=True)

@app.post("/ingest", summary="Ingest New Articles", tags=["News"])
def ingest_news():
    """
    Fetches new articles from all registered agents, filters out duplicates
    based on the article link, and saves the new, unique articles to the database.
    """
    print("Starting news ingestion...")
    all_new_articles = []

    # --- SkyWest Agent ---
    try:
        print("Fetching news from SkyWest...")
        skywest_articles = fetch_skywest_news()
        print(f"Found {len(skywest_articles)} articles from SkyWest.")
        all_new_articles.extend(skywest_articles)
    except Exception as e:
        print(f"Error fetching news from SkyWest: {e}")

    # --- Newsdata.io Agent ---
    try:
        print("Fetching news from Newsdata.io...")
        newsdata_articles = fetch_newsdata_news()
        print(f"Found {len(newsdata_articles)} articles from Newsdata.io.")
        all_new_articles.extend(newsdata_articles)
    except Exception as e:
        print(f"Error fetching news from Newsdata.io: {e}")

    existing_news = database.get_all_news()
    existing_links = {article.link for article in existing_news if article.link}

    unique_new_articles = [
        article for article in all_new_articles
        if article.get("link") and article["link"] not in existing_links
    ]

    print(f"Found {len(unique_new_articles)} new unique articles.")

    if unique_new_articles:
        # Convert dicts to Article objects for saving
        combined_news = [Article(**a) if not isinstance(a, Article) else a for a in (unique_new_articles + [a.dict() if not isinstance(a, dict) else a for a in existing_news])]
        # Save as dicts for compatibility with save_all_news
        database.save_all_news([a.dict() if isinstance(a, Article) else a for a in combined_news])
        print(f"Saved {len(unique_new_articles)} new articles to the database.")
    else:
        print("No new articles to save.")

    return {
        "message": f"Successfully ingested {len(unique_new_articles)} new articles."
    }

@app.post("/select/{story_id}", summary="Select a Story", tags=["Curation"])
def select_story(article: Article = Depends(get_article_dependency)):
    """Marks an article's status as 'selected'."""
    article.status = "selected"
    # Save update
    with database.Session(database.engine) as session:
        session.add(article)
        session.commit()
    return {"message": f"Story {article.id} has been selected."}

@app.post("/edit/{story_id}", summary="Rewrite a Story with AI", tags=["Curation"])
def edit_story(article: Article = Depends(get_article_dependency)):
    """
    Sends a selected or previously edited article to the OpenAI API for rewriting.
    The article's body is updated with the AI-generated text and its status is set to 'edited'.
    """
    if article.status not in ["selected", "edited"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Article must be 'selected' or 'edited' before sending to AI.",
        )

    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OPENAI_API_KEY is not configured on the server.",
        )

    import httpx

    # Create a custom httpx client without any proxy configuration
    http_client = httpx.Client(timeout=httpx.Timeout(30.0), follow_redirects=True)

    client = OpenAI(api_key=openai_api_key, http_client=http_client)
    prompt = f"Rewrite the following news article for a general audience. Keep it concise, informative, and engaging. \n\nTitle: {article.title}\n\nArticle: {article.body}"

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
        )
        edited_body = response.choices[0].message.content

        if not edited_body:
            raise HTTPException(
                status_code=500, detail="AI failed to generate content."
            )

        article.body = edited_body
        article.status = "edited"
        with database.Session(database.engine) as session:
            session.add(article)
            session.commit()

        return {"message": f"Story {article.id} has been edited by AI."}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred with the OpenAI API: {e}",
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
def post_to_slack(article: Article = Depends(get_article_dependency)):
    """
    Formats and sends an edited article to a Slack channel via a webhook.
    The article's status is updated to 'posted'.
    """
    if article.status != "edited":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Article must be 'edited' before posting to Slack.",
        )

    slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not slack_webhook_url:
        # Instead of failing, just update the status and return success
        article.status = "posted"
        with database.Session(database.engine) as session:
            session.add(article)
            session.commit()
        return {
            "message": f"Story {article.id} has been marked as posted (Slack webhook not configured)."
        }

    slack_payload = format_slack_message(article)

    try:
        response = requests.post(slack_webhook_url, json=slack_payload)
        response.raise_for_status()  # Raise an exception for bad status codes
        article.status = "posted"
        with database.Session(database.engine) as session:
            session.add(article)
            session.commit()
        return {"message": f"Story {article.id} has been posted to Slack."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred posting to Slack: {e}",
        )

# --- WebSocket Endpoint ---

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await websocket.send_json({"type": "ping", "data": "pong"})
            await asyncio.sleep(10)
    except WebSocketDisconnect:
        print("WebSocket disconnected")
