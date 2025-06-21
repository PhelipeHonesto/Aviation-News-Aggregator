import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .agents.aviation_pages_reader import fetch_skywest_news
from .agents.newsdata_agent import fetch_newsdata_news

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/news")
def get_news():
    # Locate news.json relative to the current file
    script_dir = Path(__file__).parent
    news_file = script_dir / "news.json"
    try:
        with open(news_file, "r") as f:
            news = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        news = []
    return news

@app.post("/ingest")
def ingest_news():
    # Load existing news
    script_dir = Path(__file__).parent
    news_file = script_dir / "news.json"
    try:
        with open(news_file, "r") as f:
            existing_news = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_news = []

    # Collect existing links to avoid duplicates
    existing_links = {article["link"] for article in existing_news}

    # Fetch from agents
    skywest_articles = fetch_skywest_news()
    newsdata_articles = fetch_newsdata_news()
    new_articles = skywest_articles + newsdata_articles

    # Filter duplicates
    unique_new_articles = [
        article for article in new_articles if article["link"] not in existing_links
    ]

    # Combine and save
    combined_news = unique_new_articles + existing_news
    with open(news_file, "w") as f:
        json.dump(combined_news, f, indent=2)

    return {"message": f"Successfully ingested {len(unique_new_articles)} new articles."}
