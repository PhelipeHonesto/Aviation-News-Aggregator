"""Utilities for scraping news from aviation web pages."""

import uuid
from datetime import datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from .base import NewsAgent

class SkyWestAgent(NewsAgent):
    HEADERS = {"User-Agent": "Mozilla/5.0"}
    URL = "https://inc.skywest.com/news-and-events/press-releases/"

    def _fetch_article_body(self, url: str) -> str:
        """Return the first paragraph or Open Graph description of a news article."""
        try:
            resp = requests.get(url, headers=self.HEADERS, timeout=10)
            resp.raise_for_status()
        except requests.RequestException as exc:
            print(f"Error fetching article body from {url}: {exc}")
            return ""

        soup = BeautifulSoup(resp.content, "lxml")

        og = soup.find("meta", attrs={"property": "og:description"})
        if isinstance(og, Tag):
            content = og.get("content")
            if isinstance(content, str):
                return content.strip()

        first_p = soup.find("p")
        if first_p is not None:
            text = first_p.get_text(strip=True)
            if isinstance(text, str):
                return text

        return ""

    def fetch(self):
        """Scrape the SkyWest press release page and return recent articles."""
        try:
            response = requests.get(self.URL, headers=self.HEADERS, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching URL {self.URL}: {e}")
            return []

        soup = BeautifulSoup(response.content, "lxml")
        articles = []

        # The news items are in a 'div' with class 'news-release-item'
        for item in soup.select("div.news-release-item", limit=15):
            # Select the 'a' tag directly to avoid intermediate access that confuses the linter
            link_element = item.select_one("h4 > a")
            date_element = item.find("div", class_="news-release-date")

            if link_element and date_element:
                title = link_element.get_text(strip=True)
                relative_link = link_element.get("href")
                if not isinstance(relative_link, str):
                    continue
                link = urljoin(self.URL, relative_link)

                body = self._fetch_article_body(link)

                date_str = date_element.get_text(strip=True)
                try:
                    # Assuming format is MM/DD/YYYY
                    parsed_date = datetime.strptime(date_str, "%m/%d/%Y")
                except ValueError:
                    # If parsing fails, use the current time
                    parsed_date = datetime.now()

                article = {
                    "id": str(uuid.uuid4()),
                    "title": title,
                    "date": parsed_date.isoformat(),
                    "body": body,
                    "link": link,
                    "source": "SkyWest, Inc.",
                    "status": "new",
                }
                articles.append(article)

        return articles

    def parse(self, raw_data):
        pass
