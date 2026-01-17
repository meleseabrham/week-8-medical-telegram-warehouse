from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TopProduct(BaseModel):
    keyword: str
    frequency: int

class ChannelActivity(BaseModel):
    channel_name: str
    post_count: int
    avg_views: float

class MessageSearch(BaseModel):
    id: int
    date: datetime
    channel: str
    text: str
    views: Optional[int]

class VisualContentStats(BaseModel):
    category: str
    count: int
    avg_views: float
