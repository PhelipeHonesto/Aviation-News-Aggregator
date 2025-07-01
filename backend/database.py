import json
from pathlib import Path
from typing import List, Dict, Optional
import uuid

# --- Constants ---
DB_FILE = Path(__file__).parent / "news.json"


# --- Private Functions ---
def _read_db() -> List[Dict]:
    """
    Loads all news articles from the JSON database.
    If the file doesn't exist, it creates an empty one.
    """
    if not DB_FILE.exists():
        DB_FILE.touch()
        return []

    try:
        with open(DB_FILE, "r") as f:
            # Handle empty file case
            content = f.read()
            if not content:
                return []
            return json.loads(content)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error reading database file: {e}")
        return []


def _write_db(news_list: List[Dict]):
    """Saves a list of news articles to the JSON database."""
    try:
        with open(DB_FILE, "w") as f:
            json.dump(news_list, f, indent=2)
    except IOError as e:
        print(f"Error writing to database file: {e}")


# --- Public API ---
def get_all_news() -> List[Dict]:
    """Returns all news articles from the database."""
    return _read_db()


def save_all_news(news_list: List[Dict]):
    """Saves a list of news articles to the JSON database."""
    _write_db(news_list)


def find_news_by_id(story_id: str) -> Optional[Dict]:
    """Finds a single news article by its ID."""
    all_news = get_all_news()
    for article in all_news:
        if article.get("id") == story_id:
            return article
    return None


def generate_id() -> str:
    """Generates a unique ID for an article."""
    return str(uuid.uuid4())
