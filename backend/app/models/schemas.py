from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MessageCreate(BaseModel):
    room_id: str
    message: str
    timestamp: str


class MessageResponse(BaseModel):
    message_id: str
    text: str
    original: Optional[str] = None
    translated: Optional[str] = None
    source_lang: Optional[str] = None
    timestamp: str

    class Config:
        from_attributes = True


class ChatRoomCreate(BaseModel):
    customer_language: str


class ChatRoomResponse(BaseModel):
    room_id: str
    customer_language: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class JoinRoomData(BaseModel):
    room_id: str
    user_type: str  # 'customer' or 'agent'
    customer_language: Optional[str] = None
    agent_id: Optional[str] = None
