"""
Loud Hawk v2 - Source Adapter System
Per-source strategies for different types of news sources
"""
import logging
from enum import Enum
from typing import List, Dict, Optional
from dataclasses import dataclass
import httpx
import feedparser
import bs4
import urllib.parse as U
from datetime import datetime

logger = logging.getLogger(__name__)

class SourceStrategy(Enum):
    """Different strategies for fetching from sources"""
    RSS_NATIVE = "rss_native"  # Direct RSS/Atom feed
    RSS_REDIRECTED = "rss_redirected"  # Follow redirects to find RSS
    RSS_NATIVE_OR_TIDY_XML = "rss_native_or_tidy_xml"  # RSS with XML recovery
    RSS_REDIRECTED_OR_TIDY_XML = "rss_redirected_or_tidy_xml"  # RSS redirect with XML recovery
    SITEMAP_OR_RSS_REDIRECTED = "sitemap_or_rss_redirected"  # Sitemap or RSS discovery
    SITEMAP_NEWS = "sitemap_news"  # Use sitemap for news
    HTML_SCRAPE = "html_scrape"  # HTML scraping with CSS selectors
    HTML_SCRAPE_WHITELIST = "html_scrape_whitelist"  # HTML scraping with content filtering
    HTML_TIDY_XML = "html_tidy_xml"  # HTML with XML recovery
    HTML_SCRAPE_OR_JSON = "html_scrape_or_json"  # HTML scraping or JSON API
    RSS_OR_HTML_SCRAPE = "rss_or_html_scrape"  # Try RSS first, fallback to HTML
    RSS_NATIVE_OR_JSON = "rss_native_or_json"  # RSS or JSON API
    JSON_API = "json_api"  # WordPress/API endpoints
    YOUTUBE_API = "youtube_api"  # YouTube channel API

@dataclass
class SourceAdapter:
    """Adapter configuration for a source"""
    name: str
    strategy: SourceStrategy
    base_url: str
    feed_url: Optional[str] = None
    selectors: Optional[Dict] = None
    api_endpoint: Optional[str] = None
    headers: Optional[Dict] = None

class SourceAdapterManager:
    """Manages source-specific adapters and strategies"""
    
    def __init__(self):
        self.adapters = {}
        self._init_default_adapters()
    
    def _init_default_adapters(self):
        """Initialize default adapters for common aviation sources"""
        
        # Regulators - usually have good RSS
        self.adapters.update({
            "FAA Newsroom": SourceAdapter(
                name="FAA Newsroom",
                strategy=SourceStrategy.RSS_REDIRECTED,
                base_url="https://www.faa.gov/newsroom",
                headers={"Referer": "https://www.faa.gov/"}
            ),
            "NTSB Reports": SourceAdapter(
                name="NTSB Reports", 
                strategy=SourceStrategy.RSS_NATIVE,
                base_url="https://www.ntsb.gov",
                feed_url="https://www.ntsb.gov/news/rss.xml"
            ),
            "EASA Updates": SourceAdapter(
                name="EASA Updates",
                strategy=SourceStrategy.RSS_NATIVE,
                base_url="https://www.easa.europa.eu",
                feed_url="https://www.easa.europa.eu/rss.xml"
            ),
            "ICAO Newsroom": SourceAdapter(
                name="ICAO Newsroom",
                strategy=SourceStrategy.RSS_NATIVE,
                base_url="https://www.icao.int",
                feed_url="https://www.icao.int/rss.xml"
            ),
        })
        
        # OEMs - mixed strategies
        self.adapters.update({
            "Airbus Newsroom": SourceAdapter(
                name="Airbus Newsroom",
                strategy=SourceStrategy.RSS_REDIRECTED,
                base_url="https://www.airbus.com/en/newsroom",
                headers={"Referer": "https://www.airbus.com/"}
            ),
            "Boeing News": SourceAdapter(
                name="Boeing News",
                strategy=SourceStrategy.RSS_NATIVE,
                base_url="https://boeing.mediaroom.com",
                feed_url="https://boeing.mediaroom.com/rss"
            ),
            "Embraer Media": SourceAdapter(
                name="Embraer Media",
                strategy=SourceStrategy.SITEMAP_NEWS,
                base_url="https://embraer.com/global/en/newsroom",
                selectors={
                    "item": ".news-item",
                    "title": "h3 a",
                    "link": "h3 a",
                    "date": ".date",
                    "summary": ".excerpt"
                }
            ),
            "Bombardier News": SourceAdapter(
                name="Bombardier News",
                strategy=SourceStrategy.RSS_NATIVE,
                base_url="https://bombardier.com/en/news",
                feed_url="https://bombardier.com/en/rss.xml"
            ),
        })
        
        # Airlines - some have good RSS, others need scraping
        self.adapters.update({
            "Delta News Hub": SourceAdapter(
                name="Delta News Hub",
                strategy=SourceStrategy.RSS_NATIVE,
                base_url="https://news.delta.com",
                feed_url="https://news.delta.com/delta-news-hub.xml"
            ),
            "Alaska Airlines": SourceAdapter(
                name="Alaska Airlines",
                strategy=SourceStrategy.RSS_REDIRECTED,
                base_url="https://news.alaskaair.com",
                headers={"Referer": "https://www.alaskaair.com/"}
            ),
            "Southwest Airlines": SourceAdapter(
                name="Southwest Airlines",
                strategy=SourceStrategy.RSS_NATIVE,
                base_url="https://swamedia.com",
                feed_url="https://swamedia.com/rss.xml"
            ),
        })
        
        # Media sources - usually WordPress with JSON API
        self.adapters.update({
            "AVWeb": SourceAdapter(
                name="AVWeb",
                strategy=SourceStrategy.JSON_API,
                base_url="https://www.avweb.com",
                api_endpoint="https://www.avweb.com/wp-json/wp/v2/posts?per_page=20&_fields=link,date,title,excerpt"
            ),
            "FlightGlobal": SourceAdapter(
                name="FlightGlobal",
                strategy=SourceStrategy.RSS_NATIVE,
                base_url="https://www.flightglobal.com",
                feed_url="https://www.flightglobal.com/rss"
            ),
        })
    
    def get_adapter(self, source_name: str) -> Optional[SourceAdapter]:
        """Get adapter for a source"""
        return self.adapters.get(source_name)
    
    def fetch_with_adapter(self, adapter: SourceAdapter) -> List[Dict]:
        """Fetch articles using the appropriate adapter strategy"""
        if adapter.strategy == SourceStrategy.RSS_NATIVE:
            return self._fetch_rss_native(adapter)
        elif adapter.strategy == SourceStrategy.RSS_REDIRECTED:
            return self._fetch_rss_redirected(adapter)
        elif adapter.strategy == SourceStrategy.RSS_NATIVE_OR_TIDY_XML:
            return self._fetch_rss_with_xml_recovery(adapter)
        elif adapter.strategy == SourceStrategy.RSS_REDIRECTED_OR_TIDY_XML:
            return self._fetch_rss_redirected_with_xml_recovery(adapter)
        elif adapter.strategy == SourceStrategy.SITEMAP_OR_RSS_REDIRECTED:
            return self._fetch_sitemap_or_rss_redirected(adapter)
        elif adapter.strategy == SourceStrategy.SITEMAP_NEWS:
            return self._fetch_sitemap_news(adapter)
        elif adapter.strategy == SourceStrategy.HTML_SCRAPE:
            return self._fetch_html_scrape(adapter)
        elif adapter.strategy == SourceStrategy.HTML_SCRAPE_WHITELIST:
            return self._fetch_html_scrape_whitelist(adapter)
        elif adapter.strategy == SourceStrategy.HTML_TIDY_XML:
            return self._fetch_html_with_xml_recovery(adapter)
        elif adapter.strategy == SourceStrategy.HTML_SCRAPE_OR_JSON:
            return self._fetch_html_or_json(adapter)
        elif adapter.strategy == SourceStrategy.RSS_OR_HTML_SCRAPE:
            return self._fetch_rss_or_html(adapter)
        elif adapter.strategy == SourceStrategy.RSS_NATIVE_OR_JSON:
            return self._fetch_rss_or_json(adapter)
        elif adapter.strategy == SourceStrategy.JSON_API:
            return self._fetch_json_api(adapter)
        elif adapter.strategy == SourceStrategy.YOUTUBE_API:
            return self._fetch_youtube_api(adapter)
        else:
            logger.warning(f"Unknown strategy {adapter.strategy} for {adapter.name}")
            return []
    
    def _fetch_rss_native(self, adapter: SourceAdapter) -> List[Dict]:
        """Fetch from direct RSS/Atom feed"""
        try:
            headers = adapter.headers or {}
            with httpx.Client(headers=headers, timeout=30) as client:
                response = client.get(adapter.feed_url)
                response.raise_for_status()
                
                feed = feedparser.parse(response.text, resolve_relative_uris=True, sanitize_html=True)
                
                items = []
                for entry in feed.entries[:50]:
                    items.append(self._parse_feed_entry(entry, adapter))
                
                logger.info(f"RSS_NATIVE: Fetched {len(items)} items from {adapter.name}")
                return items
                
        except Exception as e:
            logger.error(f"RSS_NATIVE failed for {adapter.name}: {e}")
            return []
    
    def _fetch_rss_redirected(self, adapter: SourceAdapter) -> List[Dict]:
        """Fetch RSS by first visiting homepage and following RSS links"""
        try:
            headers = adapter.headers or {}
            with httpx.Client(headers=headers, timeout=30) as client:
                # First, get the homepage to find RSS links
                response = client.get(adapter.base_url)
                response.raise_for_status()
                
                soup = bs4.BeautifulSoup(response.text, "html.parser")
                feed_url = None
                
                # Look for RSS/Atom link tags
                for link in soup.find_all("link", type=["application/rss+xml", "application/atom+xml"]):
                    href = link.get("href")
                    if href:
                        feed_url = U.urljoin(adapter.base_url, href)
                        break
                
                if not feed_url:
                    # Try common feed paths
                    base_url = U.urlparse(adapter.base_url)
                    common_paths = ["/feed", "/rss", "/rss.xml", "/feed.xml", "/atom.xml"]
                    for path in common_paths:
                        test_url = f"{base_url.scheme}://{base_url.netloc}{path}"
                        try:
                            test_response = client.head(test_url, timeout=5)
                            if test_response.status_code == 200:
                                feed_url = test_url
                                break
                        except:
                            continue
                
                if feed_url:
                    # Fetch the actual RSS feed
                    feed_response = client.get(feed_url)
                    feed_response.raise_for_status()
                    
                    feed = feedparser.parse(feed_response.text, resolve_relative_uris=True, sanitize_html=True)
                    
                    items = []
                    for entry in feed.entries[:50]:
                        items.append(self._parse_feed_entry(entry, adapter))
                    
                    logger.info(f"RSS_REDIRECTED: Fetched {len(items)} items from {adapter.name}")
                    return items
                else:
                    logger.warning(f"RSS_REDIRECTED: No RSS feed found for {adapter.name}")
                    return []
                    
        except Exception as e:
            logger.error(f"RSS_REDIRECTED failed for {adapter.name}: {e}")
            return []
    
    def _fetch_sitemap_news(self, adapter: SourceAdapter) -> List[Dict]:
        """Fetch from sitemap or HTML scraping"""
        try:
            headers = adapter.headers or {}
            with httpx.Client(headers=headers, timeout=30) as client:
                response = client.get(adapter.base_url)
                response.raise_for_status()
                
                soup = bs4.BeautifulSoup(response.text, "html.parser")
                items = []
                
                if adapter.selectors:
                    # Use provided selectors for HTML scraping
                    for node in soup.select(adapter.selectors.get("item", "article"))[:30]:
                        try:
                            title_el = node.select_one(adapter.selectors.get("title", "h1, h2, h3"))
                            title = title_el.get_text(strip=True) if title_el else ""
                            
                            link_el = node.select_one(adapter.selectors.get("link", "a"))
                            href = link_el.get("href") if link_el else None
                            link = U.urljoin(adapter.base_url, href) if href else None
                            
                            if title and link:
                                items.append({
                                    "source": adapter.name,
                                    "title": title,
                                    "url": link,
                                    "published_at": datetime.utcnow(),
                                    "summary": "",
                                    "canonical_url": link,
                                    "content_hash": f"{title.lower()}|{adapter.name.lower()}|{datetime.utcnow().date()}"
                                })
                        except Exception as e:
                            logger.warning(f"Error parsing item in {adapter.name}: {e}")
                            continue
                
                logger.info(f"SITEMAP_NEWS: Fetched {len(items)} items from {adapter.name}")
                return items
                
        except Exception as e:
            logger.error(f"SITEMAP_NEWS failed for {adapter.name}: {e}")
            return []
    
    def _fetch_html_scrape(self, adapter: SourceAdapter) -> List[Dict]:
        """Fetch by scraping HTML with CSS selectors"""
        return self._fetch_sitemap_news(adapter)  # Same logic for now
    
    def _fetch_json_api(self, adapter: SourceAdapter) -> List[Dict]:
        """Fetch from JSON API (WordPress, etc.)"""
        try:
            headers = adapter.headers or {}
            with httpx.Client(headers=headers, timeout=30) as client:
                response = client.get(adapter.api_endpoint)
                response.raise_for_status()
                
                data = response.json()
                items = []
                
                for post in data[:20]:  # Limit to 20 posts
                    try:
                        title = post.get("title", {}).get("rendered", "")
                        link = post.get("link", "")
                        date_str = post.get("date", "")
                        excerpt = post.get("excerpt", {}).get("rendered", "")
                        
                        # Parse date
                        published_at = datetime.utcnow()
                        if date_str:
                            try:
                                published_at = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                            except:
                                pass
                        
                        if title and link:
                            # Clean HTML from excerpt
                            excerpt = bs4.BeautifulSoup(excerpt, "html.parser").get_text(strip=True)
                            
                            items.append({
                                "source": adapter.name,
                                "title": title,
                                "url": link,
                                "published_at": published_at,
                                "summary": excerpt,
                                "canonical_url": link,
                                "content_hash": f"{title.lower()}|{adapter.name.lower()}|{published_at.date()}"
                            })
                    except Exception as e:
                        logger.warning(f"Error parsing JSON post in {adapter.name}: {e}")
                        continue
                
                logger.info(f"JSON_API: Fetched {len(items)} items from {adapter.name}")
                return items
                
        except Exception as e:
            logger.error(f"JSON_API failed for {adapter.name}: {e}")
            return []
    
    def _parse_feed_entry(self, entry, adapter: SourceAdapter) -> Dict:
        """Parse a feed entry into standardized format"""
        link = entry.get("link", "").strip()
        title = entry.get("title", "").strip()
        
        # Parse published date
        published_at = datetime.utcnow()
        for date_field in ["published", "updated", "created", "pubDate"]:
            if hasattr(entry, date_field):
                try:
                    date_str = entry[date_field]
                    # Try common formats
                    for fmt in ["%a, %d %b %Y %H:%M:%S %z", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ"]:
                        try:
                            published_at = datetime.strptime(date_str, fmt)
                            break
                        except:
                            continue
                    if published_at != datetime.utcnow():
                        break
                except:
                    continue
        
        # Clean summary
        summary = ""
        for summary_field in ["summary", "description", "content"]:
            if hasattr(entry, summary_field):
                summary = entry[summary_field]
                summary = bs4.BeautifulSoup(summary, "html.parser").get_text(strip=True)
                break
        
        # Normalize URL
        full_url = U.urljoin(adapter.base_url, link)
        canonical_url = full_url  # Could add normalization here
        
        return {
            "source": adapter.name,
            "title": title,
            "url": full_url,
            "canonical_url": canonical_url,
            "published_at": published_at,
            "summary": summary,
            "content_hash": f"{title.lower()}|{adapter.name.lower()}|{published_at.date()}"
        }

    def _fetch_rss_with_xml_recovery(self, adapter: SourceAdapter) -> List[Dict]:
        """Fetch RSS with XML recovery for malformed feeds"""
        try:
            items = self._fetch_rss_native(adapter)
            if not items:
                # Try XML recovery
                return self._fetch_rss_with_recovery(adapter)
            return items
        except Exception as e:
            logger.error(f"RSS with XML recovery failed for {adapter.name}: {e}")
            return []

    def _fetch_rss_redirected_with_xml_recovery(self, adapter: SourceAdapter) -> List[Dict]:
        """Fetch RSS redirected with XML recovery"""
        try:
            items = self._fetch_rss_redirected(adapter)
            if not items:
                # Try XML recovery
                return self._fetch_rss_with_recovery(adapter)
            return items
        except Exception as e:
            logger.error(f"RSS redirected with XML recovery failed for {adapter.name}: {e}")
            return []

    def _fetch_rss_with_recovery(self, adapter: SourceAdapter) -> List[Dict]:
        """Fetch RSS with XML recovery using lxml"""
        try:
            headers = adapter.headers or {}
            with httpx.Client(headers=headers, timeout=30) as client:
                response = client.get(adapter.feed_url)
                response.raise_for_status()
                
                # Try XML recovery
                try:
                    from lxml import etree
                    parser = etree.XMLParser(recover=True)
                    tree = etree.fromstring(response.text.encode(), parser)
                    recovered_content = etree.tostring(tree, encoding='unicode')
                    feed = feedparser.parse(recovered_content, resolve_relative_uris=True, sanitize_html=True)
                except:
                    feed = feedparser.parse(response.text, resolve_relative_uris=True, sanitize_html=True)
                
                items = []
                for entry in feed.entries[:50]:
                    items.append(self._parse_feed_entry(entry, adapter))
                
                logger.info(f"RSS with recovery: Fetched {len(items)} items from {adapter.name}")
                return items
                
        except Exception as e:
            logger.error(f"RSS with recovery failed for {adapter.name}: {e}")
            return []

    def _fetch_sitemap_or_rss_redirected(self, adapter: SourceAdapter) -> List[Dict]:
        """Try RSS first, fallback to sitemap"""
        try:
            items = self._fetch_rss_redirected(adapter)
            if items:
                return items
            
            # Fallback to sitemap
            return self._fetch_sitemap_news(adapter)
        except Exception as e:
            logger.error(f"Sitemap or RSS redirected failed for {adapter.name}: {e}")
            return []

    def _fetch_html_scrape_whitelist(self, adapter: SourceAdapter) -> List[Dict]:
        """HTML scraping with content whitelisting"""
        items = self._fetch_html_scrape(adapter)
        # Filter items based on content keywords
        filtered_items = []
        for item in items:
            title_lower = item.get("title", "").lower()
            summary_lower = item.get("summary", "").lower()
            
            # Whitelist keywords for aviation content
            aviation_keywords = [
                "aviation", "aircraft", "airline", "flight", "airport", "pilot",
                "aircraft", "boeing", "airbus", "embraer", "safety", "faa",
                "ntsb", "easa", "icao", "air traffic", "airspace", "route"
            ]
            
            if any(keyword in title_lower or keyword in summary_lower for keyword in aviation_keywords):
                filtered_items.append(item)
        
        logger.info(f"HTML scrape whitelist: Filtered {len(items)} to {len(filtered_items)} items from {adapter.name}")
        return filtered_items

    def _fetch_html_with_xml_recovery(self, adapter: SourceAdapter) -> List[Dict]:
        """HTML scraping with XML recovery"""
        return self._fetch_html_scrape_whitelist(adapter)  # Same for now

    def _fetch_html_or_json(self, adapter: SourceAdapter) -> List[Dict]:
        """Try HTML scraping first, fallback to JSON API"""
        try:
            items = self._fetch_html_scrape(adapter)
            if items:
                return items
            
            # Fallback to JSON API
            return self._fetch_json_api(adapter)
        except Exception as e:
            logger.error(f"HTML or JSON failed for {adapter.name}: {e}")
            return []

    def _fetch_rss_or_html(self, adapter: SourceAdapter) -> List[Dict]:
        """Try RSS first, fallback to HTML scraping"""
        try:
            items = self._fetch_rss_native(adapter)
            if items:
                return items
            
            # Fallback to HTML scraping
            return self._fetch_html_scrape(adapter)
        except Exception as e:
            logger.error(f"RSS or HTML failed for {adapter.name}: {e}")
            return []

    def _fetch_rss_or_json(self, adapter: SourceAdapter) -> List[Dict]:
        """Try RSS first, fallback to JSON API"""
        try:
            items = self._fetch_rss_native(adapter)
            if items:
                return items
            
            # Fallback to JSON API
            return self._fetch_json_api(adapter)
        except Exception as e:
            logger.error(f"RSS or JSON failed for {adapter.name}: {e}")
            return []

    def _fetch_youtube_api(self, adapter: SourceAdapter) -> List[Dict]:
        """Fetch from YouTube channel API (placeholder)"""
        # This would require YouTube API key and implementation
        logger.warning(f"YouTube API not implemented for {adapter.name}")
        return []

# Global adapter manager instance
adapter_manager = SourceAdapterManager()
