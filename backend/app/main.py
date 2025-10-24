from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio
import uvicorn

from app.config import settings
from app.socket.handlers import register_socket_handlers

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


# API 라우터 (나중에 추가)
# app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
# app.include_router(agent.router, prefix="/api/agent", tags=["agent"])
# app.include_router(translation.router, prefix="/api/translation", tags=["translation"])


if __name__ == "__main__":
    uvicorn.run(
        "main:socket_app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
