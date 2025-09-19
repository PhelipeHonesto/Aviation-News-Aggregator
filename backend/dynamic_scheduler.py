"""
Dynamic Scheduler for Loud Hawk v2
Adjusts polling frequency based on source activity and content volume
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from sqlmodel import Session, select
from database import get_session
from models import NewsArticle

logger = logging.getLogger(__name__)

@dataclass
class SourceActivity:
    """Tracks source activity metrics"""
    source_name: str
    articles_last_hour: int
    articles_last_24h: int
    avg_articles_per_hour: float
    last_article_at: Optional[datetime]
    success_rate: float
    error_streak: int

class DynamicScheduler:
    """Manages dynamic polling frequencies based on source activity"""
    
    def __init__(self):
        self.activity_cache: Dict[str, SourceActivity] = {}
        self.frequency_rules = {
            # Fast movers - high volume, frequent updates
            "FAST": {
                "sources": ["Simple Flying", "FlightGlobal", "AVweb", "The Aviation Herald"],
                "interval": 3,  # 3 minutes
                "conditions": lambda activity: activity.avg_articles_per_hour >= 2.0
            },
            # Steady sources - regulators, OEMs
            "STEADY": {
                "sources": ["FAA Newsroom", "NTSB Press", "EASA News", "Airbus Newsroom", "Boeing Newsroom"],
                "interval": 10,  # 10 minutes
                "conditions": lambda activity: 0.5 <= activity.avg_articles_per_hour < 2.0
            },
            # Moderate sources - airlines, industry
            "MODERATE": {
                "sources": ["Delta News Hub", "United Media Room", "A4A Airlines for America"],
                "interval": 15,  # 15 minutes
                "conditions": lambda activity: 0.2 <= activity.avg_articles_per_hour < 0.5
            },
            # Slow movers - IR pages, MROs
            "SLOW": {
                "sources": ["Lufthansa Technik News", "ST Engineering Aerospace"],
                "interval": 30,  # 30 minutes
                "conditions": lambda activity: activity.avg_articles_per_hour < 0.2
            }
        }
        
    def calculate_source_activity(self, source_name: str, hours_back: int = 24) -> SourceActivity:
        """Calculate activity metrics for a source"""
        with get_session() as session:
            # Get articles from last 24 hours
            cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
            
            # Count articles by time periods
            articles_24h = session.exec(
                select(NewsArticle).where(
                    NewsArticle.source == source_name,
                    NewsArticle.published_at >= cutoff_time
                )
            ).all()
            
            articles_1h = [
                a for a in articles_24h 
                if a.published_at >= datetime.utcnow() - timedelta(hours=1)
            ]
            
            # Calculate metrics
            avg_per_hour = len(articles_24h) / hours_back if hours_back > 0 else 0
            
            last_article = None
            if articles_24h:
                last_article = max(a.published_at for a in articles_24h)
            
            return SourceActivity(
                source_name=source_name,
                articles_last_hour=len(articles_1h),
                articles_last_24h=len(articles_24h),
                avg_articles_per_hour=avg_per_hour,
                last_article_at=last_article,
                success_rate=1.0,  # TODO: Integrate with source_health
                error_streak=0      # TODO: Integrate with source_health
            )
    
    def get_optimal_interval(self, source_name: str) -> int:
        """Get optimal polling interval for a source"""
        activity = self.calculate_source_activity(source_name)
        self.activity_cache[source_name] = activity
        
        # Check if source matches predefined fast movers
        for rule_name, rule in self.frequency_rules.items():
            if source_name in rule["sources"]:
                return rule["interval"]
        
        # Dynamic calculation based on activity
        avg_per_hour = activity.avg_articles_per_hour
        
        if avg_per_hour >= 2.0:
            return 3  # Fast movers
        elif avg_per_hour >= 0.5:
            return 10  # Steady sources
        elif avg_per_hour >= 0.2:
            return 15  # Moderate sources
        else:
            return 30  # Slow movers
    
    def should_poll_source(self, source_name: str, last_poll: Optional[datetime]) -> bool:
        """Determine if a source should be polled now"""
        if last_poll is None:
            return True
            
        interval = self.get_optimal_interval(source_name)
        next_poll = last_poll + timedelta(minutes=interval)
        
        return datetime.utcnow() >= next_poll
    
    def get_active_sources(self, all_sources: List[str]) -> List[str]:
        """Get list of sources that should be polled now"""
        active_sources = []
        
        for source_name in all_sources:
            # TODO: Get last_poll from source_health table
            last_poll = None  # Placeholder
            
            if self.should_poll_source(source_name, last_poll):
                active_sources.append(source_name)
        
        return active_sources
    
    def update_source_activity(self, source_name: str):
        """Update activity metrics after successful fetch"""
        if source_name in self.activity_cache:
            # Refresh the cache
            self.activity_cache[source_name] = self.calculate_source_activity(source_name)
    
    def get_source_priority(self, source_name: str) -> int:
        """Get priority score for a source (higher = more important)"""
        activity = self.activity_cache.get(source_name)
        if not activity:
            activity = self.calculate_source_activity(source_name)
            self.activity_cache[source_name] = activity
        
        # Base priority by source type
        base_priority = {
            "FAA Newsroom": 100,
            "NTSB Press": 95,
            "EASA News": 90,
            "ICAO Newsroom": 85,
            "Airbus Newsroom": 80,
            "Boeing Newsroom": 80,
            "The Aviation Herald": 75,
            "Aviation Week": 70,
            "FlightGlobal": 65,
            "Simple Flying": 60,
            "AVweb": 60,
        }.get(source_name, 50)
        
        # Adjust by activity
        activity_multiplier = min(2.0, max(0.5, activity.avg_articles_per_hour))
        
        return int(base_priority * activity_multiplier)

# Global scheduler instance
dynamic_scheduler = DynamicScheduler()
