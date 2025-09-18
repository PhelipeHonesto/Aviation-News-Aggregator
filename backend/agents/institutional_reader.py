"""Institutional news reader for aviation organizations."""

import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import logging

from .base import NewsAgent


class InstitutionalReaderAgent(NewsAgent):
    """Agent for reading news from institutional aviation sources."""
    
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    def __init__(self):
        # Load environment variables
        dotenv_path = Path(__file__).parent.parent / ".env"
        load_dotenv(dotenv_path=dotenv_path)
        
        # List of institutional aviation sources
        self.sources = [
            {
                "name": "FAA News",
                "url": "https://www.faa.gov/news",
                "selectors": {
                    "articles": "div.news-item, article, .press-release",
                    "title": "h1, h2, h3, .title",
                    "link": "a",
                    "summary": "p, .summary, .excerpt",
                    "date": "time, .date, .published"
                }
            },
            {
                "name": "ICAO News",
                "url": "https://www.icao.int/Newsroom/Pages/default.aspx",
                "selectors": {
                    "articles": "div.news-item, .news-article",
                    "title": "h1, h2, h3, .title",
                    "link": "a",
                    "summary": "p, .summary, .excerpt",
                    "date": "time, .date, .published"
                }
            },
            {
                "name": "IATA News",
                "url": "https://www.iata.org/en/pressroom/",
                "selectors": {
                    "articles": "div.news-item, .press-release, article",
                    "title": "h1, h2, h3, .title",
                    "link": "a",
                    "summary": "p, .summary, .excerpt",
                    "date": "time, .date, .published"
                }
            }
        ]
    
    def fetch(self) -> List[Dict[str, Any]]:
        """
        Fetch news from institutional aviation sources.
        """
        all_articles = []
        
        for source in self.sources:
            try:
                articles = self._scrape_source(source)
                all_articles.extend(articles)
                logging.info(f"Institutional agent fetched {len(articles)} articles from {source['name']}")
            except Exception as e:
                logging.error(f"Error fetching from {source['name']}: {e}")
                continue
        
        return all_articles
    
    def _scrape_source(self, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scrape a specific institutional source."""
        try:
            response = requests.get(source["url"], headers=self.HEADERS, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "html.parser")
            articles = []
            
            # Find article containers
            article_containers = soup.select(source["selectors"]["articles"])
            
            for container in article_containers[:10]:  # Limit to 10 articles per source
                try:
                    # Extract title
                    title_elem = container.select_one(source["selectors"]["title"])
                    if not title_elem:
                        continue
                    title = title_elem.get_text(strip=True)
                    
                    # Extract link
                    link_elem = container.select_one(source["selectors"]["link"])
                    if not link_elem:
                        continue
                    
                    link = link_elem.get("href", "")
                    if link.startswith("/"):
                        link = source["url"] + link
                    elif not link.startswith("http"):
                        link = source["url"] + "/" + link
                    
                    # Extract summary
                    summary_elem = container.select_one(source["selectors"]["summary"])
                    summary = summary_elem.get_text(strip=True) if summary_elem else ""
                    
                    # Extract date
                    date_elem = container.select_one(source["selectors"]["date"])
                    published_at = datetime.now()
                    if date_elem:
                        date_text = date_elem.get_text(strip=True)
                        published_at = self._parse_date(date_text)
                    
                    if title and link:
                        article = {
                            "title": title,
                            "summary": summary[:300] if summary else "",
                            "published_at": published_at.isoformat(),
                            "body": summary,
                            "link": link,
                            "source": source["name"],
                            "status": "new",
                        }
                        articles.append(article)
                        
                except Exception as e:
                    logging.warning(f"Error parsing article from {source['name']}: {e}")
                    continue
            
            return articles
            
        except Exception as e:
            logging.error(f"Error scraping {source['name']}: {e}")
            return []
    
    def _parse_date(self, date_text: str) -> datetime:
        """Parse various date formats."""
        date_formats = [
            "%Y-%m-%d",
            "%B %d, %Y",
            "%b %d, %Y",
            "%d %B %Y",
            "%d %b %Y",
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%Y-%m-%d %H:%M:%S",
            "%B %d, %Y at %I:%M %p"
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_text.strip(), fmt)
            except ValueError:
                continue
        
        # If no format matches, return current time
        return datetime.now()

    def parse(self, raw_data):
        """Parse raw data if needed."""
        pass
