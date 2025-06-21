"""News fetching agents."""

from .aviation_pages_reader import fetch_skywest_news
from .newsdata_agent import fetch_newsdata_news
from .groundnews_agent import fetch_groundnews
from .institutional_reader import fetch_institutional_news

__all__ = [
    "fetch_skywest_news",
    "fetch_newsdata_news",
    "fetch_groundnews",
    "fetch_institutional_news",
]

