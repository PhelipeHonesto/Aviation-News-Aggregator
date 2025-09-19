"""
YouTube Adapter for Loud Hawk v2
Fetches aviation-related content from YouTube channels
"""

import logging
import httpx
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
import re

logger = logging.getLogger(__name__)

@dataclass
class YouTubeChannel:
    """YouTube channel configuration"""
    name: str
    channel_id: str
    category: str
    priority: int
    enabled: bool = True

class YouTubeAdapter:
    """Adapter for fetching aviation content from YouTube channels"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/youtube/v3"
        
        # Aviation channels configuration
        self.channels = [
            YouTubeChannel(
                name="Mentour Pilot",
                channel_id="UCwpH0sw9f0Zqec6aOesuUdg",
                category="CREATOR",
                priority=8
            ),
            YouTubeChannel(
                name="DJ's Aviation",
                channel_id="UCqQwY2g4FQcdMg4RijlVhug", 
                category="CREATOR",
                priority=7
            ),
            YouTubeChannel(
                name="FAA Safety Briefing",
                channel_id="UC8mA0tQVaHjb4oo4OtM4pSg",
                category="SAFETY",
                priority=9
            ),
            YouTubeChannel(
                name="Captain Joe",
                channel_id="UCPxH3xiedPUSyMWCd4AeJOA",
                category="CREATOR",
                priority=6
            ),
            YouTubeChannel(
                name="74 Gear",
                channel_id="UCqQwY2g4FQcdMg4RijlVhug",
                category="CREATOR", 
                priority=6
            ),
            YouTubeChannel(
                name="FlightChops",
                channel_id="UCgq2Q5u5dIhD4I2d2b2b2b2",
                category="CREATOR",
                priority=5
            )
        ]
        
        # Aviation keywords for content filtering
        self.aviation_keywords = [
            "aviation", "aircraft", "airline", "flight", "pilot", "airport",
            "boeing", "airbus", "embraer", "safety", "faa", "ntsb", "easa",
            "air traffic", "airspace", "route", "aviation safety", "flight training",
            "cockpit", "aircraft accident", "incident", "aviation news"
        ]
        
    def fetch_channel_videos(self, channel: YouTubeChannel, hours_back: int = 24) -> List[Dict]:
        """Fetch recent videos from a YouTube channel"""
        if not self.api_key:
            logger.warning("YouTube API key not configured, skipping YouTube content")
            return []
            
        try:
            # Calculate publishedAfter timestamp
            published_after = (datetime.utcnow() - timedelta(hours=hours_back)).isoformat() + "Z"
            
            # Search for recent videos from channel
            url = f"{self.base_url}/search"
            params = {
                "part": "snippet",
                "channelId": channel.channel_id,
                "order": "date",
                "type": "video",
                "publishedAfter": published_after,
                "maxResults": 10,
                "key": self.api_key
            }
            
            with httpx.Client(timeout=30) as client:
                response = client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                videos = []
                for item in data.get("items", []):
                    video = self._parse_youtube_video(item, channel)
                    if video:
                        videos.append(video)
                
                logger.info(f"YouTube: Fetched {len(videos)} videos from {channel.name}")
                return videos
                
        except Exception as e:
            logger.error(f"YouTube fetch failed for {channel.name}: {e}")
            return []
    
    def _parse_youtube_video(self, item: Dict, channel: YouTubeChannel) -> Optional[Dict]:
        """Parse a YouTube video item into our format"""
        try:
            snippet = item.get("snippet", {})
            title = snippet.get("title", "")
            description = snippet.get("description", "")
            
            # Filter for aviation content
            if not self._is_aviation_content(title, description):
                return None
            
            published_at_str = snippet.get("publishedAt", "")
            published_at = datetime.fromisoformat(published_at_str.replace("Z", "+00:00"))
            
            video_id = item.get("id", {}).get("videoId", "")
            url = f"https://www.youtube.com/watch?v={video_id}"
            
            # Clean title (remove common YouTube clickbait)
            clean_title = self._clean_title(title)
            
            return {
                "title": clean_title,
                "url": url,
                "canonical_url": url,
                "published_at": published_at,
                "summary": description[:500] if description else "",
                "source": f"YouTube - {channel.name}",
                "category": channel.category,
                "content_type": "video",
                "content_hash": f"youtube_{video_id}_{published_at.date()}"
            }
            
        except Exception as e:
            logger.error(f"Error parsing YouTube video: {e}")
            return None
    
    def _is_aviation_content(self, title: str, description: str) -> bool:
        """Check if content is aviation-related"""
        text = (title + " " + description).lower()
        
        # Check for aviation keywords
        for keyword in self.aviation_keywords:
            if keyword in text:
                return True
        
        # Filter out non-aviation content
        non_aviation_keywords = [
            "gaming", "music", "cooking", "travel vlog", "lifestyle", 
            "tech review", "unboxing", "prank", "comedy", "movie"
        ]
        
        for keyword in non_aviation_keywords:
            if keyword in text:
                return False
                
        return False
    
    def _clean_title(self, title: str) -> str:
        """Clean YouTube title from clickbait"""
        # Remove common clickbait patterns
        clickbait_patterns = [
            r"you won't believe",
            r"this will shock you",
            r"doctors hate this",
            r"click here",
            r"watch this",
            r"amazing",
            r"incredible",
            r"shocking",
            r"epic",
            r"insane"
        ]
        
        clean_title = title
        for pattern in clickbait_patterns:
            clean_title = re.sub(pattern, "", clean_title, flags=re.IGNORECASE)
        
        # Remove extra whitespace
        clean_title = re.sub(r"\s+", " ", clean_title).strip()
        
        return clean_title
    
    def fetch_all_channels(self, hours_back: int = 24) -> List[Dict]:
        """Fetch videos from all enabled channels"""
        all_videos = []
        
        for channel in self.channels:
            if channel.enabled:
                videos = self.fetch_channel_videos(channel, hours_back)
                all_videos.extend(videos)
        
        # Sort by priority and recency
        all_videos.sort(key=lambda x: (x.get("source", ""), x.get("published_at", datetime.min)), reverse=True)
        
        logger.info(f"YouTube: Total videos fetched: {len(all_videos)}")
        return all_videos
    
    def get_channel_info(self, channel_id: str) -> Optional[Dict]:
        """Get channel information"""
        if not self.api_key:
            return None
            
        try:
            url = f"{self.base_url}/channels"
            params = {
                "part": "snippet,statistics",
                "id": channel_id,
                "key": self.api_key
            }
            
            with httpx.Client(timeout=30) as client:
                response = client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if data.get("items"):
                    item = data["items"][0]
                    return {
                        "name": item["snippet"]["title"],
                        "description": item["snippet"]["description"],
                        "subscriber_count": item["statistics"].get("subscriberCount", 0),
                        "video_count": item["statistics"].get("videoCount", 0)
                    }
                    
        except Exception as e:
            logger.error(f"Error fetching channel info for {channel_id}: {e}")
            
        return None

# Global YouTube adapter instance
youtube_adapter = YouTubeAdapter()
