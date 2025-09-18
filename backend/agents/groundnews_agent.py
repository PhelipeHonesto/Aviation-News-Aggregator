"""GroundNews scraping agent for aviation news."""

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


class GroundNewsAgent(NewsAgent):
    """Agent for scraping aviation news from GroundNews website."""
    
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    def __init__(self):
        # Load environment variables
        dotenv_path = Path(__file__).parent.parent / ".env"
        load_dotenv(dotenv_path=dotenv_path)
        
        # GroundNews RSS feed or main page
        self.base_url = "https://ground.news"
        self.aviation_url = "https://ground.news/sources/aviation"
    
    def fetch(self) -> List[Dict[str, Any]]:
        """
        Fetch aviation news from GroundNews.
        """
        try:
            # Try to get aviation-specific news
            articles = self._scrape_aviation_page()
            if not articles:
                # Fallback to general news with aviation keywords
                articles = self._scrape_general_news()
            
            logging.info(f"GroundNews agent fetched {len(articles)} articles")
            return articles
            
        except Exception as e:
            logging.error(f"Error fetching from GroundNews: {e}")
            return []
    
    def _scrape_aviation_page(self) -> List[Dict[str, Any]]:
        """Scrape the aviation-specific page."""
        try:
            response = requests.get(self.aviation_url, headers=self.HEADERS, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "html.parser")
            articles = []
            
            # Look for article containers (this will need to be updated based on actual GroundNews structure)
            article_containers = soup.find_all("div", class_=["article", "story", "news-item"], limit=10)
            
            for container in article_containers:
                try:
                    # Extract title
                    title_elem = container.find(["h1", "h2", "h3", "h4"])
                    if not title_elem:
                        continue
                    title = title_elem.get_text(strip=True)
                    
                    # Extract link
                    link_elem = container.find("a")
                    if not link_elem:
                        continue
                    link = link_elem.get("href", "")
                    if link.startswith("/"):
                        link = self.base_url + link
                    
                    # Extract summary/description
                    summary_elem = container.find(["p", "div"], class_=["summary", "description", "excerpt"])
                    summary = summary_elem.get_text(strip=True) if summary_elem else ""
                    
                    # Extract date
                    date_elem = container.find(["time", "span"], class_=["date", "published"])
                    published_at = datetime.now()
                    if date_elem:
                        date_text = date_elem.get_text(strip=True)
                        # Try to parse various date formats
                        try:
                            published_at = datetime.strptime(date_text, "%Y-%m-%d")
                        except ValueError:
                            try:
                                published_at = datetime.strptime(date_text, "%B %d, %Y")
                            except ValueError:
                                published_at = datetime.now()
                    
                    if title and link:
                        article = {
                            "title": title,
                            "summary": summary[:300] if summary else "",
                            "published_at": published_at.isoformat(),
                            "body": summary,
                            "link": link,
                            "source": "GroundNews",
                            "status": "new",
                        }
                        articles.append(article)
                        
                except Exception as e:
                    logging.warning(f"Error parsing article container: {e}")
                    continue
            
            return articles
            
        except Exception as e:
            logging.error(f"Error scraping GroundNews aviation page: {e}")
            return []
    
    def _scrape_general_news(self) -> List[Dict[str, Any]]:
        """Fallback to scrape general news and filter for aviation content."""
        try:
            response = requests.get(self.base_url, headers=self.HEADERS, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "html.parser")
            articles = []
            
            # Look for general article containers
            article_containers = soup.find_all("div", class_=["article", "story", "news-item"], limit=20)
            
            aviation_keywords = [
                "aviation", "airline", "aircraft", "airport", "pilot", "flight", 
                "airplane", "helicopter", "air traffic", "faa", "boeing", "airbus",
                "airline industry", "aviation safety", "air travel"
            ]
            
            for container in article_containers:
                try:
                    # Extract title
                    title_elem = container.find(["h1", "h2", "h3", "h4"])
                    if not title_elem:
                        continue
                    title = title_elem.get_text(strip=True)
                    
                    # Check if title contains aviation keywords
                    title_lower = title.lower()
                    if not any(keyword in title_lower for keyword in aviation_keywords):
                        continue
                    
                    # Extract link
                    link_elem = container.find("a")
                    if not link_elem:
                        continue
                    link = link_elem.get("href", "")
                    if link.startswith("/"):
                        link = self.base_url + link
                    
                    # Extract summary
                    summary_elem = container.find(["p", "div"], class_=["summary", "description", "excerpt"])
                    summary = summary_elem.get_text(strip=True) if summary_elem else ""
                    
                    # Extract date
                    date_elem = container.find(["time", "span"], class_=["date", "published"])
                    published_at = datetime.now()
                    if date_elem:
                        date_text = date_elem.get_text(strip=True)
                        try:
                            published_at = datetime.strptime(date_text, "%Y-%m-%d")
                        except ValueError:
                            try:
                                published_at = datetime.strptime(date_text, "%B %d, %Y")
                            except ValueError:
                                published_at = datetime.now()
                    
                    if title and link:
                        article = {
                            "title": title,
                            "summary": summary[:300] if summary else "",
                            "published_at": published_at.isoformat(),
                            "body": summary,
                            "link": link,
                            "source": "GroundNews",
                            "status": "new",
                        }
                        articles.append(article)
                        
                except Exception as e:
                    logging.warning(f"Error parsing article container: {e}")
                    continue
            
            return articles[:10]  # Limit to 10 articles
            
        except Exception as e:
            logging.error(f"Error scraping GroundNews general page: {e}")
            return []

    def parse(self, raw_data):
        """Parse raw data if needed."""
        pass
