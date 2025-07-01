import os
import uuid
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv
import logging

from .base import NewsAgent


class NewsDataAgent(NewsAgent):
    def fetch(self):
        """
        Fetches aviation news from the Newsdata.io API.
        """
        # Load environment variables from .env file
        dotenv_path = Path(__file__).parent.parent / ".env"
        load_dotenv(dotenv_path=dotenv_path)

        API_KEY = os.getenv("NEWSDATA_API_KEY")
        if not API_KEY:
            logging.error("Error: NEWSDATA_API_KEY not found in .env file.")
            return []

        URL = f"https://newsdata.io/api/1/news?apikey={API_KEY}&q=aviation&language=en"

        try:
            response = requests.get(URL)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching from Newsdata.io: {e}")
            return []
        except ValueError:  # Catches JSON decoding errors
            logging.error("Error: Could not decode JSON response from Newsdata.io")
            return []

        articles = []
        if data.get("status") == "success":
            for item in data.get("results", []):
                article = {
                    # No 'id' field; let DB handle it
                    "title": item.get("title"),
                    "summary": item.get("description", ""),
                    "published_at": item.get("pubDate", datetime.now().isoformat()),
                    "body": item.get("description", ""),
                    "link": item.get("link"),
                    "source": item.get("source_id", "Newsdata.io"),
                    "status": "new",
                }
                # Ensure we have a title and a link before adding
                if article["title"] and article["link"]:
                    articles.append(article)
        else:
            logging.error(f"Newsdata.io API returned an error: {data.get('results', {}).get('message')}")

        return articles

    def parse(self, raw_data):
        pass
