from sqlmodel import SQLModel, Field, Session, create_engine, select
from typing import List, Optional
import uuid
import os
from sqlalchemy import text

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
def init_db():
    SQLModel.metadata.create_all(engine)

# --- Public API ---
def get_all_news() -> List[Article]:
    with Session(engine) as session:
        articles = session.exec(select(Article)).all()
        return articles

def save_all_news(news_list: List[dict]):
    """Bulk replace all news articles (dangerous: clears table first)."""
    with Session(engine) as session:
        session.exec(text("DELETE FROM article"))
        for news in news_list:
            article = Article(**news)
            session.add(article)
        session.commit()

def find_news_by_id(story_id: str) -> Optional[Article]:
    with Session(engine) as session:
        article = session.get(Article, story_id)
        return article

def generate_id() -> str:
    return str(uuid.uuid4())
