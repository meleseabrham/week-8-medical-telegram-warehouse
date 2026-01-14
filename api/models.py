from sqlalchemy import Column, Integer, String, DateTime
from .database import Base
import datetime

class RawMessage(Base):
    __tablename__ = "raw_messages"

    id = Column(Integer, primary_key=True, index=True)
    channel = Column(String, index=True)
    content = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
