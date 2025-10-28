"""
인증 관련 API 라우터
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta, datetime

from app.database import get_db
from app.models.database import Agent
from app.schemas.auth import LoginRequest, TokenResponse, AgentResponse
from app.services.auth import verify_password, create_access_token
from app.config import settings
from app.dependencies import get_current_agent

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    상담사 로그인

    - **email**: 상담사 이메일
    - **password**: 비밀번호

    Returns:
        - **access_token**: JWT 액세스 토큰
        - **token_type**: 토큰 타입 (bearer)
    """
    # 이메일로 상담사 조회
    agent = db.query(Agent).filter(Agent.email == login_data.email).first()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 비밀번호 검증
    if not verify_password(login_data.password, agent.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # JWT 토큰 생성
    access_token_expires = timedelta(hours=settings.JWT_ACCESS_TOKEN_EXPIRE_HOURS)
    access_token = create_access_token(
        data={"sub": agent.id, "email": agent.email, "role": agent.role},
        expires_delta=access_token_expires
    )

    # 마지막 로그인 시간 업데이트
    from datetime import datetime
    agent.last_login = datetime.utcnow()
    db.commit()

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/logout")
async def logout():
    """
    상담사 로그아웃

    Note: JWT는 stateless이므로 서버에서는 별도 처리 없음.
    클라이언트에서 토큰을 삭제해야 함.
    """
    return {"message": "로그아웃 되었습니다"}


@router.get("/me", response_model=AgentResponse)
async def get_me(
    db: Session = Depends(get_db),
    current_agent: Agent = Depends(get_current_agent)
):
    """
    현재 로그인한 상담사 정보 조회

    Requires: Bearer 토큰
    """
    return current_agent
