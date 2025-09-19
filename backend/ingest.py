"""
Loud Hawk v2 - Advanced News Ingestion System

Professional-grade news ingestion with:
- Multi-strategy source adapters
- XML recovery for malformed feeds
- Dynamic scheduling integration
- Authority-weighted ranking
- Circuit breaker reliability
"""
import yaml
import time
import httpx
import feedparser
import bs4
import urllib.parse as U
import logging
import hashlib
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime
import re

from models import NewsArticle
from database import save_articles
from source_health import fetch_with_reliability, SourceReliability, record_source_bozo
from dynamic_scheduler import dynamic_scheduler
from ranking_system import ranking_system
from youtube_adapter import youtube_adapter
from database import engine

logger = logging.getLogger(__name__)

@dataclass
class Source:
    name: str
    category: str
    weight: int
    kind: str
    enabled: bool = True
    home: Optional[str] = None
    url: Optional[str] = None
    selectors: Optional[Dict] = None
    discover: bool = False
    adapter_strategy: Optional[str] = None
    notes: Optional[str] = None
    region: Optional[str] = None

def load_sources(path: str = "trusted_sources.yaml") -> List[Source]:
    """Load sources from YAML configuration"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        return [Source(**row) for row in cfg]
    except Exception as e:
        logger.error(f"Error loading sources from {path}: {e}")
        return []

# HTTP client with realistic headers to avoid 403 blocks
session = httpx.Client(
    timeout=30,
    headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept": "application/rss+xml, application/atom+xml, application/xml;q=0.9, text/xml;q=0.8, text/html;q=0.7, */*;q=0.6",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Cache-Control": "max-age=0",
    },
    follow_redirects=True,
    http2=True
)

def discover_feeds(home_url: str) -> List[str]:
    """Auto-discover RSS/Atom feeds from a homepage"""
    try:
        response = session.get(home_url)
        response.raise_for_status()
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        
        feeds = []
        
        # Look for RSS/Atom link tags
        for link in soup.find_all("link", type=["application/rss+xml", "application/atom+xml"]):
            href = link.get("href")
            if href:
                feeds.append(U.urljoin(home_url, href))
        
        # Look for common feed URLs
        base_url = U.urlparse(home_url)
        common_paths = [
            "/feed", "/rss", "/rss.xml", "/feed.xml", "/atom.xml",
            "/news/rss", "/news/feed", "/press/rss", "/press/feed",
            "/blog/rss", "/blog/feed", "/media/rss", "/media/feed"
        ]
        
        for path in common_paths:
            feed_url = f"{base_url.scheme}://{base_url.netloc}{path}"
            try:
                test_response = session.head(feed_url, timeout=5)
                if test_response.status_code == 200:
                    feeds.append(feed_url)
            except:
                continue
        
        # Look for sitemap references
        sitemap_urls = []
        for link in soup.find_all("link", rel="alternate", type="application/xml"):
            href = link.get("href")
            if href and "sitemap" in href.lower():
                sitemap_urls.append(U.urljoin(home_url, href))
        
        # Check sitemaps for news feeds
        for sitemap_url in sitemap_urls:
            try:
                sitemap_response = session.get(sitemap_url, timeout=10)
                if sitemap_response.status_code == 200:
                    sitemap_soup = bs4.BeautifulSoup(sitemap_response.text, "xml")
                    for loc in sitemap_soup.find_all("loc"):
                        url = loc.get_text()
                        if any(feed_type in url.lower() for feed_type in ["rss", "feed", "atom"]):
                            feeds.append(url)
            except:
                continue
        
        logger.info(f"Discovered {len(feeds)} potential feeds for {home_url}")
        return list(set(feeds))  # Remove duplicates
        
    except Exception as e:
        logger.error(f"Error discovering feeds for {home_url}: {e}")
        return []

def fetch_rss(src: Source) -> List[Dict]:
    """Fetch articles from RSS/Atom feed with reliability tracking"""
    try:
        if not src.enabled:
            logger.info(f"Source {src.name} is disabled, skipping")
            return []
            
        url = src.url or src.home
        if not url:
            logger.warning(f"No URL found for source {src.name}")
            return []
        
        # Try auto-discovery if enabled and no direct URL
        if src.discover and src.home and not src.url:
            discovered_feeds = discover_feeds(src.home)
            for feed_url in discovered_feeds:
                if any(ext in feed_url.lower() for ext in [".xml", "/feed", "/rss", "/atom"]):
                    url = feed_url
                    logger.info(f"Using discovered feed: {url}")
                    break
        
        logger.info(f"Fetching RSS feed: {src.name} from {url}")
        
        # Use reliability-tracked fetch
        content, error = fetch_with_reliability(src.name, url)
        if error:
            logger.warning(f"Failed to fetch {src.name}: {error}")
            return []
        
        if not content:
            logger.warning(f"No content returned for {src.name}")
            return []
        
        # Parse with improved options for better XML handling
        feed = feedparser.parse(content, resolve_relative_uris=True, sanitize_html=True)
        
        # Handle bozo (malformed XML) feeds
        if feed.bozo:
            bozo_error = f"Malformed XML: {feed.bozo_exception}"
            logger.warning(f"RSS feed {src.name} has parsing issues: {bozo_error}")
            record_source_bozo(src.name, bozo_error)
            
            # Try to recover malformed XML with lxml
            try:
                from lxml import etree
                # Attempt to recover the XML
                parser = etree.XMLParser(recover=True)
                tree = etree.fromstring(content.encode(), parser)
                recovered_content = etree.tostring(tree, encoding='unicode')
                feed = feedparser.parse(recovered_content, resolve_relative_uris=True, sanitize_html=True)
                logger.info(f"Successfully recovered XML for {src.name}")
            except Exception as recovery_error:
                logger.warning(f"XML recovery failed for {src.name}: {recovery_error}")
        
        items = []
        for entry in feed.entries[:50]:  # Limit to 50 items per feed
            link = entry.get("link", "").strip()
            title = entry.get("title", "").strip()
            
            if not link or not title:
                continue
            
            # Parse published date with more formats
            published_at = None
            date_fields = ["published", "updated", "created", "pubDate"]
            date_formats = [
                "%a, %d %b %Y %H:%M:%S %z",
                "%Y-%m-%dT%H:%M:%S%z",
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d"
            ]
            
            for date_field in date_fields:
                if hasattr(entry, date_field):
                    date_str = entry[date_field]
                    for fmt in date_formats:
                        try:
                            published_at = datetime.strptime(date_str, fmt)
                            break
                        except:
                            continue
                    if published_at:
                        break
            
            # Fallback to feed's lastBuildDate if entry date parsing fails
            if not published_at and hasattr(feed.feed, 'lastBuildDate'):
                try:
                    published_at = datetime.strptime(
                        feed.feed.lastBuildDate, "%a, %d %b %Y %H:%M:%S %z"
                    )
                except:
                    pass
            
            if not published_at:
                published_at = datetime.utcnow()
            
            # Clean summary with better HTML stripping
            summary = ""
            for summary_field in ["summary", "description", "content"]:
                if hasattr(entry, summary_field):
                    summary = entry[summary_field]
                    # Remove HTML tags and clean whitespace
                    summary = re.sub(r'<[^>]+>', '', summary).strip()
                    summary = re.sub(r'\s+', ' ', summary)  # Normalize whitespace
                    break
            
            # Normalize URL and create canonical URL
            full_url = U.urljoin(url, link)
            canonical_url = NewsArticle.normalize_url(full_url)
            
            # Create content hash for deduplication using new method
            content_hash = NewsArticle.create_hash(title, canonical_url, published_at)
            
            items.append({
                "source": src.name,
                "title": title,
                "url": full_url,
                "canonical_url": canonical_url,
                "published_at": published_at,
                "summary": summary,
                "content_hash": content_hash,
                "weight": src.weight
            })
        
        logger.info(f"Successfully fetched {len(items)} articles from {src.name}")
        return items
        
    except Exception as e:
        logger.error(f"Error fetching RSS feed {src.name}: {e}")
        return []

def fetch_html(src: Source) -> List[Dict]:
    """Fetch articles from HTML page using CSS selectors with reliability tracking"""
    try:
        if not src.enabled:
            logger.info(f"Source {src.name} is disabled, skipping")
            return []
            
        if not src.home or not src.selectors:
            logger.warning(f"HTML source {src.name} missing home URL or selectors")
            return []
        
        logger.info(f"Fetching HTML content: {src.name} from {src.home}")
        
        # Use reliability-tracked fetch
        content, error = fetch_with_reliability(src.name, src.home)
        if error:
            logger.warning(f"Failed to fetch {src.name}: {error}")
            return []
        
        if not content:
            logger.warning(f"No content returned for {src.name}")
            return []
        
        soup = bs4.BeautifulSoup(content, "html.parser")
        sel = src.selectors
        items = []
        
        for node in soup.select(sel.get("item", "article, .post, .press-item"))[:30]:
            try:
                # Extract title
                title_el = node.select_one(sel.get("title", "h1 a, h2 a, .title a"))
                title = title_el.get_text(strip=True) if title_el else ""
                
                # Extract link
                link_el = node.select_one(sel.get("link", "h1 a, h2 a, .title a"))
                href = link_el.get("href") if link_el else None
                link = U.urljoin(src.home, href) if href else None
                
                # Extract date
                date_el = node.select_one(sel.get("date", "time, .date"))
                dt_str = ""
                if date_el:
                    if date_el.has_attr("datetime"):
                        dt_str = date_el.get("datetime")
                    else:
                        dt_str = date_el.get_text(strip=True)
                
                # Parse date
                published_at = None
                if dt_str:
                    for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"]:
                        try:
                            published_at = datetime.strptime(dt_str, fmt)
                            break
                        except:
                            continue
                
                if not published_at:
                    published_at = datetime.utcnow()
                
                # Extract summary
                sum_el = node.select_one(sel.get("summary", ".excerpt, .summary, p"))
                summary = sum_el.get_text(strip=True) if sum_el else ""
                
                if title and link:
                    # Normalize URL and create canonical URL
                    canonical_url = NewsArticle.normalize_url(link)
                    
                    # Create content hash for deduplication using new method
                    content_hash = NewsArticle.create_hash(title, canonical_url, published_at)
                    
                    items.append({
                        "source": src.name,
                        "title": title,
                        "url": link,
                        "canonical_url": canonical_url,
                        "published_at": published_at,
                        "summary": summary,
                        "content_hash": content_hash,
                        "weight": src.weight
                    })
                    
            except Exception as e:
                logger.warning(f"Error parsing HTML item in {src.name}: {e}")
                continue
        
        # Be polite to servers
        time.sleep(0.2)
        
        logger.info(f"Successfully fetched {len(items)} articles from {src.name}")
        return items
        
    except Exception as e:
        logger.error(f"Error fetching HTML content {src.name}: {e}")
        return []

def harvest_all_sources() -> List[NewsArticle]:
    """Harvest articles from all enabled sources"""
    sources = load_sources()
    enabled_sources = [src for src in sources if src.enabled]
    all_articles = []
    
    logger.info(f"Starting harvest of {len(enabled_sources)} enabled sources (total: {len(sources)})")
    
    for src in enabled_sources:
        try:
            if src.kind == "rss":
                items = fetch_rss(src)
            elif src.kind == "html":
                items = fetch_html(src)
            else:
                logger.warning(f"Unknown source kind '{src.kind}' for {src.name}")
                continue
            
            # Convert to NewsArticle objects
            for item in items:
                article = NewsArticle(
                    source=item["source"],
                    title=item["title"],
                    url=item["url"],
                    canonical_url=item["canonical_url"],
                    published_at=item["published_at"],
                    summary=item["summary"],
                    content_hash=item["content_hash"]
                )
                all_articles.append(article)
                
        except Exception as e:
            logger.error(f"Error processing source {src.name}: {e}")
            continue
    
    logger.info(f"Harvested {len(all_articles)} total articles from {len(enabled_sources)} sources")
    return all_articles

def run_harvest():
    """Run the complete harvest process and save to database"""
    try:
        articles = harvest_all_sources()
        if articles:
            saved_count = save_articles(articles)
            logger.info(f"Harvest completed: {saved_count} new articles saved")
            return saved_count
        else:
            logger.warning("No articles harvested")
            return 0
    except Exception as e:
        logger.error(f"Error during harvest: {e}")
        return 0

def harvest_youtube_sources():
    """Harvest aviation content from YouTube channels"""
    try:
        videos = youtube_adapter.fetch_all_channels(hours_back=24)
        if videos:
            logger.info(f"Harvested {len(videos)} YouTube videos")
            
            # Convert to NewsArticle objects
            articles = []
            for video in videos:
                article = NewsArticle(
                    source=video["source"],
                    title=video["title"],
                    url=video["url"],
                    canonical_url=video["canonical_url"],
                    published_at=video["published_at"],
                    summary=video.get("summary", ""),
                    content_hash=video["content_hash"]
                )
                articles.append(article)
            
            return articles
    except Exception as e:
        logger.error(f"Error harvesting YouTube sources: {e}")
    
    return []
