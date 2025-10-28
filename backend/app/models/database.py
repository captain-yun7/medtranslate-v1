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


# DB 헬퍼 함수
def save_message(
    db_session,
    room_id: str,
    sender_type: str,
    original_text: str,
    translated_text: str = None,
    source_lang: str = None,
    target_lang: str = None,
    sender_id: str = None
) -> Message:
    """
    메시지를 데이터베이스에 저장

    Args:
        db_session: SQLAlchemy 세션
        room_id: 채팅방 ID
        sender_type: 발신자 유형 ('customer' or 'agent')
        original_text: 원문
        translated_text: 번역문
        source_lang: 원문 언어
        target_lang: 번역 대상 언어
        sender_id: 발신자 ID (optional)

    Returns:
        Message: 저장된 메시지 객체
    """
    message = Message(
        room_id=room_id,
        sender_type=sender_type,
        sender_id=sender_id,
        original_text=original_text,
        translated_text=translated_text,
        source_lang=source_lang,
        target_lang=target_lang,
        created_at=datetime.utcnow()
    )

    db_session.add(message)
    db_session.commit()
    db_session.refresh(message)

    return message


def get_messages(db_session, room_id: str, limit: int = 100, offset: int = 0):
    """
    채팅방의 메시지 히스토리 조회

    Args:
        db_session: SQLAlchemy 세션
        room_id: 채팅방 ID
        limit: 조회할 메시지 수 (기본 100)
        offset: 건너뛸 메시지 수 (기본 0)

    Returns:
        List[Message]: 메시지 리스트 (오래된 순)
    """
    messages = db_session.query(Message)\
        .filter(Message.room_id == room_id)\
        .order_by(Message.created_at.asc())\
        .offset(offset)\
        .limit(limit)\
        .all()

    return messages
