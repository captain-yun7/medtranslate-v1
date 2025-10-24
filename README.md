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

## 시작하기

### 1. 환경 변수 설정

```bash
# 프로젝트 루트에서
cp .env.example .env

# .env 파일을 열어 API 키 설정
ANTHROPIC_API_KEY=your_api_key_here
```

### 2. Docker Compose로 실행

```bash
# 모든 서비스 시작 (백엔드, 프론트엔드, DB, Redis)
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

### 3. 개별 서비스 실행

#### Backend

```bash
cd backend

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# .env 파일 설정
cp .env.example .env

# 서버 실행
uvicorn app.main:socket_app --reload
```

Backend API: http://localhost:8000
API 문서: http://localhost:8000/api/docs

#### Frontend

```bash
cd frontend

# 의존성 설치
npm install

# .env.local 설정
cp .env.local.example .env.local

# 개발 서버 실행
npm run dev
```

Frontend: http://localhost:3000

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

### Socket.io Events

#### 클라이언트 → 서버
- `join_room` - 채팅방 입장
- `customer_message` - 고객 메시지 전송
- `agent_message` - 상담사 메시지 전송
- `typing` - 타이핑 시작
- `stop_typing` - 타이핑 중지
- `end_chat` - 채팅 종료

#### 서버 → 클라이언트
- `connected` - 연결 확인
- `joined_room` - 입장 확인
- `customer_receive_message` - 고객 메시지 수신
- `agent_receive_message` - 상담사 메시지 수신
- `message_sent` - 발신 확인
- `user_typing` - 상대방 타이핑 중
- `user_stop_typing` - 타이핑 중지
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

- [x] 백엔드 기본 구조 및 Socket.io 서버
- [x] 번역 서비스 (Claude API)
- [x] 세션 관리
- [x] 프론트엔드 기본 UI
- [x] 고객용 채팅 페이지
- [ ] 상담사용 콘솔
- [ ] 데이터베이스 연동
- [ ] 인증/권한 시스템
- [ ] 파일 첨부 기능
- [ ] 채팅 히스토리
- [ ] 통계 및 모니터링

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
