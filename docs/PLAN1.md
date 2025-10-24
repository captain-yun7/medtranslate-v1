# 완벽한 선택입니다! 👍

Next.js (Frontend) + FastAPI (Backend)가 **가장 확장성 있고 프로페셔널한 구성**입니다.

---

## 1. 최종 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│                    사용자 레이어                          │
├─────────────────────────────────────────────────────────┤
│  고객 (병원 사이트)              상담사 (관리 콘솔)        │
│  https://www.hospital-a.com     https://admin.medtranslate.co.kr │
│         ↓ (iframe)                      ↓                │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│              Next.js Frontend (프론트엔드)                │
│        https://chat.medtranslate.co.kr                  │
│  ┌──────────────────────────────────────────────┐       │
│  │ - 고객용 채팅 UI                              │       │
│  │ - 상담사용 콘솔 UI                            │       │
│  │ - 언어 선택, 메시지 입력                      │       │
│  │ - 실시간 메시지 렌더링                        │       │
│  └──────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────┘
                        ↓
          WebSocket (Socket.io)  +  REST API
                        ↓
┌─────────────────────────────────────────────────────────┐
│              FastAPI Backend (백엔드)                    │
│          https://api.medtranslate.co.kr                 │
│  ┌──────────────────────────────────────────────┐       │
│  │ - Socket.io 실시간 통신 서버                  │       │
│  │ - AI 번역 엔진 (Claude/GPT/DeepL)            │       │
│  │ - 상담사 매칭 로직                            │       │
│  │ - 채팅 세션 관리                              │       │
│  │ - 인증/권한 관리                              │       │
│  │ - 번역 캐싱                                   │       │
│  └──────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│                   데이터 레이어                          │
├─────────────────────────────────────────────────────────┤
│  PostgreSQL        Redis          S3/Storage            │
│  (채팅 로그)       (캐싱)         (파일 첨부)            │
└─────────────────────────────────────────────────────────┘
```

---

## 2. 프로젝트 구조

```
medtranslate/
├── frontend/                      # Next.js 프론트엔드
│   ├── app/
│   │   ├── chat/
│   │   │   └── [roomId]/
│   │   │       └── page.tsx       # 고객용 채팅
│   │   ├── agent/
│   │   │   ├── dashboard/
│   │   │   │   └── page.tsx       # 상담사 대시보드
│   │   │   └── console/
│   │   │       └── [roomId]/
│   │   │           └── page.tsx   # 상담사 채팅 콘솔
│   │   ├── embed/
│   │   │   └── page.tsx           # iframe 임베드용
│   │   └── layout.tsx
│   │
│   ├── components/
│   │   ├── Chat/
│   │   │   ├── CustomerChat.tsx
│   │   │   ├── AgentChat.tsx
│   │   │   ├── MessageList.tsx
│   │   │   ├── MessageInput.tsx
│   │   │   └── LanguageSelector.tsx
│   │   └── ui/                    # shadcn/ui
│   │
│   ├── lib/
│   │   ├── socket.ts              # Socket.io 클라이언트
│   │   ├── api.ts                 # API 호출 함수
│   │   └── utils.ts
│   │
│   ├── hooks/
│   │   ├── useChat.ts
│   │   └── useSocket.ts
│   │
│   ├── types/
│   │   └── index.ts
│   │
│   ├── public/
│   │   └── widget.js              # 외부 임베드 스크립트
│   │
│   ├── .env.local
│   ├── next.config.js
│   ├── package.json
│   └── tsconfig.json
│
├── backend/                       # FastAPI 백엔드
│   ├── app/
│   │   ├── main.py                # FastAPI 앱 + Socket.io
│   │   ├── config.py              # 설정
│   │   │
│   │   ├── api/
│   │   │   ├── chat.py            # 채팅 REST API
│   │   │   ├── agent.py           # 상담사 API
│   │   │   ├── translation.py     # 번역 API
│   │   │   └── webhook.py         # 웹훅
│   │   │
│   │   ├── socket/
│   │   │   ├── handlers.py        # Socket.io 핸들러
│   │   │   └── events.py          # 이벤트 정의
│   │   │
│   │   ├── services/
│   │   │   ├── translation.py     # 번역 서비스
│   │   │   ├── cache.py           # 캐싱 서비스
│   │   │   ├── session.py         # 세션 관리
│   │   │   └── matching.py        # 상담사 매칭
│   │   │
│   │   ├── models/
│   │   │   ├── database.py        # SQLAlchemy 모델
│   │   │   └── schemas.py         # Pydantic 스키마
│   │   │
│   │   └── utils/
│   │       ├── auth.py            # 인증
│   │       └── helpers.py
│   │
│   ├── tests/
│   ├── alembic/                   # DB 마이그레이션
│   ├── .env
│   ├── requirements.txt
│   └── Dockerfile
│
├── shared/                        # 공통 타입 정의 (선택)
│   └── types.ts
│
├── infrastructure/                # 인프라 코드
│   ├── docker-compose.yml
│   ├── docker-compose.prod.yml
│   └── nginx/
│       └── nginx.conf
│
└── docs/                          # 문서
    ├── API.md
    └── DEPLOYMENT.md
```

---

## 3. 백엔드 (FastAPI) 구현

### A. main.py (핵심 서버)

```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio
import uvicorn

from app.config import settings
from app.api import chat, agent, translation
from app.socket.handlers import register_socket_handlers

# FastAPI 앱
app = FastAPI(
    title="MedTranslate API",
    version="1.0.0",
    docs_url="/api/docs",
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://chat.medtranslate.co.kr",
        "https://admin.medtranslate.co.kr",
        "http://localhost:3000",
        "http://localhost:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Socket.io 서버
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=[
        "https://chat.medtranslate.co.kr",
        "https://admin.medtranslate.co.kr",
        "http://localhost:3000",
        "http://localhost:3001",
    ],
    logger=True,
    engineio_logger=True,
)

# Socket.io 핸들러 등록
register_socket_handlers(sio)

# Socket.io를 FastAPI에 마운트
socket_app = socketio.ASGIApp(sio, app)

# REST API 라우터
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(agent.router, prefix="/api/agent", tags=["agent"])
app.include_router(translation.router, prefix="/api/translation", tags=["translation"])

@app.get("/")
async def root():
    return {"message": "MedTranslate API Server"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:socket_app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
```

### B. Socket.io 핸들러

```python
# backend/app/socket/handlers.py
import socketio
from typing import Dict
from app.services.translation import TranslationService
from app.services.session import SessionManager
from app.models.database import save_message
import logging

logger = logging.getLogger(__name__)

# 활성 세션 관리
session_manager = SessionManager()
translation_service = TranslationService()

def register_socket_handlers(sio: socketio.AsyncServer):
    
    @sio.on('connect')
    async def connect(sid, environ):
        logger.info(f"Client connected: {sid}")
        await sio.emit('connected', {'sid': sid}, room=sid)
    
    @sio.on('disconnect')
    async def disconnect(sid):
        logger.info(f"Client disconnected: {sid}")
        # 세션 정리
        await session_manager.remove_connection(sid)
    
    @sio.on('join_room')
    async def join_room(sid, data):
        """
        채팅방 입장
        data = {
            'room_id': 'room_123',
            'user_type': 'customer' | 'agent',
            'customer_language': 'vi',  # 고객인 경우
            'agent_id': 'agent_001'     # 상담사인 경우
        }
        """
        room_id = data['room_id']
        user_type = data['user_type']
        
        # Socket.io 룸 입장
        await sio.enter_room(sid, room_id)
        
        # 세션에 연결 정보 저장
        await session_manager.add_connection(
            room_id=room_id,
            sid=sid,
            user_type=user_type,
            language=data.get('customer_language'),
            agent_id=data.get('agent_id')
        )
        
        logger.info(f"{user_type} joined room {room_id}: {sid}")
        
        # 입장 확인
        await sio.emit('joined_room', {
            'room_id': room_id,
            'user_type': user_type
        }, room=sid)
        
        # 상대방이 이미 있으면 알림
        session = await session_manager.get_session(room_id)
        if user_type == 'agent' and session.get('customer_sid'):
            await sio.emit('customer_online', {
                'language': session['customer_language']
            }, room=sid)
        elif user_type == 'customer' and session.get('agent_sid'):
            await sio.emit('agent_online', {}, room=sid)
    
    @sio.on('customer_message')
    async def handle_customer_message(sid, data):
        """
        고객 메시지 처리
        data = {
            'room_id': 'room_123',
            'message': 'Xin chào',
            'timestamp': '2025-10-24T...'
        }
        """
        room_id = data['room_id']
        message = data['message']
        
        # 세션 정보 가져오기
        session = await session_manager.get_session(room_id)
        if not session:
            await sio.emit('error', {
                'message': 'Session not found'
            }, room=sid)
            return
        
        source_lang = session['customer_language']
        
        try:
            # 1. 한국어로 번역
            translated = await translation_service.translate(
                text=message,
                source_lang=source_lang,
                target_lang='ko',
                context='medical'
            )
            
            # 2. DB에 저장
            await save_message(
                room_id=room_id,
                sender_type='customer',
                original_text=message,
                translated_text=translated,
                source_lang=source_lang,
                target_lang='ko'
            )
            
            # 3. 상담사에게 전송 (원문 + 번역)
            agent_sid = session.get('agent_sid')
            if agent_sid:
                await sio.emit('agent_receive_message', {
                    'message_id': f"msg_{data['timestamp']}",
                    'original': message,
                    'translated': translated,
                    'source_lang': source_lang,
                    'timestamp': data['timestamp']
                }, room=agent_sid)
            
            # 4. 고객에게 발신 확인
            await sio.emit('message_sent', {
                'message_id': f"msg_{data['timestamp']}",
                'message': message,
                'timestamp': data['timestamp']
            }, room=sid)
            
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            await sio.emit('error', {
                'message': 'Translation failed',
                'detail': str(e)
            }, room=sid)
    
    @sio.on('agent_message')
    async def handle_agent_message(sid, data):
        """
        상담사 메시지 처리
        data = {
            'room_id': 'room_123',
            'message': '안녕하세요, 무엇을 도와드릴까요?',
            'timestamp': '2025-10-24T...'
        }
        """
        room_id = data['room_id']
        message = data['message']
        
        # 세션 정보
        session = await session_manager.get_session(room_id)
        if not session:
            return
        
        target_lang = session['customer_language']
        
        try:
            # 1. 고객 언어로 번역
            translated = await translation_service.translate(
                text=message,
                source_lang='ko',
                target_lang=target_lang,
                context='medical'
            )
            
            # 2. DB 저장
            await save_message(
                room_id=room_id,
                sender_type='agent',
                original_text=message,
                translated_text=translated,
                source_lang='ko',
                target_lang=target_lang
            )
            
            # 3. 고객에게 전송 (번역된 메시지만)
            customer_sid = session.get('customer_sid')
            if customer_sid:
                await sio.emit('customer_receive_message', {
                    'message_id': f"msg_{data['timestamp']}",
                    'message': translated,
                    'timestamp': data['timestamp']
                }, room=customer_sid)
            
            # 4. 상담사에게 발신 확인 (원문 + 번역 미리보기)
            await sio.emit('message_sent', {
                'message_id': f"msg_{data['timestamp']}",
                'original': message,
                'translated': translated,
                'target_lang': target_lang,
                'timestamp': data['timestamp']
            }, room=sid)
            
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            await sio.emit('error', {
                'message': 'Translation failed'
            }, room=sid)
    
    @sio.on('typing')
    async def handle_typing(sid, data):
        """타이핑 표시"""
        room_id = data['room_id']
        user_type = data['user_type']
        
        session = await session_manager.get_session(room_id)
        
        # 상대방에게만 전송
        if user_type == 'customer':
            agent_sid = session.get('agent_sid')
            if agent_sid:
                await sio.emit('user_typing', {
                    'user_type': 'customer'
                }, room=agent_sid)
        else:
            customer_sid = session.get('customer_sid')
            if customer_sid:
                await sio.emit('user_typing', {
                    'user_type': 'agent'
                }, room=customer_sid)
    
    @sio.on('stop_typing')
    async def handle_stop_typing(sid, data):
        """타이핑 중지"""
        room_id = data['room_id']
        user_type = data['user_type']
        
        session = await session_manager.get_session(room_id)
        
        if user_type == 'customer':
            agent_sid = session.get('agent_sid')
            if agent_sid:
                await sio.emit('user_stop_typing', {}, room=agent_sid)
        else:
            customer_sid = session.get('customer_sid')
            if customer_sid:
                await sio.emit('user_stop_typing', {}, room=customer_sid)
    
    @sio.on('end_chat')
    async def handle_end_chat(sid, data):
        """채팅 종료"""
        room_id = data['room_id']
        
        # 세션 종료 처리
        await session_manager.end_session(room_id)
        
        # 룸의 모든 참가자에게 알림
        await sio.emit('chat_ended', {
            'room_id': room_id,
            'ended_by': data.get('ended_by', 'user')
        }, room=room_id)
        
        # 룸 정리
        await sio.leave_room(sid, room_id)
```

### C. 번역 서비스

```python
# backend/app/services/translation.py
from anthropic import AsyncAnthropic
from typing import Optional
import hashlib
import json
from app.services.cache import cache_service
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class TranslationService:
    def __init__(self):
        self.claude = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.medical_glossary = self._load_glossary()
    
    def _load_glossary(self):
        """의료 용어집 로드"""
        return {
            "ko": {
                "예약": {"en": "appointment", "vi": "lịch hẹn", "ja": "予約", "zh": "预约", "th": "การนัดหมาย"},
                "진료": {"en": "consultation", "vi": "khám bệnh", "ja": "診察", "zh": "就诊", "th": "การตรวจรักษา"},
                "처방전": {"en": "prescription", "vi": "đơn thuốc", "ja": "処方箋", "zh": "处方", "th": "ใบสั่งยา"},
                "증상": {"en": "symptom", "vi": "triệu chứng", "ja": "症状", "zh": "症状", "th": "อาการ"},
                # ... 더 많은 용어
            }
        }
    
    async def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        context: str = 'medical'
    ) -> str:
        """
        AI 번역 (캐싱 포함)
        """
        # 1. 캐시 확인
        cache_key = self._get_cache_key(text, source_lang, target_lang)
        cached = await cache_service.get(cache_key)
        if cached:
            logger.info(f"Cache hit for: {text[:30]}...")
            return cached
        
        # 2. AI 번역
        try:
            translated = await self._translate_with_claude(
                text, source_lang, target_lang, context
            )
            
            # 3. 캐시 저장 (30일)
            await cache_service.set(cache_key, translated, expire=2592000)
            
            return translated
            
        except Exception as e:
            logger.error(f"Translation failed: {str(e)}")
            raise
    
    async def _translate_with_claude(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        context: str
    ) -> str:
        """Claude API로 번역"""
        
        # 용어집 컨텍스트 생성
        glossary_context = self._create_glossary_context(source_lang, target_lang)
        
        # 언어별 이름 매핑
        lang_names = {
            'ko': '한국어',
            'en': 'English',
            'ja': '日本語',
            'zh': '中文',
            'vi': 'Tiếng Việt',
            'th': 'ภาษาไทย'
        }
        
        prompt = f"""당신은 의료 전문 통역사입니다.
다음 의료 상담 메시지를 {lang_names.get(target_lang, target_lang)}로 정확하게 번역해주세요.

원문 언어: {lang_names.get(source_lang, source_lang)}
원문: {text}

의료 용어 참고:
{glossary_context}

번역 시 주의사항:
1. 의료 용어는 정확하게 번역
2. 환자/의료진의 의도와 감정을 정확히 전달
3. 격식있고 공손한 표현 사용
4. 증상이나 통증 표현은 명확하게 번역
5. 문화적 차이를 고려한 자연스러운 표현

번역문만 출력하세요. 설명이나 주석 없이 번역 결과만 제공하세요."""

        message = await self.claude.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        return message.content[0].text.strip()
    
    def _create_glossary_context(self, source_lang: str, target_lang: str) -> str:
        """용어집 컨텍스트 생성"""
        if source_lang not in self.medical_glossary:
            return ""
        
        context_lines = []
        for ko_term, translations in list(self.medical_glossary[source_lang].items())[:20]:
            if target_lang in translations:
                target_term = translations[target_lang]
                context_lines.append(f"- {ko_term} → {target_term}")
        
        return "\n".join(context_lines)
    
    def _get_cache_key(self, text: str, source_lang: str, target_lang: str) -> str:
        """캐시 키 생성"""
        content = f"{text}:{source_lang}:{target_lang}"
        hash_key = hashlib.md5(content.encode()).hexdigest()
        return f"trans:{hash_key}"

# 싱글톤 인스턴스
translation_service = TranslationService()
```

### D. 세션 관리

```python
# backend/app/services/session.py
from typing import Dict, Optional
import asyncio
from datetime import datetime

class SessionManager:
    def __init__(self):
        # 활성 세션 저장
        # room_id -> session_data
        self.sessions: Dict[str, dict] = {}
        # sid -> room_id 매핑
        self.sid_to_room: Dict[str, str] = {}
    
    async def add_connection(
        self,
        room_id: str,
        sid: str,
        user_type: str,
        language: Optional[str] = None,
        agent_id: Optional[str] = None
    ):
        """연결 추가"""
        if room_id not in self.sessions:
            self.sessions[room_id] = {
                'customer_sid': None,
                'agent_sid': None,
                'customer_language': None,
                'agent_id': None,
                'created_at': datetime.now().isoformat(),
                'status': 'waiting'
            }
        
        session = self.sessions[room_id]
        
        if user_type == 'customer':
            session['customer_sid'] = sid
            session['customer_language'] = language
        else:  # agent
            session['agent_sid'] = sid
            session['agent_id'] = agent_id
            session['status'] = 'active'
        
        self.sid_to_room[sid] = room_id
    
    async def remove_connection(self, sid: str):
        """연결 제거"""
        if sid in self.sid_to_room:
            room_id = self.sid_to_room[sid]
            if room_id in self.sessions:
                session = self.sessions[room_id]
                if session['customer_sid'] == sid:
                    session['customer_sid'] = None
                elif session['agent_sid'] == sid:
                    session['agent_sid'] = None
                    session['status'] = 'waiting'
            
            del self.sid_to_room[sid]
    
    async def get_session(self, room_id: str) -> Optional[dict]:
        """세션 정보 가져오기"""
        return self.sessions.get(room_id)
    
    async def end_session(self, room_id: str):
        """세션 종료"""
        if room_id in self.sessions:
            session = self.sessions[room_id]
            # sid_to_room 정리
            if session['customer_sid']:
                self.sid_to_room.pop(session['customer_sid'], None)
            if session['agent_sid']:
                self.sid_to_room.pop(session['agent_sid'], None)
            
            # 세션 삭제
            del self.sessions[room_id]
    
    async def get_waiting_rooms(self) -> list:
        """대기 중인 채팅방 목록"""
        waiting = []
        for room_id, session in self.sessions.items():
            if session['status'] == 'waiting' and session['customer_sid']:
                waiting.append({
                    'room_id': room_id,
                    'customer_language': session['customer_language'],
                    'created_at': session['created_at']
                })
        return waiting

# 싱글톤 인스턴스
session_manager = SessionManager()
```

---

## 4. 프론트엔드 (Next.js) 구현

### A. Socket.io 클라이언트 훅

```typescript
// frontend/hooks/useSocket.ts
import { useEffect, useState, useRef } from 'react';
import { io, Socket } from 'socket.io-client';

const SOCKET_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export function useSocket() {
  const [isConnected, setIsConnected] = useState(false);
  const socketRef = useRef<Socket | null>(null);

  useEffect(() => {
    const socket = io(SOCKET_URL, {
      transports: ['websocket'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5,
    });

    socket.on('connect', () => {
      console.log('Socket connected:', socket.id);
      setIsConnected(true);
    });

    socket.on('disconnect', () => {
      console.log('Socket disconnected');
      setIsConnected(false);
    });

    socket.on('error', (error) => {
      console.error('Socket error:', error);
    });

    socketRef.current = socket;

    return () => {
      socket.disconnect();
    };
  }, []);

  return {
    socket: socketRef.current,
    isConnected,
  };
}
```

### B. 채팅 훅

```typescript
// frontend/hooks/useChat.ts
import { useState, useEffect, useCallback } from 'react';
import { Socket } from 'socket.io-client';

export interface Message {
  id: string;
  type: 'sent' | 'received';
  text: string;
  original?: string;
  translated?: string;
  timestamp: string;
  sourceLang?: string;
}

interface UseChatProps {
  socket: Socket | null;
  roomId: string;
  userType: 'customer' | 'agent';
  language?: string;
}

export function useChat({ socket, roomId, userType, language }: UseChatProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [isOnline, setIsOnline] = useState(false);

  useEffect(() => {
    if (!socket) return;

    // 방 입장
    socket.emit('join_room', {
      room_id: roomId,
      user_type: userType,
      customer_language: language,
    });

    // 입장 확인
    socket.on('joined_room', (data) => {
      console.log('Joined room:', data);
    });

    // 메시지 수신
    if (userType === 'customer') {
      socket.on('customer_receive_message', (data) => {
        setMessages(prev => [...prev, {
          id: data.message_id,
          type: 'received',
          text: data.message,
          timestamp: data.timestamp,
        }]);
      });

      socket.on('message_sent', (data) => {
        setMessages(prev => [...prev, {
          id: data.message_id,
          type: 'sent',
          text: data.message,
          timestamp: data.timestamp,
        }]);
      });

      socket.on('agent_online', () => {
        setIsOnline(true);
      });
    } else {
      // agent
      socket.on('agent_receive_message', (data) => {
        setMessages(prev => [...prev, {
          id: data.message_id,
          type: 'received',
          original: data.original,
          translated: data.translated,
          text: data.translated,
          sourceLang: data.source_lang,
          timestamp: data.timestamp,
        }]);
      });

      socket.on('message_sent', (data) => {
        setMessages(prev => [...prev, {
          id: data.message_id,
          type: 'sent',
          text: data.original,
          translated: data.translated,
          timestamp: data.timestamp,
        }]);
      });

      socket.on('customer_online', (data) => {
        setIsOnline(true);
      });
    }

    // 타이핑 표시
    socket.on('user_typing', () => {
      setIsTyping(true);
    });

    socket.on('user_stop_typing', () => {
      setIsTyping(false);
    });

    // 채팅 종료
    socket.on('chat_ended', () => {
      console.log('Chat ended');
    });

    return () => {
      socket.off('joined_room');
      socket.off('customer_receive_message');
      socket.off('agent_receive_message');
      socket.off('message_sent');
      socket.off('user_typing');
      socket.off('user_stop_typing');
      socket.off('chat_ended');
    };
  }, [socket, roomId, userType, language]);

  const sendMessage = useCallback((message: string) => {
    if (!socket || !message.trim()) return;

    const event = userType === 'customer' ? 'customer_message' : 'agent_message';
    
    socket.emit(event, {
      room_id: roomId,
      message: message,
      timestamp: new Date().toISOString(),
    });
  }, [socket, roomId, userType]);

  const sendTyping = useCallback(() => {
    if (!socket) return;
    socket.emit('typing', {
      room_id: roomId,
      user_type: userType,
    });
  }, [socket, roomId, userType]);

  const sendStopTyping = useCallback(() => {
    if (!socket) return;
    socket.emit('stop_typing', {
      room_id: roomId,
      user_type: userType,
    });
  }, [socket, roomId, userType]);

  const endChat = useCallback(() => {
    if (!socket) return;
    socket.emit('end_chat', {
      room_id: roomId,
      ended_by: userType,
    });
  }, [socket, roomId, userType]);

  return {
    messages,
    isTyping,
    isOnline,
    sendMessage,
    sendTyping,
    sendStopTyping,
    endChat,
  };
}
```

### C. 고객용 채팅 컴포넌트

```typescript
// frontend/app/chat/[roomId]/page.tsx
'use client';

import { useState, useRef, useEffect } from 'react';
import { useSocket } from '@/hooks/useSocket';
import { useChat } from '@/hooks/useChat';

export default function ChatPage({ params }: { params: { roomId: string } }) {
  const { socket, isConnected } = useSocket();
  const [inputText, setInputText] = useState('');
  const [language, setLanguage] = useState('vi');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const {
    messages,
    isTyping,
    isOnline,
    sendMessage,
    sendTyping,
    sendStopTyping,
  } = useChat({
    socket,
    roomId: params.roomId,
    userType: 'customer',
    language,
  });

  // 자동 스크롤
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = () => {
    if (!inputText.trim()) return;
    sendMessage(inputText);
    setInputText('');
    sendStopTyping();
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputText(e.target.value);
    sendTyping();
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* 헤더 */}
      <div className="bg-blue-600 text-white p-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className={`w-3 h-3 rounded-full ${isOnline ? 'bg-green-400' : 'bg-gray-400'}`} />
          <h1 className="text-lg font-semibold">의료 상담</h1>
        </div>
        <div className={`text-sm ${isConnected ? 'text-green-200' : 'text-red-200'}`}>
          {isConnected ? '연결됨' : '연결 중...'}
        </div>
      </div>

      {/* 언어 선택 */}
      <div className="p-3 bg-white border-b">
        <select
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          className="w-full p-2 border rounded-lg"
        >
          <option value="en">English</option>
          <option value="ja">日本語</option>
          <option value="zh">中文</option>
          <option value="th">ภาษาไทย</option>
          <option value="vi">Tiếng Việt</option>
        </select>
      </div>

      {/* 메시지 영역 */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.type === 'sent' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[70%] rounded-lg p-3 ${
                msg.type === 'sent'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white border border-gray-200'
              }`}
            >
              <p className="text-sm">{msg.text}</p>
              <span className="text-xs opacity-70 mt-1 block">
                {new Date(msg.timestamp).toLocaleTimeString()}
              </span>
            </div>
          </div>
        ))}

        {isTyping && (
          <div className="flex justify-start">
            <div className="bg-gray-200 rounded-lg p-3">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-100" />
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-200" />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* 입력 영역 */}
      <div className="p-4 bg-white border-t">
        <div className="flex gap-2">
          <input
            type="text"
            value={inputText}
            onChange={handleInputChange}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="메시지를 입력하세요..."
            className="flex-1 p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={handleSend}
            disabled={!inputText.trim() || !isConnected}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            전송
          </button>
        </div>
      </div>
    </div>
  );
}
```

---

## 5. 배포 및 인프라

### docker-compose.yml

```yaml
version: '3.8'

services:
  # FastAPI 백엔드
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/medtranslate
      - REDIS_URL=redis://redis:6379
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    depends_on:
      - db
      - redis
    volumes:
      - ./backend:/app
    command: uvicorn app.main:socket_app --host 0.0.0.0 --port 8000 --reload

  # Next.js 프론트엔드 (고객용)
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev

  # PostgreSQL
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: medtranslate
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  # Redis
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

---

## 6. 개발 일정 (10주)

```
Week 1-2: 백엔드 기반 구축
  - FastAPI 프로젝트 셋업
  - Socket.io 서버 구현
  - 데이터베이스 스키마 설계
  - 기본 API 엔드포인트

Week 3-4: 번역 엔진 통합
  - Claude API 통합
  - 번역 서비스 구현
  - 캐싱 시스템 (Redis)
  - 의료 용어집 구축 (1000개)

Week 5-6: 프론트엔드 개발
  - Next.js 프로젝트 셋업
  - 고객용 채팅 UI
  - Socket.io 클라이언트 통합
  - 반응형 디자인

Week 7-8: 상담사 콘솔
  - 상담사 대시보드
  - 멀티채팅 관리
  - 번역 미리보기 UI
  - 빠른 답변 템플릿

Week 9: 통합 테스트
  - 부하 테스트
  - 번역 품질 테스트
  - 실제 상담사 파일럿

Week 10: 배포 및 최적화
  - 프로덕션 배포
  - 모니터링 설정
  - 문서 작성
```

---

## 7. 최종 비용 견적

### 개발 비용
- **백엔드 개발**: ₩20,000,000
- **프론트엔드 개발**: ₩18,000,000
- **AI 통합**: ₩10,000,000
- **QA/테스트**: ₩7,000,000
- **총 개발 비용**: **₩55,000,000**

### 월 운영 비용 (동시 50명 기준)
- AWS EC2 (Backend): ₩400,000
- RDS PostgreSQL: ₩300,000
- Redis: ₩150,000
- Vercel Pro (Frontend): ₩25,000
- Claude API: ₩600,000
- **월 총 비용**: **₩1,475,000**

---

완벽한 선택하셨습니다! 더 궁금한 점 있으시면 말씀해주세요! 🚀