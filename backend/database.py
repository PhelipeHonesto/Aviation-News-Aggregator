"""Database utilities for the OsaCurator backend."""

from typing import List, Optional
import os
import uuid
import logging
from datetime import datetime

from sqlalchemy import text
from sqlmodel import Field, Session, SQLModel, create_engine, select

# --- Database Setup ---
DB_PATH = os.path.join(os.path.dirname(__file__), "news.db")
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)

# --- Models ---
class Article(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    title: str = Field(index=True)
    summary: Optional[str] = None
    published_at: datetime = Field(index=True)
    body: Optional[str] = None
    link: str = Field(unique=True, index=True)
    source: str = Field(index=True)
    status: str = Field(default="new", index=True)
    created_at: datetime = Field(default_factory=datetime.now, index=True)
    updated_at: datetime = Field(default_factory=datetime.now)

# --- DB Init ---
def init_db() -> None:
    """Create database tables if they don't already exist."""
    SQLModel.metadata.create_all(engine)

# --- Public API ---
def get_all_news() -> List[Article]:
    """Return all articles stored in the database."""
    with Session(engine) as session:
        articles = session.exec(select(Article)).all()
        return articles

def save_all_news(news_list: List[dict]) -> None:
    """Upsert news articles by ID or link. If no ID, create new."""
    with Session(engine) as session:
        for news in news_list:
            try:
                news_id = news.get("id")
                link = news.get("link")
                
                # Try to find existing article by ID first, then by link
                article = None
                if news_id:
                    article = session.get(Article, news_id)
                
                if not article and link:
                    # Try to find by link to avoid duplicates
                    stmt = select(Article).where(Article.link == link)
                    article = session.exec(stmt).first()
                
                if article:
                    # Update existing article
                    for key, value in news.items():
                        if key != "id":  # Don't update the ID
                            setattr(article, key, value)
                    article.updated_at = datetime.now()
                else:
                    # Create new article
                    if not news_id:
                        news["id"] = str(uuid.uuid4())
                    if "published_at" not in news:
                        news["published_at"] = datetime.now()
                    elif isinstance(news["published_at"], str):
                        try:
                            # Handle both ISO format and other formats
                            if 'T' in news["published_at"]:
                                news["published_at"] = datetime.fromisoformat(news["published_at"].replace('Z', '+00:00'))
                            else:
                                # Try parsing as regular datetime string
                                news["published_at"] = datetime.strptime(news["published_at"], "%Y-%m-%d %H:%M:%S")
                        except Exception:
                            news["published_at"] = datetime.now()
                    
                    # Set timestamps
                    now = datetime.now()
                    news["created_at"] = now
                    news["updated_at"] = now
                    
                    article = Article(**news)
                    session.add(article)
                    
            except Exception as e:
                logging.error(f"Error upserting article: {e}")
                continue
                
        try:
            session.commit()
        except Exception as e:
            logging.error(f"Error committing articles to database: {e}")
            session.rollback()

def find_news_by_id(story_id: str) -> Optional[Article]:
    """Return a single article by ID, or ``None`` if not found."""
    with Session(engine) as session:
        article = session.get(Article, story_id)
        return article

def generate_id() -> str:
    """Generate a new UUID string."""
    return str(uuid.uuid4())
