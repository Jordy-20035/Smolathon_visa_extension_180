from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List
import uuid

class ContentPageBase(BaseModel):
    title: str
    slug: str
    content: str
    is_published: bool = False
    page_type: str  # 'news', 'service', 'about', 'statistics'

class ContentPageCreate(ContentPageBase):
    pass

class ContentPageUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    content: Optional[str] = None
    is_published: Optional[bool] = None

class ContentPage(ContentPageBase):
    id: uuid.UUID
    author_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ContentPageList(BaseModel):
    items: List[ContentPage]
    total: int

class NewsItem(BaseModel):
    id: uuid.UUID
    title: str
    slug: str
    excerpt: str
    created_at: datetime
    is_published: bool
    
    model_config = ConfigDict(from_attributes=True)