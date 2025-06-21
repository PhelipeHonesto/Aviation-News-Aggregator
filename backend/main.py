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
    # Correctly locate news.json relative to the current file
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
    # --- Read existing news ---
    script_dir = Path(__file__).parent
    news_file = script_dir / "news.json"
    try:
        with open(news_file, "r") as f:
            existing_news = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_news = []

    existing_links = {article['link'] for article in existing_news}

    # --- Fetch new news from agents ---
    skywest_articles = fetch_skywest_news()
    newsdata_articles = fetch_newsdata_news()
    new_articles = skywest_articles + newsdata_articles

    # --- Filter out duplicates ---
    unique_new_articles = [
        article for article in new_articles if article['link'] not in existing_links
    ]

    # --- Combine and save ---
    combined_news = unique_new_articles + existing_news

    with open(news_file, "w") as f:
        json.dump(combined_news, f, indent=2)

    return {"message": f"Successfully ingested {len(unique_new_articles)} new articles."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
