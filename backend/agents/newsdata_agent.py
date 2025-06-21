import os
import uuid
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv


def fetch_newsdata_news():
    """
    Fetches aviation news from the Newsdata.io API.
    """
    # Load environment variables from .env file
    dotenv_path = Path(__file__).parent.parent / ".env"
    load_dotenv(dotenv_path=dotenv_path)

    API_KEY = os.getenv("NEWSDATA_API_KEY")
    if not API_KEY:
        print("Error: NEWSDATA_API_KEY not found in .env file.")
        return []

    URL = f"https://newsdata.io/api/1/news?apikey={API_KEY}&q=aviation&language=en"

    try:
        response = requests.get(URL)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching from Newsdata.io: {e}")
        return []
    except ValueError:  # Catches JSON decoding errors
        print("Error: Could not decode JSON response from Newsdata.io")
        return []

    articles = []
    if data.get("status") == "success":
        for item in data.get("results", []):
            article = {
                "id": str(uuid.uuid4()),
                "title": item.get("title"),
                "date": item.get("pubDate", datetime.now().isoformat()),
                "body": item.get("description", ""),
                "link": item.get("link"),
                "source": item.get("source_id", "Newsdata.io"),
                "status": "new",
            }
            # Ensure we have a title and a link before adding
            if article["title"] and article["link"]:
                articles.append(article)
    else:
        print(
            f"Newsdata.io API returned an error: {data.get('results', {}).get('message')}"
        )

    return articles
