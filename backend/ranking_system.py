"""
Authority-Weighted Ranking System for Loud Hawk v2
Ranks articles by source authority, recency, and content quality
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import re
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class ArticleRank:
    """Article ranking score and metadata"""
    article_id: int
    score: float
    authority_score: float
    recency_score: float
    quality_score: float
    category: str
    source: str

class AuthorityRankingSystem:
    """Authority-weighted ranking system for aviation news"""
    
    def __init__(self):
        # Source authority weights (higher = more authoritative)
        self.source_authority = {
            # Regulators (highest authority)
            "FAA Newsroom": 100,
            "NTSB Press": 95,
            "EASA News": 90,
            "ICAO Newsroom": 85,
            "Transport Canada Civil Aviation": 80,
            "UK CAA News": 80,
            "CASA Australia News": 75,
            
            # Safety organizations
            "The Aviation Herald": 85,
            "Skybrary": 70,
            
            # OEMs (high authority for technical content)
            "Airbus Newsroom": 80,
            "Boeing Newsroom": 80,
            "Embraer Media": 75,
            "Bombardier News": 70,
            "GE Aerospace Press": 75,
            "Pratt & Whitney News": 70,
            "Rolls-Royce Civil Aerospace": 70,
            
            # Airlines (moderate authority)
            "Delta News Hub": 60,
            "United Media Room": 60,
            "Alaska Airlines Newsroom": 55,
            "American Airlines Newsroom": 55,
            "Southwest Newsroom": 55,
            "Lufthansa Group News": 60,
            "Air France-KLM Press": 55,
            
            # Industry associations
            "A4A Airlines for America": 70,
            "ACI World": 65,
            "Eurocontrol News": 70,
            "NATS (UK ATC) News": 65,
            
            # Media (varies by reputation)
            "Aviation Week": 75,
            "FlightGlobal": 70,
            "The Air Current": 70,
            "AVweb": 65,
            "Simple Flying": 50,
            "AirlineGeeks": 55,
            "Runway Girl Network": 60,
            
            # Data providers
            "OAG Blog": 65,
            "Flightradar24 Blog": 60,
            "RoutesOnline": 55,
            
            # eVTOL (emerging authority)
            "Joby Aviation News": 60,
            "Archer Aviation News": 55,
            "Eve Air Mobility": 55,
            "Vertical Aerospace": 55,
            
            # Airports
            "Heathrow Media Centre": 50,
            "ATL Pressroom": 50,
            
            # MRO
            "Lufthansa Technik News": 60,
            "ST Engineering Aerospace": 55,
            
            # YouTube creators (lower but valuable)
            "YouTube - Mentour Pilot": 40,
            "YouTube - DJ's Aviation": 35,
            "YouTube - FAA Safety Briefing": 60,
            "YouTube - Captain Joe": 35,
            
            # Default for unknown sources
            "default": 30
        }
        
        # Category authority weights
        self.category_authority = {
            "REGULATOR": 1.5,
            "SAFETY": 1.4,
            "OEM": 1.3,
            "ATC": 1.2,
            "INDUSTRY": 1.1,
            "AIRLINE": 1.0,
            "MEDIA": 0.9,
            "DATA": 0.8,
            "AIRPORT": 0.7,
            "EVTOL": 0.8,
            "MRO": 0.8,
            "CREATOR": 0.6,
            "default": 0.5
        }
        
        # Clickbait patterns to downweight
        self.clickbait_patterns = [
            r"\d+\s+things?\s+you\s+need\s+to\s+know",
            r"you\s+won't\s+believe",
            r"this\s+will\s+shock\s+you",
            r"doctors?\s+hate\s+this",
            r"click\s+here",
            r"watch\s+this",
            r"amazing\s+",
            r"incredible\s+",
            r"shocking\s+",
            r"epic\s+",
            r"insane\s+",
            r"mind\s+blowing",
            r"game\s+changer",
            r"secret\s+",
            r"hidden\s+",
            r"revealed\s*$",
            r"exposed\s*$"
        ]
        
        # High-value aviation keywords
        self.aviation_keywords = [
            "safety", "incident", "accident", "investigation", "regulation",
            "certification", "maintenance", "engine", "avionics", "airframe",
            "air traffic", "airspace", "route", "capacity", "delays",
            "fleet", "delivery", "order", "partnership", "alliance",
            "sustainability", "emissions", "fuel", "efficiency", "innovation"
        ]
    
    def calculate_article_score(self, article: Dict) -> ArticleRank:
        """Calculate comprehensive ranking score for an article"""
        source = article.get("source", "")
        category = article.get("category", "default")
        title = article.get("title", "")
        summary = article.get("summary", "")
        published_at = article.get("published_at")
        
        # Authority score (0-100)
        authority_score = self._calculate_authority_score(source, category)
        
        # Recency score (0-100)
        recency_score = self._calculate_recency_score(published_at)
        
        # Quality score (0-100)
        quality_score = self._calculate_quality_score(title, summary)
        
        # Combine scores with weights
        total_score = (
            authority_score * 0.4 +  # 40% authority
            recency_score * 0.3 +    # 30% recency  
            quality_score * 0.3      # 30% quality
        )
        
        return ArticleRank(
            article_id=article.get("id", 0),
            score=total_score,
            authority_score=authority_score,
            recency_score=recency_score,
            quality_score=quality_score,
            category=category,
            source=source
        )
    
    def _calculate_authority_score(self, source: str, category: str) -> float:
        """Calculate authority score based on source reputation"""
        source_score = self.source_authority.get(source, self.source_authority["default"])
        category_multiplier = self.category_authority.get(category, self.category_authority["default"])
        
        return min(100.0, source_score * category_multiplier)
    
    def _calculate_recency_score(self, published_at: Optional[datetime]) -> float:
        """Calculate recency score (newer = higher)"""
        if not published_at:
            return 0.0
            
        now = datetime.utcnow()
        if published_at.tzinfo is None:
            # Assume UTC if no timezone
            published_at = published_at.replace(tzinfo=datetime.utcnow().tzinfo)
        
        age_hours = (now - published_at).total_seconds() / 3600
        
        # Scoring curve: 100 for <1 hour, 80 for <6 hours, 60 for <24 hours, etc.
        if age_hours < 1:
            return 100.0
        elif age_hours < 6:
            return 80.0
        elif age_hours < 24:
            return 60.0
        elif age_hours < 72:
            return 40.0
        elif age_hours < 168:  # 1 week
            return 20.0
        else:
            return 10.0
    
    def _calculate_quality_score(self, title: str, summary: str) -> float:
        """Calculate content quality score"""
        text = (title + " " + summary).lower()
        score = 50.0  # Base score
        
        # Penalize clickbait
        for pattern in self.clickbait_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                score -= 20.0
                break
        
        # Reward aviation keywords
        aviation_keyword_count = sum(1 for keyword in self.aviation_keywords if keyword in text)
        score += min(30.0, aviation_keyword_count * 3.0)
        
        # Reward technical content
        technical_indicators = ["analysis", "report", "study", "research", "data", "statistics", "trend"]
        if any(indicator in text for indicator in technical_indicators):
            score += 15.0
        
        # Reward news indicators
        news_indicators = ["announces", "reports", "confirms", "reveals", "launches", "partnership"]
        if any(indicator in text for indicator in news_indicators):
            score += 10.0
        
        # Penalize promotional content
        promo_indicators = ["sale", "discount", "offer", "promotion", "sponsored", "advertisement"]
        if any(indicator in text for indicator in promo_indicators):
            score -= 25.0
        
        return max(0.0, min(100.0, score))
    
    def rank_articles(self, articles: List[Dict], limit: int = 50) -> List[Dict]:
        """Rank and return top articles"""
        if not articles:
            return []
        
        # Calculate scores for all articles
        ranked_articles = []
        for article in articles:
            rank = self.calculate_article_score(article)
            ranked_articles.append((article, rank))
        
        # Sort by total score (descending)
        ranked_articles.sort(key=lambda x: x[1].score, reverse=True)
        
        # Return top articles with ranking metadata
        result = []
        for i, (article, rank) in enumerate(ranked_articles[:limit]):
            article["rank"] = i + 1
            article["score"] = round(rank.score, 2)
            article["authority_score"] = round(rank.authority_score, 2)
            article["recency_score"] = round(rank.recency_score, 2)
            article["quality_score"] = round(rank.quality_score, 2)
            result.append(article)
        
        return result
    
    def get_source_rankings(self, articles: List[Dict]) -> Dict[str, Dict]:
        """Get ranking statistics by source"""
        source_stats = {}
        
        for article in articles:
            source = article.get("source", "Unknown")
            if source not in source_stats:
                source_stats[source] = {
                    "count": 0,
                    "total_score": 0.0,
                    "avg_score": 0.0,
                    "top_score": 0.0,
                    "authority_score": 0.0
                }
            
            stats = source_stats[source]
            stats["count"] += 1
            stats["total_score"] += article.get("score", 0.0)
            stats["top_score"] = max(stats["top_score"], article.get("score", 0.0))
            stats["authority_score"] = self._calculate_authority_score(source, article.get("category", "default"))
        
        # Calculate averages
        for source, stats in source_stats.items():
            if stats["count"] > 0:
                stats["avg_score"] = round(stats["total_score"] / stats["count"], 2)
        
        return source_stats
    
    def detect_duplicates(self, articles: List[Dict]) -> List[List[Dict]]:
        """Detect potential duplicate articles"""
        # Group by content hash first
        hash_groups = {}
        for article in articles:
            content_hash = article.get("content_hash", "")
            if content_hash not in hash_groups:
                hash_groups[content_hash] = []
            hash_groups[content_hash].append(article)
        
        # Find groups with multiple articles (duplicates)
        duplicate_groups = [group for group in hash_groups.values() if len(group) > 1]
        
        # Also check for title similarity (fuzzy duplicates)
        title_groups = {}
        for article in articles:
            title = article.get("title", "").lower().strip()
            # Simple similarity check - could be improved with Levenshtein distance
            similar_titles = [t for t in title_groups.keys() if self._title_similarity(title, t) > 0.8]
            if similar_titles:
                # Merge with existing group
                existing_group = title_groups[similar_titles[0]]
                existing_group.append(article)
            else:
                title_groups[title] = [article]
        
        # Add fuzzy duplicates
        fuzzy_duplicates = [group for group in title_groups.values() if len(group) > 1]
        
        return duplicate_groups + fuzzy_duplicates
    
    def _title_similarity(self, title1: str, title2: str) -> float:
        """Calculate similarity between two titles (0-1)"""
        words1 = set(title1.split())
        words2 = set(title2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)

# Global ranking system instance
ranking_system = AuthorityRankingSystem()
