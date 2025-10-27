from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio
import uvicorn

from app.config import settings
from app.socket.handlers import register_socket_handlers
from app.routers import chat, monitoring
from app.services.cache import cache_service

# FastAPI 앱
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/api/docs",
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Socket.io 서버
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=settings.CORS_ORIGINS,
    logger=True,
    engineio_logger=True,
)

# Socket.io 핸들러 등록
register_socket_handlers(sio)

# Socket.io를 FastAPI에 마운트
socket_app = socketio.ASGIApp(sio, app)


@app.get("/")
async def root():
    return {"message": "MedTranslate API Server"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.on_event("startup")
async def startup_event():
    """앱 시작 시 초기화"""
    # Redis 연결
    await cache_service.connect()


# API 라우터
app.include_router(chat.router)
app.include_router(monitoring.router)


if __name__ == "__main__":
    uvicorn.run(
        "main:socket_app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
