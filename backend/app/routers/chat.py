from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime

from app.schemas.chat import (
    ChatRoomCreate,
    ChatRoomResponse,
    MessageResponse,
    TranslationTestRequest,
    TranslationTestResponse
)
from app.models.database import ChatRoom, Message, Agent
from app.database import get_db
from app.services.translation import translation_service
from app.dependencies import get_current_agent
import time

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("/rooms", response_model=ChatRoomResponse, status_code=201)
async def create_chat_room(
    room_data: ChatRoomCreate,
    db: Session = Depends(get_db)
):
    """
    새로운 채팅방 생성

    - **customer_language**: 고객 언어 (ko, en, ja, zh, vi, th)
    """
    # 고유 ID 생성
    room_id = f"room_{uuid.uuid4().hex[:12]}"

    # 채팅방 생성
    new_room = ChatRoom(
        id=room_id,
        customer_language=room_data.customer_language,
        status='waiting',
        created_at=datetime.utcnow()
    )

    db.add(new_room)
    db.commit()
    db.refresh(new_room)

    return new_room


@router.get("/rooms", response_model=List[ChatRoomResponse])
async def get_chat_rooms(
    status: str = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    채팅방 목록 조회

    - **status**: 상태 필터 (waiting, active, ended)
    - **limit**: 최대 결과 수 (기본 50)
    """
    query = db.query(ChatRoom)

    if status:
        query = query.filter(ChatRoom.status == status)

    rooms = query.order_by(ChatRoom.created_at.desc()).limit(limit).all()

    return rooms


@router.get("/agent/rooms", response_model=List[ChatRoomResponse])
async def get_agent_rooms(
    include_waiting: bool = True,
    db: Session = Depends(get_db),
    current_agent: Agent = Depends(get_current_agent)
):
    """
    현재 로그인한 상담사의 채팅방 목록 조회

    - **include_waiting**: 대기 중인 채팅방도 포함 (기본 True)

    Returns:
        - 상담사에게 할당된 활성 채팅방
        - include_waiting=True인 경우, 미할당 대기 채팅방도 포함
    """
    # 상담사에게 할당된 활성 채팅방
    query = db.query(ChatRoom).filter(
        ChatRoom.agent_id == current_agent.id,
        ChatRoom.status.in_(['waiting', 'active'])
    )

    assigned_rooms = query.order_by(ChatRoom.created_at.desc()).all()

    # 대기 중인 미할당 채팅방 추가
    if include_waiting:
        waiting_rooms = db.query(ChatRoom).filter(
            ChatRoom.agent_id == None,
            ChatRoom.status == 'waiting'
        ).order_by(ChatRoom.created_at.desc()).limit(10).all()

        return assigned_rooms + waiting_rooms

    return assigned_rooms


@router.post("/rooms/{room_id}/assign", response_model=ChatRoomResponse)
async def assign_room_to_agent(
    room_id: str,
    db: Session = Depends(get_db),
    current_agent: Agent = Depends(get_current_agent)
):
    """
    채팅방을 현재 상담사에게 할당

    대기 중인 채팅방을 상담사가 수락할 때 사용
    """
    room = db.query(ChatRoom).filter(ChatRoom.id == room_id).first()

    if not room:
        raise HTTPException(status_code=404, detail="채팅방을 찾을 수 없습니다")

    if room.status != 'waiting':
        raise HTTPException(status_code=400, detail="대기 중인 채팅방만 할당할 수 있습니다")

    if room.agent_id and room.agent_id != current_agent.id:
        raise HTTPException(status_code=400, detail="이미 다른 상담사에게 할당된 채팅방입니다")

    # 상담사 할당 및 상태 변경
    room.agent_id = current_agent.id
    room.status = 'active'

    db.commit()
    db.refresh(room)

    return room


@router.get("/rooms/{room_id}", response_model=ChatRoomResponse)
async def get_chat_room(
    room_id: str,
    db: Session = Depends(get_db)
):
    """
    특정 채팅방 조회
    """
    room = db.query(ChatRoom).filter(ChatRoom.id == room_id).first()

    if not room:
        raise HTTPException(status_code=404, detail="채팅방을 찾을 수 없습니다")

    return room


@router.get("/rooms/{room_id}/messages", response_model=List[MessageResponse])
async def get_room_messages(
    room_id: str,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    채팅방의 메시지 히스토리 조회

    - **limit**: 최대 결과 수 (기본 100)
    """
    # 채팅방 존재 확인
    room = db.query(ChatRoom).filter(ChatRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="채팅방을 찾을 수 없습니다")

    # 메시지 조회
    messages = db.query(Message)\
        .filter(Message.room_id == room_id)\
        .order_by(Message.created_at.asc())\
        .limit(limit)\
        .all()

    return messages


@router.delete("/rooms/{room_id}", status_code=204)
async def end_chat_room(
    room_id: str,
    db: Session = Depends(get_db)
):
    """
    채팅방 종료
    """
    room = db.query(ChatRoom).filter(ChatRoom.id == room_id).first()

    if not room:
        raise HTTPException(status_code=404, detail="채팅방을 찾을 수 없습니다")

    room.status = 'ended'
    room.ended_at = datetime.utcnow()

    db.commit()

    return None


@router.post("/translation/test", response_model=TranslationTestResponse)
async def test_translation(request: TranslationTestRequest):
    """
    번역 테스트 API

    - **text**: 번역할 텍스트
    - **source_lang**: 원문 언어
    - **target_lang**: 번역 대상 언어
    """
    start_time = time.time()

    try:
        translated = await translation_service.translate(
            text=request.text,
            source_lang=request.source_lang,
            target_lang=request.target_lang
        )

        elapsed_ms = (time.time() - start_time) * 1000

        return TranslationTestResponse(
            original_text=request.text,
            translated_text=translated,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
            elapsed_time_ms=round(elapsed_ms, 2),
            cached=False  # TODO: 캐시 히트 여부 확인
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"번역 실패: {str(e)}"
        )
