import uuid
from datetime import datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


def fetch_skywest_news():
    """
    Scrapes the SkyWest, Inc. press release website for news.
    """
    URL = "https://inc.skywest.com/news-and-events/press-releases/"
    try:
        response = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {URL}: {e}")
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
            link = urljoin(URL, relative_link)

            body = ""

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
