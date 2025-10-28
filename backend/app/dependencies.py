"""
FastAPI 의존성 함수들
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.database import Agent
from app.services.auth import decode_access_token

# Bearer 토큰 스키마
security = HTTPBearer()


async def get_current_agent(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Agent:
    """
    현재 인증된 상담사 조회

    JWT 토큰을 검증하고 상담사 정보를 반환합니다.

    Args:
        credentials: Bearer 토큰
        db: 데이터베이스 세션

    Returns:
        Agent: 인증된 상담사 객체

    Raises:
        HTTPException: 인증 실패 시 401
    """
    # 토큰 디코딩
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 토큰에서 상담사 ID 추출
    agent_id: str = payload.get("sub")
    if agent_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰에 사용자 정보가 없습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 상담사 조회
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자를 찾을 수 없습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return agent


async def get_current_active_agent(
    current_agent: Agent = Depends(get_current_agent)
) -> Agent:
    """
    현재 활성화된 상담사 조회

    상담사가 온라인 상태인지 확인합니다.

    Args:
        current_agent: 현재 상담사

    Returns:
        Agent: 활성 상담사

    Raises:
        HTTPException: 상담사가 비활성 상태일 때 403
    """
    if current_agent.status == "offline":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="비활성 상태의 계정입니다"
        )

    return current_agent


async def get_current_admin(
    current_agent: Agent = Depends(get_current_agent)
) -> Agent:
    """
    관리자 권한 확인

    Args:
        current_agent: 현재 상담사

    Returns:
        Agent: 관리자

    Raises:
        HTTPException: 관리자가 아닐 때 403
    """
    if current_agent.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다"
        )

    return current_agent
