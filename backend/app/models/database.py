from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class ChatRoom(Base):
    __tablename__ = "chat_rooms"

    id = Column(String(50), primary_key=True)
    customer_language = Column(String(10), nullable=False)
    agent_id = Column(String(50), ForeignKey('agents.id'), nullable=True)
    status = Column(String(20), default='waiting')  # waiting, active, ended
    created_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    extra_data = Column(JSON, nullable=True)  # metadata is reserved

    messages = relationship("Message", back_populates="room")
    agent = relationship("Agent", back_populates="chat_rooms")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(String(50), ForeignKey('chat_rooms.id'), nullable=False)
    sender_type = Column(String(20), nullable=False)  # customer, agent
    sender_id = Column(String(50), nullable=True)
    original_text = Column(Text, nullable=False)
    translated_text = Column(Text, nullable=True)
    source_lang = Column(String(10), nullable=False)
    target_lang = Column(String(10), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    extra_data = Column(JSON, nullable=True)  # metadata is reserved

    room = relationship("ChatRoom", back_populates="messages")


class Agent(Base):
    """상담사 테이블"""
    __tablename__ = "agents"

    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default='agent')  # agent, admin
    status = Column(String(20), default='offline')  # online, away, offline
    max_concurrent_chats = Column(Integer, default=5)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    chat_rooms = relationship("ChatRoom", back_populates="agent")
    sessions = relationship("AgentSession", back_populates="agent")


class AgentSession(Base):
    """상담사 세션 테이블"""
    __tablename__ = "agent_sessions"

    id = Column(String(50), primary_key=True)
    agent_id = Column(String(50), ForeignKey('agents.id'), nullable=False)
    token = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    ip_address = Column(String(45), nullable=True)

    agent = relationship("Agent", back_populates="sessions")


class CustomerSession(Base):
    """고객 세션 테이블 (익명)"""
    __tablename__ = "customer_sessions"

    id = Column(String(50), primary_key=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    language = Column(String(10), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    extra_data = Column(JSON, nullable=True)  # metadata is reserved


# DB 헬퍼 함수 (TODO: 나중에 구현)
async def save_message(**kwargs):
    """메시지 저장 함수 (구현 필요)"""
    pass
