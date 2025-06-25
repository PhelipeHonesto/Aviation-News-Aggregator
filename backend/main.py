from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from openai import OpenAI
import requests
from typing import List, Dict, Any

# Local imports
import database
from agents.aviation_pages_reader import fetch_skywest_news
from agents.newsdata_agent import fetch_newsdata_news

# --- Application Setup ---

# Load environment variables from a .env file at the project root
load_dotenv(dotenv_path=database.DB_FILE.parent / ".env")

app = FastAPI(
    title="OsaCurator API",
    description="API for fetching, curating, and publishing news articles.",
    version="1.0.0",
)

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

def get_article_dependency(story_id: str) -> Dict[str, Any]:
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

@app.get("/news", summary="Get All News", response_model=List[Dict], tags=["News"])
def get_news():
    """
    Returns a list of all news articles, sorted by date in descending order.
    """
    news = database.get_all_news()
    return sorted(news, key=lambda x: x.get("date", ""), reverse=True)

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
    existing_links = {article["link"] for article in existing_news if "link" in article}

    unique_new_articles = [
        article for article in all_new_articles if article.get("link") and article["link"] not in existing_links
    ]

    print(f"Found {len(unique_new_articles)} new unique articles.")

    if unique_new_articles:
        combined_news = unique_new_articles + existing_news
        database.save_all_news(combined_news)
        print(f"Saved {len(unique_new_articles)} new articles to the database.")
    else:
        print("No new articles to save.")

    return {"message": f"Successfully ingested {len(unique_new_articles)} new articles."}

@app.post("/select/{story_id}", summary="Select a Story", tags=["Curation"])
def select_story(article: Dict = Depends(get_article_dependency)):
    """Marks an article's status as 'selected'."""
    all_news = database.get_all_news()
    for item in all_news:
        if item.get("id") == article.get("id"):
            item["status"] = "selected"
            break
    database.save_all_news(all_news)
    return {"message": f"Story {article.get('id')} has been selected."}

@app.post("/edit/{story_id}", summary="Rewrite a Story with AI", tags=["Curation"])
def edit_story(article: Dict = Depends(get_article_dependency)):
    """
    Sends a selected or previously edited article to the OpenAI API for rewriting.
    The article's body is updated with the AI-generated text and its status is set to 'edited'.
    """
    if article.get("status") not in ["selected", "edited"]:
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

    client = OpenAI(api_key=openai_api_key)
    prompt = f"Rewrite the following news article for a general audience. Keep it concise, informative, and engaging. \n\nTitle: {article.get('title')}\n\nArticle: {article.get('body')}"
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-4o",
        )
        edited_body = chat_completion.choices[0].message.content
        
        if not edited_body:
            raise HTTPException(status_code=500, detail="AI failed to generate content.")

        all_news = database.get_all_news()
        for item in all_news:
            if item.get("id") == article.get("id"):
                item["body"] = edited_body
                item["status"] = "edited"
                break
        database.save_all_news(all_news)

        return {"message": f"Story {article.get('id')} has been edited by AI."}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred with the OpenAI API: {e}",
        )


def format_slack_message(article: Dict[str, Any]) -> Dict[str, Any]:
    """Return a Slack message payload for a given article."""
    return {
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f":newspaper: {article.get('title', 'No Title')}"},
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": article.get("body", "No content available.")},
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Source: *{article.get('source', 'N/A')}* | <{article.get('link', '#')}|Read Original>",
                    }
                ],
            },
        ]
    }

@app.post("/slack/{story_id}", summary="Post Story to Slack", tags=["Curation"])
def post_to_slack(article: Dict = Depends(get_article_dependency)):
    """
    Formats and sends an edited article to a Slack channel via a webhook.
    The article's status is updated to 'posted'.
    """
    if article.get("status") != "edited":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Article must be 'edited' before posting to Slack.",
        )

    slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not slack_webhook_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SLACK_WEBHOOK_URL is not configured on the server.",
        )

    slack_payload = format_slack_message(article)
    
    try:
        response = requests.post(slack_webhook_url, json=slack_payload)
        response.raise_for_status()  # Raise an exception for bad status codes

        all_news = database.get_all_news()
        for item in all_news:
            if item.get("id") == article.get("id"):
                item["status"] = "posted"
                break
        database.save_all_news(all_news)

        return {"message": f"Story {article.get('id')} has been posted to Slack."}

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to post to Slack: {e}",
        )
