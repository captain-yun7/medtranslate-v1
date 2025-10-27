from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ChatRoomCreate(BaseModel):
    """채팅방 생성 요청"""
    customer_language: str = Field(..., description="고객 언어 코드 (ko, en, ja, zh, vi, th)")

    class Config:
        json_schema_extra = {
            "example": {
                "customer_language": "vi"
            }
        }


class ChatRoomResponse(BaseModel):
    """채팅방 응답"""
    id: str
    customer_language: str
    agent_id: Optional[str] = None
    status: str
    created_at: datetime
    ended_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    """메시지 생성 요청"""
    sender_type: str = Field(..., description="발신자 유형 (customer, agent)")
    original_text: str = Field(..., description="원문")
    source_lang: str = Field(..., description="원문 언어")

    class Config:
        json_schema_extra = {
            "example": {
                "sender_type": "customer",
                "original_text": "안녕하세요, 예약하고 싶습니다",
                "source_lang": "ko"
            }
        }


class MessageResponse(BaseModel):
    """메시지 응답"""
    id: int
    room_id: str
    sender_type: str
    sender_id: Optional[str] = None
    original_text: str
    translated_text: Optional[str] = None
    source_lang: str
    target_lang: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TranslationTestRequest(BaseModel):
    """번역 테스트 요청"""
    text: str = Field(..., description="번역할 텍스트")
    source_lang: str = Field(..., description="원문 언어")
    target_lang: str = Field(..., description="번역 대상 언어")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "안녕하세요, 예약하고 싶습니다",
                "source_lang": "ko",
                "target_lang": "en"
            }
        }


class TranslationTestResponse(BaseModel):
    """번역 테스트 응답"""
    original_text: str
    translated_text: str
    source_lang: str
    target_lang: str
    elapsed_time_ms: float
    cached: bool = False
