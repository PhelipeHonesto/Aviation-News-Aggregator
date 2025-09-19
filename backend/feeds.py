"""
Loud Hawk v2 - RSS Feed Configuration
Curated list of aviation RSS feeds for aggregation
"""
from typing import Dict, List
from datetime import datetime
import feedparser
import requests
from bs4 import BeautifulSoup
import time
import logging

logger = logging.getLogger(__name__)

# Aviation RSS Feeds Configuration
AVIATION_FEEDS = {
    # Regulatory & Safety
    "FAA": {
        "url": "https://www.faa.gov/news/rss",
        "category": "Regulation",
        "weight": 10
    },
    "NTSB": {
        "url": "https://www.ntsb.gov/news/rss",
        "category": "Safety",
        "weight": 10
    },
    "EASA": {
        "url": "https://www.easa.europa.eu/news/rss",
        "category": "Regulation", 
        "weight": 10
    },
    "ICAO": {
        "url": "https://www.icao.int/Newsroom/rss",
        "category": "Regulation",
        "weight": 9
    },
    
    # Airlines
    "Alaska Airlines": {
        "url": "https://news.alaskaair.com/rss",
        "category": "Airlines",
        "weight": 7
    },
    "Southwest": {
        "url": "https://news.southwest.com/rss",
        "category": "Airlines", 
        "weight": 7
    },
    "American Airlines": {
        "url": "https://news.aa.com/rss",
        "category": "Airlines",
        "weight": 7
    },
    "United Airlines": {
        "url": "https://newsroom.united.com/rss",
        "category": "Airlines",
        "weight": 7
    },
    
    # OEMs
    "Boeing": {
        "url": "https://boeing.mediaroom.com/rss",
        "category": "OEMs",
        "weight": 8
    },
    "Airbus": {
        "url": "https://www.airbus.com/newsroom/rss",
        "category": "OEMs",
        "weight": 8
    },
    "Embraer": {
        "url": "https://embraer.com/news/rss",
        "category": "OEMs",
        "weight": 7
    },
    "Bombardier": {
        "url": "https://bombardier.com/news/rss",
        "category": "OEMs",
        "weight": 6
    },
    
    # Aviation Media
    "AVWeb": {
        "url": "https://www.avweb.com/avwebflash/feed/",
        "category": "Media",
        "weight": 6
    },
    "FlightGlobal": {
        "url": "https://www.flightglobal.com/rss",
        "category": "Media",
        "weight": 8
    },
    "AeroTime": {
        "url": "https://www.aerotime.aero/rss",
        "category": "Media",
        "weight": 5
    },
    
    # NASA & Research
    "NASA Aeronautics": {
        "url": "https://www.nasa.gov/aeronautics/rss",
        "category": "Research",
        "weight": 7
    },
    
    # eVTOL & Future Aviation
    "Joby Aviation": {
        "url": "https://www.jobyaviation.com/news/rss",
        "category": "eVTOL",
        "weight": 5
    },
    "Archer Aviation": {
        "url": "https://www.archer.com/rss",
        "category": "eVTOL",
        "weight": 5
    },
    "Lilium": {
        "url": "https://www.lilium.com/news/rss",
        "category": "eVTOL",
        "weight": 4
    },
    
    # Additional Airlines
    "Delta Air Lines": {
        "url": "https://news.delta.com/rss",
        "category": "Airlines",
        "weight": 7
    },
    "JetBlue Airways": {
        "url": "https://news.jetblue.com/rss",
        "category": "Airlines",
        "weight": 6
    },
    "Spirit Airlines": {
        "url": "https://corporate.spirit.com/news/rss",
        "category": "Airlines",
        "weight": 5
    },
    "Frontier Airlines": {
        "url": "https://news.flyfrontier.com/rss",
        "category": "Airlines",
        "weight": 5
    },
    
    # Additional OEMs
    "Gulfstream": {
        "url": "https://www.gulfstream.com/news/rss",
        "category": "OEMs",
        "weight": 6
    },
    "Cessna": {
        "url": "https://www.cessna.com/news/rss",
        "category": "OEMs",
        "weight": 6
    },
    "Piper": {
        "url": "https://www.piper.com/news/rss",
        "category": "OEMs",
        "weight": 5
    },
    
    # Aviation Media & Blogs
    "The Points Guy": {
        "url": "https://thepointsguy.com/feed/",
        "category": "Media",
        "weight": 6
    },
    "AirlineGeeks": {
        "url": "https://airlinegeeks.com/feed/",
        "category": "Media",
        "weight": 5
    },
    "Simple Flying": {
        "url": "https://simpleflying.com/feed/",
        "category": "Media",
        "weight": 6
    },
    "Airlines for America": {
        "url": "https://www.airlines.org/news/rss",
        "category": "Industry",
        "weight": 7
    },
    
    # Airports & Infrastructure
    "LAX": {
        "url": "https://www.flylax.com/news/rss",
        "category": "Infrastructure",
        "weight": 4
    },
    "JFK": {
        "url": "https://www.jfkairport.com/news/rss",
        "category": "Infrastructure",
        "weight": 4
    },
    
    # Aviation Organizations
    "AOPA": {
        "url": "https://www.aopa.org/news/rss",
        "category": "General Aviation",
        "weight": 6
    },
    "NBAA": {
        "url": "https://www.nbaa.org/news/rss",
        "category": "Business Aviation",
        "weight": 6
    }
}

def fetch_rss_feed(source: str, feed_config: Dict) -> List[Dict]:
    """Fetch and parse a single RSS feed"""
    articles = []
    
    try:
        logger.info(f"Fetching RSS feed: {source}")
        
        # Fetch feed with timeout
        response = requests.get(
            feed_config["url"], 
            timeout=10,
            headers={'User-Agent': 'Loud Hawk News Aggregator v2'}
        )
        response.raise_for_status()
        
        # Parse feed
        feed = feedparser.parse(response.content)
        
        if feed.bozo:
            logger.warning(f"RSS feed {source} has parsing issues: {feed.bozo_exception}")
        
        # Extract articles
        for entry in feed.entries[:20]:  # Limit to 20 most recent
            try:
                # Parse published date
                pub_date = datetime.utcnow()
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_date = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    pub_date = datetime(*entry.updated_parsed[:6])
                
                article = {
                    "source": source,
                    "title": entry.get("title", "").strip(),
                    "url": entry.get("link", ""),
                    "published_at": pub_date,
                    "summary": entry.get("summary", "").strip(),
                    "category": feed_config["category"],
                    "weight": feed_config["weight"]
                }
                
                # Only add if we have essential data
                if article["title"] and article["url"]:
                    articles.append(article)
                    
            except Exception as e:
                logger.error(f"Error parsing entry from {source}: {e}")
                continue
        
        logger.info(f"Successfully fetched {len(articles)} articles from {source}")
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching RSS feed {source}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error fetching {source}: {e}")
    
    return articles

def fetch_all_feeds() -> List[Dict]:
    """Fetch all configured RSS feeds"""
    all_articles = []
    
    for source, config in AVIATION_FEEDS.items():
        try:
            articles = fetch_rss_feed(source, config)
            all_articles.extend(articles)
            
            # Be polite to servers
            time.sleep(0.5)
            
        except Exception as e:
            logger.error(f"Failed to fetch feed {source}: {e}")
            continue
    
    logger.info(f"Total articles fetched: {len(all_articles)}")
    return all_articles
