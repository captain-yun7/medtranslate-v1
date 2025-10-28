"""
인증 관련 Pydantic 스키마
"""
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """로그인 요청"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT 토큰 응답"""
    access_token: str
    token_type: str = "bearer"


class AgentResponse(BaseModel):
    """상담사 정보 응답"""
    id: str
    name: str
    email: EmailStr
    role: str
    status: str

    class Config:
        from_attributes = True
