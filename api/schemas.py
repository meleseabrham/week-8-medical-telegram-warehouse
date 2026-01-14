from pydantic import BaseModel

class MessageBase(BaseModel):
    channel: str
    content: str

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: int
    timestamp: str

    class Config:
        orm_mode = True
