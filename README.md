# MedTranslate - 의료 다국어 실시간 번역 상담 서비스

의료 분야 특화 실시간 다국어 번역 상담 플랫폼입니다. 외국인 환자와 한국 의료진 간의 원활한 소통을 지원합니다.

## 기술 스택

### Backend
- **FastAPI** - 고성능 Python 웹 프레임워크
- **Socket.io** - 실시간 양방향 통신
- **PostgreSQL** - 채팅 로그 저장
- **Redis** - 번역 결과 캐싱
- **Anthropic Claude** - AI 기반 의료 전문 번역

### Frontend
- **Next.js 14** - React 기반 프론트엔드 프레임워크
- **TypeScript** - 타입 안전성
- **Tailwind CSS** - 스타일링
- **Socket.io Client** - 실시간 통신

## 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│              Next.js Frontend (프론트엔드)                │
│        https://chat.medtranslate.co.kr                  │
│  - 고객용 채팅 UI / 상담사용 콘솔 UI                      │
└─────────────────────────────────────────────────────────┘
                        ↓
          WebSocket (Socket.io)  +  REST API
                        ↓
┌─────────────────────────────────────────────────────────┐
│              FastAPI Backend (백엔드)                    │
│  - Socket.io 실시간 통신 서버                            │
│  - AI 번역 엔진 (Claude)                                 │
│  - 상담사 매칭 로직 / 채팅 세션 관리                      │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  PostgreSQL        Redis          S3/Storage            │
│  (채팅 로그)       (캐싱)         (파일 첨부)            │
└─────────────────────────────────────────────────────────┘
```

## 프로젝트 구조

```
medtranslate-v1/
├── backend/                      # FastAPI 백엔드
│   ├── app/
│   │   ├── main.py              # FastAPI + Socket.io 서버
│   │   ├── config.py            # 설정
│   │   ├── api/                 # REST API 라우터
│   │   ├── socket/
│   │   │   └── handlers.py      # Socket.io 핸들러
│   │   ├── services/
│   │   │   ├── translation.py   # 번역 서비스
│   │   │   ├── cache.py         # Redis 캐싱
│   │   │   └── session.py       # 세션 관리
│   │   └── models/
│   │       ├── database.py      # SQLAlchemy 모델
│   │       └── schemas.py       # Pydantic 스키마
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                     # Next.js 프론트엔드
│   ├── app/
│   │   ├── chat/[roomId]/
│   │   │   └── page.tsx         # 고객용 채팅
│   │   └── layout.tsx
│   ├── hooks/
│   │   ├── useSocket.ts         # Socket.io 연결
│   │   └── useChat.ts           # 채팅 로직
│   ├── types/
│   │   └── index.ts             # TypeScript 타입
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml           # 개발 환경 설정
├── .env.example                 # 환경 변수 예제
└── README.md
```

## Quick Start - MVP Demo

### 현재 상태
- ✅ Socket.io 실시간 통신
- ✅ AI 번역 (Mock 모드 - API 키 설정 시 실제 번역)
- ✅ 고객용 채팅 UI
- ✅ 상담사용 콘솔
- ✅ 타이핑 표시
- ✅ 다국어 지원

### 1. 환경 변수 설정

```bash
# Backend 환경변수 (.env 이미 설정됨)
cd backend
# ANTHROPIC_API_KEY=your_api_key (선택사항 - 설정 안하면 Mock 번역 사용)

# Frontend 환경변수 (.env.local 이미 설정됨)
cd frontend
# NEXT_PUBLIC_API_URL=http://localhost:8001
```

### 2. 서비스 실행

#### Backend (포트 8001)

```bash
cd backend

# 가상환경 활성화
source venv/bin/activate  # Windows: venv\Scripts\activate

# 서버 실행 (이미 실행 중이면 생략)
uvicorn app.main:socket_app --host 0.0.0.0 --port 8001 --reload
```

Backend API: http://localhost:8001
API 문서: http://localhost:8001/api/docs

#### Frontend (포트 3000-3009)

```bash
cd frontend

# 개발 서버 실행 (이미 실행 중이면 생략)
npm run dev
```

Frontend: http://localhost:3000 (또는 3001-3009)

### 3. MVP 데모 실행

#### 방법 1: 수동 테스트

1. **채팅방 생성**
   ```bash
   curl -X POST http://localhost:8001/api/chat/rooms \
     -H "Content-Type: application/json" \
     -d '{"customer_language":"vi"}'

   # 응답에서 room_id 확인
   # 예: {"id":"room_abc123","customer_language":"vi",...}
   ```

2. **고객 페이지 접속**
   ```
   http://localhost:3001/chat/room_abc123
   ```

3. **상담사 콘솔 접속** (새 브라우저 탭)
   ```
   http://localhost:3001/agent
   ```
   - "Join Chat" 버튼 클릭하여 대기 중인 채팅방 입장

4. **채팅 테스트**
   - 고객: 베트남어로 메시지 입력 (예: "Xin chào")
   - 상담사: 한국어로 응답 (예: "안녕하세요")
   - 양방향 실시간 번역 확인

#### 방법 2: 자동화 테스트

```bash
# 백엔드와 프론트엔드가 실행 중인 상태에서
cd frontend
node test-e2e-chat.js

# 예상 결과:
# ✅ Customer connected
# ✅ Agent connected
# ✅ Messages sent/received with translations
# ✅ Tests passed: 8
```

## 주요 기능

### 1. 실시간 채팅
- Socket.io를 통한 실시간 양방향 통신
- 타이핑 표시
- 온라인 상태 표시

### 2. AI 번역
- Claude API를 활용한 고품질 의료 전문 번역
- 의료 용어집 기반 정확한 번역
- Redis 캐싱으로 응답 속도 최적화

### 3. 다국어 지원
- 한국어 (ko)
- English (en)
- 日本語 (ja)
- 中文 (zh)
- Tiếng Việt (vi)
- ภาษาไทย (th)

### 4. 세션 관리
- 채팅방 생성 및 관리
- 고객-상담사 매칭
- 세션 상태 추적

## API 엔드포인트

### REST API

- `GET /` - Health check
- `GET /health` - Health status
- `GET /api/docs` - Swagger API 문서

### Socket.io Events (Updated for MVP)

#### 클라이언트 → 서버
- `join_room` - 채팅방 입장
  ```json
  {
    "room_id": "room_abc123",
    "user_type": "customer" | "agent",
    "language": "vi",
    "agent_id": "agent_001" // agent만
  }
  ```
- `send_message` - 메시지 전송 (통합 이벤트)
  ```json
  {
    "room_id": "room_abc123",
    "text": "메시지 내용",
    "language": "vi" | "ko"
  }
  ```
- `typing` - 타이핑 시작
- `stop_typing` - 타이핑 중지
- `end_chat` - 채팅 종료

#### 서버 → 클라이언트
- `connected` - 연결 확인
- `joined_room` - 입장 확인
- `new_message` - 메시지 수신 (통합 이벤트)
  ```json
  {
    "sender_type": "customer" | "agent",
    "text": "원문",
    "translated_text": "번역문",
    "source_lang": "vi",
    "target_lang": "ko"
  }
  ```
- `typing` - 상대방 타이핑 중
- `stop_typing` - 타이핑 중지
- `agent_online` / `customer_online` - 상대방 온라인
- `chat_ended` - 채팅 종료

## 번역 흐름

1. **고객 메시지** (예: 베트남어)
   - 고객이 베트남어로 메시지 입력
   - Socket.io로 서버 전송
   - Claude API로 한국어 번역
   - 번역 결과 Redis에 캐싱
   - 상담사에게 원문 + 번역 전송

2. **상담사 메시지** (한국어)
   - 상담사가 한국어로 메시지 입력
   - Socket.io로 서버 전송
   - Claude API로 고객 언어(베트남어) 번역
   - 번역 결과 캐싱
   - 고객에게 번역된 메시지 전송

## 개발 로드맵

### Phase 1: 프로젝트 기반 설정 (완료 ✅)
- [x] 프로젝트 구조 및 디렉토리 설정
- [x] 개발 환경 설정 (VSCode, Git)
- [x] ERD 및 데이터베이스 스키마 설계
- [x] 데이터베이스 마이그레이션 설정

### Phase 2: REST API & 번역 엔진 (완료 ✅)
- [x] FastAPI 백엔드 기본 구조
- [x] Socket.io 실시간 통신 서버
- [x] 번역 서비스 (Claude API with Mock fallback)
- [x] Redis 캐싱 시스템
- [x] REST API 엔드포인트 (채팅방, 메시지, 모니터링)
- [x] 에러 핸들링 및 재시도 로직

### Phase 3: 고객 UI (완료 ✅)
- [x] Next.js 프론트엔드 설정
- [x] 고객용 채팅 페이지
- [x] 반응형 UI 컴포넌트
- [x] 언어 선택기
- [x] 타이핑 표시
- [x] 연결 상태 표시

### Phase 4: 상담사 콘솔 (MVP 완료 ✅)
- [x] 상담사용 콘솔 페이지
- [x] 대기 중인 채팅방 목록
- [x] 상담사 채팅 페이지
- [x] 실시간 채팅 및 번역

### 향후 계획
- [ ] 데이터베이스 연동 (메시지 저장)
- [ ] 인증/권한 시스템
- [ ] 파일 첨부 기능
- [ ] 채팅 히스토리
- [ ] 통계 및 모니터링 대시보드
- [ ] 상담사 배정 로직
- [ ] 알림 시스템

## 환경 변수

### Backend (.env)
```
ANTHROPIC_API_KEY=your_api_key
DATABASE_URL=postgresql://user:pass@localhost:5432/medtranslate
REDIS_URL=redis://localhost:6379
DEBUG=True
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 라이센스

Private

## 문의

프로젝트 관련 문의사항이 있으시면 이슈를 생성해주세요.
