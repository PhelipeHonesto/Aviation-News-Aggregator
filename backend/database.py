"""Database utilities for the OsaCurator backend."""

from typing import List, Optional
import os
import uuid

from sqlalchemy import text
from sqlmodel import Field, Session, SQLModel, create_engine, select

# --- Database Setup ---
DB_PATH = os.path.join(os.path.dirname(__file__), "news.db")
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)

# --- Models ---
class Article(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    title: str
    date: str
    body: Optional[str] = None
    link: str
    source: str
    status: str

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
    """Replace all news articles with the given list."""
    with Session(engine) as session:
        session.exec(text("DELETE FROM article"))
        for news in news_list:
            article = Article(**news)
            session.add(article)
        session.commit()

def find_news_by_id(story_id: str) -> Optional[Article]:
    """Return a single article by ID, or ``None`` if not found."""
    with Session(engine) as session:
        article = session.get(Article, story_id)
        return article

def generate_id() -> str:
    """Generate a new UUID string."""
    return str(uuid.uuid4())
