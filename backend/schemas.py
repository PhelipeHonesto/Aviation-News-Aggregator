from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ArticleSchema(BaseModel):
    id: str
    title: str
    summary: Optional[str] = None
    source: str
    published_at: datetime
    body: Optional[str] = None
    link: str
    status: Optional[str] = None

    class Config:
        orm_mode = True 