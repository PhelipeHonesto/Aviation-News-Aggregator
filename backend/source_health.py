"""
Loud Hawk v2 - Source Health & Reliability Tracking
Circuit breaker pattern for robust news aggregation
"""
import time
import random
import httpx
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple
from dataclasses import dataclass
from sqlmodel import SQLModel, Field, Session
from database import engine

logger = logging.getLogger(__name__)

# Reliability constants
HTTP_TIMEOUT = 15
MAX_RETRIES = 2
BACKOFF_BASE = 0.6  # seconds
CIRCUIT_BREAKER_THRESHOLD = 4  # disable after 4 consecutive failures
BOZO_FEED_THRESHOLD = 3  # disable after 3 consecutive bozo feeds
TIMEOUT_THRESHOLD = 5  # disable after 5 consecutive timeouts

@dataclass
class SourceHealth:
    """Source health tracking data"""
    name: str
    enabled: bool = True
    success_24h: int = 0
    fail_24h: int = 0
    last_ok_at: Optional[datetime] = None
    error_streak: int = 0
    bozo_streak: int = 0  # Consecutive bozo feeds
    timeout_streak: int = 0  # Consecutive timeouts
    disabled_reason: Optional[str] = None
    last_error: Optional[str] = None

class SourceReliability(SQLModel, table=True):
    """Database model for tracking source reliability"""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    enabled: bool = Field(default=True)
    success_24h: int = Field(default=0)
    fail_24h: int = Field(default=0)
    last_ok_at: Optional[datetime] = None
    error_streak: int = Field(default=0)
    bozo_streak: int = Field(default=0)  # Consecutive bozo feeds
    timeout_streak: int = Field(default=0)  # Consecutive timeouts
    disabled_reason: Optional[str] = None
    last_error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

def backoff(attempt: int) -> None:
    """Exponential backoff with jitter"""
    time.sleep(BACKOFF_BASE * (2 ** attempt) + random.random() * 0.2)

def fetch_with_reliability(source_name: str, url: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Fetch URL with reliability tracking and circuit breaker
    
    Returns:
        (content, error) - content if successful, error message if failed
    """
    # Check if source is enabled, create health record if it doesn't exist
    health = get_source_health(source_name)
    if not health:
        # Initialize health record for new source
        init_source_health(source_name)
        health = get_source_health(source_name)
    
    if not health or not health.enabled:
        return None, f"Source {source_name} is disabled: {health.disabled_reason if health else 'not found'}"

    for attempt in range(MAX_RETRIES + 1):
        try:
            # Parse domain for referer header
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            referer = f"https://{domain}/"
            
            with httpx.Client(
                timeout=httpx.Timeout(HTTP_TIMEOUT),
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                    "Accept": "application/rss+xml, application/atom+xml, application/xml;q=0.9, text/xml;q=0.8, */*;q=0.7",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Referer": referer,
                    "Cache-Control": "no-cache",
                },
                follow_redirects=True,
                http2=True,
            ) as client:
                response = client.get(url)
                
                if response.status_code == 304:
                    return "", None  # Not modified
                
                response.raise_for_status()
                
                # Small politeness delay between sources
                time.sleep(0.2)
                
                # Record success
                record_source_success(source_name)
                return response.text, None
                
        except httpx.TimeoutException as e:
            error_msg = f"Timeout after {HTTP_TIMEOUT}s"
            if attempt < MAX_RETRIES:
                backoff(attempt)
            else:
                record_source_timeout(source_name, error_msg)
                return None, error_msg
                
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.reason_phrase}"
            # Only trip circuit breaker on 4xx errors (except 429 rate limit)
            if e.response.status_code >= 400 and e.response.status_code < 500 and e.response.status_code != 429:
                record_source_failure(source_name, error_msg)
            else:
                record_source_success(source_name)  # Don't count 429 as failure
            return None, error_msg
            
        except Exception as e:
            error_msg = f"Network error: {str(e)}"
            if attempt < MAX_RETRIES:
                backoff(attempt)
            else:
                record_source_failure(source_name, error_msg)
                return None, error_msg

def init_source_health(source_name: str) -> None:
    """Initialize health record for a new source"""
    with Session(engine) as session:
        # Check if already exists
        existing = session.query(SourceReliability).filter(
            SourceReliability.name == source_name
        ).first()
        
        if not existing:
            health_record = SourceReliability(
                name=source_name,
                enabled=True,
                success_24h=0,
                fail_24h=0,
                error_streak=0
            )
            session.add(health_record)
            session.commit()
            logger.info(f"Initialized health record for source: {source_name}")

def get_source_health(source_name: str) -> Optional[SourceHealth]:
    """Get source health data from database"""
    with Session(engine) as session:
        record = session.query(SourceReliability).filter(
            SourceReliability.name == source_name
        ).first()
        
        if not record:
            return None
            
        return SourceHealth(
            name=record.name,
            enabled=record.enabled,
            success_24h=record.success_24h,
            fail_24h=record.fail_24h,
            last_ok_at=record.last_ok_at,
            error_streak=record.error_streak,
            disabled_reason=record.disabled_reason,
            last_error=record.last_error
        )

def record_source_success(source_name: str) -> None:
    """Record a successful fetch for a source"""
    with Session(engine) as session:
        record = session.query(SourceReliability).filter(
            SourceReliability.name == source_name
        ).first()
        
        if not record:
            record = SourceReliability(name=source_name)
            session.add(record)
        
        record.success_24h += 1
        record.error_streak = 0
        record.bozo_streak = 0  # Reset bozo streak on success
        record.timeout_streak = 0  # Reset timeout streak on success
        record.last_ok_at = datetime.utcnow()
        record.last_error = None
        record.updated_at = datetime.utcnow()
        
        session.commit()
        logger.info(f"Source {source_name} success recorded")

def record_source_failure(source_name: str, error_msg: str) -> None:
    """Record a failed fetch for a source"""
    with Session(engine) as session:
        record = session.query(SourceReliability).filter(
            SourceReliability.name == source_name
        ).first()
        
        if not record:
            record = SourceReliability(name=source_name)
            session.add(record)
        
        record.fail_24h += 1
        record.error_streak += 1
        record.last_error = error_msg
        record.updated_at = datetime.utcnow()
        
        # Circuit breaker: disable after consecutive failures
        if record.error_streak >= CIRCUIT_BREAKER_THRESHOLD:
            record.enabled = False
            record.disabled_reason = f"Circuit breaker: {record.error_streak} consecutive failures"
            logger.warning(f"Source {source_name} disabled by circuit breaker")
        
        session.commit()
        logger.warning(f"Source {source_name} failure recorded: {error_msg}")

def record_source_timeout(source_name: str, error_msg: str) -> None:
    """Record a timeout for a source"""
    with Session(engine) as session:
        record = session.query(SourceReliability).filter(
            SourceReliability.name == source_name
        ).first()
        
        if not record:
            record = SourceReliability(name=source_name)
            session.add(record)
        
        record.fail_24h += 1
        record.timeout_streak += 1
        record.last_error = error_msg
        record.updated_at = datetime.utcnow()
        
        # Circuit breaker: disable after consecutive timeouts
        if record.timeout_streak >= TIMEOUT_THRESHOLD:
            record.enabled = False
            record.disabled_reason = f"Circuit breaker: {record.timeout_streak} consecutive timeouts"
            logger.warning(f"Source {source_name} disabled by timeout circuit breaker")
        
        session.commit()
        logger.warning(f"Source {source_name} timeout recorded: {error_msg}")

def record_source_bozo(source_name: str, error_msg: str) -> None:
    """Record a bozo (malformed) feed for a source"""
    with Session(engine) as session:
        record = session.query(SourceReliability).filter(
            SourceReliability.name == source_name
        ).first()
        
        if not record:
            record = SourceReliability(name=source_name)
            session.add(record)
        
        record.fail_24h += 1
        record.bozo_streak += 1
        record.last_error = error_msg
        record.updated_at = datetime.utcnow()
        
        # Circuit breaker: disable after consecutive bozo feeds
        if record.bozo_streak >= BOZO_FEED_THRESHOLD:
            record.enabled = False
            record.disabled_reason = f"Circuit breaker: {record.bozo_streak} consecutive bozo feeds"
            logger.warning(f"Source {source_name} disabled by bozo circuit breaker")
        
        session.commit()
        logger.warning(f"Source {source_name} bozo feed recorded: {error_msg}")

def enable_source(source_name: str) -> bool:
    """Enable a source (reset circuit breaker)"""
    with Session(engine) as session:
        record = session.query(SourceReliability).filter(
            SourceReliability.name == source_name
        ).first()
        
        if not record:
            return False
        
        record.enabled = True
        record.error_streak = 0
        record.disabled_reason = None
        record.last_error = None
        record.updated_at = datetime.utcnow()
        
        session.commit()
        logger.info(f"Source {source_name} enabled")
        return True

def disable_source(source_name: str, reason: str) -> bool:
    """Manually disable a source"""
    with Session(engine) as session:
        record = session.query(SourceReliability).filter(
            SourceReliability.name == source_name
        ).first()
        
        if not record:
            return False
        
        record.enabled = False
        record.disabled_reason = reason
        record.updated_at = datetime.utcnow()
        
        session.commit()
        logger.info(f"Source {source_name} disabled: {reason}")
        return True

def get_all_source_health() -> list[SourceHealth]:
    """Get health data for all sources"""
    with Session(engine) as session:
        records = session.query(SourceReliability).all()
        return [
            SourceHealth(
                name=record.name,
                enabled=record.enabled,
                success_24h=record.success_24h,
                fail_24h=record.fail_24h,
                last_ok_at=record.last_ok_at,
                error_streak=record.error_streak,
                disabled_reason=record.disabled_reason,
                last_error=record.last_error
            )
            for record in records
        ]

def calculate_reliability_score(health: SourceHealth) -> float:
    """Calculate reliability score (0.0 to 1.0)"""
    total_attempts = health.success_24h + health.fail_24h
    if total_attempts == 0:
        return 0.5  # Neutral score for new sources
    
    return health.success_24h / total_attempts

def cleanup_old_health_data() -> None:
    """Clean up health data older than 24 hours"""
    cutoff = datetime.utcnow() - timedelta(hours=24)
    
    with Session(engine) as session:
        # Reset 24h counters for old data
        session.query(SourceReliability).filter(
            SourceReliability.updated_at < cutoff
        ).update({
            "success_24h": 0,
            "fail_24h": 0,
            "updated_at": datetime.utcnow()
        })
        session.commit()
        logger.info("Cleaned up old health data")

def validate_source(source_name: str, url: str) -> Tuple[bool, str]:
    """
    Validate a source by fetching and parsing once
    
    Returns:
        (success, message) - success status and descriptive message
    """
    content, error = fetch_with_reliability(source_name, url)
    if error:
        return False, f"Fetch failed: {error}"
    
    if not content:
        return False, "No content returned"
    
    # Basic validation - check if it looks like RSS or has content
    if "<?xml" in content or "<rss" in content or "<feed" in content:
        return True, "RSS feed detected"
    elif len(content) > 1000:  # Reasonable content length
        return True, f"HTML content detected ({len(content)} chars)"
    else:
        return False, "Content too short or invalid format"
