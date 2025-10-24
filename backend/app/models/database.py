from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class ChatRoom(Base):
    __tablename__ = "chat_rooms"

    id = Column(String(50), primary_key=True)
    customer_language = Column(String(10), nullable=False)
    agent_id = Column(String(50), nullable=True)
    status = Column(String(20), default='waiting')  # waiting, active, ended
    created_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)

    messages = relationship("Message", back_populates="room")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(String(50), ForeignKey('chat_rooms.id'), nullable=False)
    sender_type = Column(String(20), nullable=False)  # customer, agent
    original_text = Column(Text, nullable=False)
    translated_text = Column(Text, nullable=True)
    source_lang = Column(String(10), nullable=False)
    target_lang = Column(String(10), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    room = relationship("ChatRoom", back_populates="messages")


# DB 헬퍼 함수 (TODO: 나중에 구현)
async def save_message(**kwargs):
    """메시지 저장 함수 (구현 필요)"""
    pass
