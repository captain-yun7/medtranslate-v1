# MedTranslate ERD (Entity Relationship Diagram)

## 데이터베이스 스키마 다이어그램

```
┌─────────────────────────────┐
│        chat_rooms           │
├─────────────────────────────┤
│ id (PK)              STRING │
│ customer_language    STRING │
│ agent_id (FK)        STRING │
│ status               STRING │
│ created_at          DATETIME│
│ ended_at            DATETIME│
│ metadata              JSON  │
└─────────────────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────────────────┐
│         messages            │
├─────────────────────────────┤
│ id (PK)                 INT │
│ room_id (FK)         STRING │
│ sender_type          STRING │
│ sender_id            STRING │
│ original_text          TEXT │
│ original_language    STRING │
│ translated_text        TEXT │
│ target_language      STRING │
│ timestamp           DATETIME│
│ metadata              JSON  │
└─────────────────────────────┘


┌─────────────────────────────┐        ┌─────────────────────────────┐
│          agents             │        │      customer_sessions      │
├─────────────────────────────┤        ├─────────────────────────────┤
│ id (PK)              STRING │        │ id (PK)              STRING │
│ name                 STRING │        │ ip_address           STRING │
│ email                STRING │        │ user_agent           STRING │
│ password_hash        STRING │        │ language             STRING │
│ role                 STRING │        │ created_at          DATETIME│
│ status               STRING │        │ last_active         DATETIME│
│ max_concurrent_chats    INT │        │ metadata              JSON  │
│ created_at          DATETIME│        └─────────────────────────────┘
│ last_login          DATETIME│
└─────────────────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────────────────┐
│      agent_sessions         │
├─────────────────────────────┤
│ id (PK)              STRING │
│ agent_id (FK)        STRING │
│ token                STRING │
│ created_at          DATETIME│
│ expires_at          DATETIME│
│ ip_address           STRING │
└─────────────────────────────┘


┌─────────────────────────────┐
│    translation_cache        │
├─────────────────────────────┤
│ id (PK)              STRING │
│ source_text            TEXT │
│ source_lang          STRING │
│ target_lang          STRING │
│ translated_text        TEXT │
│ created_at          DATETIME│
│ hit_count               INT │
└─────────────────────────────┘


┌─────────────────────────────┐
│     medical_glossary        │
├─────────────────────────────┤
│ id (PK)                 INT │
│ term_ko              STRING │
│ term_en              STRING │
│ term_ja              STRING │
│ term_zh              STRING │
│ term_vi              STRING │
│ term_th              STRING │
│ category             STRING │
│ usage_count             INT │
│ created_at          DATETIME│
│ updated_at          DATETIME│
└─────────────────────────────┘


┌─────────────────────────────┐
│      quick_responses        │
├─────────────────────────────┤
│ id (PK)                 INT │
│ category             STRING │
│ title                STRING │
│ content_ko             TEXT │
│ content_en             TEXT │
│ content_ja             TEXT │
│ content_zh             TEXT │
│ content_vi             TEXT │
│ content_th             TEXT │
│ usage_count             INT │
│ created_at          DATETIME│
│ updated_at          DATETIME│
└─────────────────────────────┘
```

## 테이블 상세 설명

### 1. `chat_rooms` (채팅방)
채팅 세션을 관리하는 테이블

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | VARCHAR(50) | PRIMARY KEY | 채팅방 고유 ID |
| customer_language | VARCHAR(10) | NOT NULL | 고객 언어 (ko, en, ja, zh, vi, th) |
| agent_id | VARCHAR(50) | FOREIGN KEY → agents.id | 배정된 상담사 ID (NULL 가능) |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'waiting' | 채팅방 상태 (waiting, active, ended) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 생성 시간 |
| ended_at | TIMESTAMP | NULL | 종료 시간 |
| metadata | JSONB | NULL | 추가 메타데이터 (위젯 설정 등) |

**인덱스:**
- PRIMARY KEY: `id`
- INDEX: `agent_id`, `status`, `created_at`

---

### 2. `messages` (메시지)
채팅방 내 메시지를 저장하는 테이블

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | SERIAL | PRIMARY KEY | 메시지 고유 ID (자동 증가) |
| room_id | VARCHAR(50) | FOREIGN KEY → chat_rooms.id | 채팅방 ID |
| sender_type | VARCHAR(20) | NOT NULL | 발신자 유형 (customer, agent) |
| sender_id | VARCHAR(50) | NULL | 발신자 ID (상담사인 경우) |
| original_text | TEXT | NOT NULL | 원문 |
| original_language | VARCHAR(10) | NOT NULL | 원문 언어 |
| translated_text | TEXT | NULL | 번역문 |
| target_language | VARCHAR(10) | NULL | 번역 대상 언어 |
| timestamp | TIMESTAMP | NOT NULL, DEFAULT NOW() | 메시지 전송 시간 |
| metadata | JSONB | NULL | 번역 품질, 신뢰도 등 |

**인덱스:**
- PRIMARY KEY: `id`
- INDEX: `room_id`, `timestamp`

---

### 3. `agents` (상담사)
상담사 정보를 관리하는 테이블

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | VARCHAR(50) | PRIMARY KEY | 상담사 고유 ID |
| name | VARCHAR(100) | NOT NULL | 이름 |
| email | VARCHAR(255) | UNIQUE, NOT NULL | 이메일 (로그인 ID) |
| password_hash | VARCHAR(255) | NOT NULL | 비밀번호 해시 |
| role | VARCHAR(20) | NOT NULL, DEFAULT 'agent' | 권한 (agent, admin) |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'offline' | 상태 (online, away, offline) |
| max_concurrent_chats | INTEGER | DEFAULT 5 | 동시 상담 최대 수 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 계정 생성 시간 |
| last_login | TIMESTAMP | NULL | 마지막 로그인 시간 |

**인덱스:**
- PRIMARY KEY: `id`
- UNIQUE INDEX: `email`
- INDEX: `status`

---

### 4. `agent_sessions` (상담사 세션)
상담사 로그인 세션 관리

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | VARCHAR(50) | PRIMARY KEY | 세션 ID |
| agent_id | VARCHAR(50) | FOREIGN KEY → agents.id | 상담사 ID |
| token | VARCHAR(255) | UNIQUE, NOT NULL | JWT 토큰 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 세션 생성 시간 |
| expires_at | TIMESTAMP | NOT NULL | 만료 시간 |
| ip_address | VARCHAR(45) | NULL | IP 주소 |

**인덱스:**
- PRIMARY KEY: `id`
- UNIQUE INDEX: `token`
- INDEX: `agent_id`, `expires_at`

---

### 5. `customer_sessions` (고객 세션)
고객 접속 정보 (익명)

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | VARCHAR(50) | PRIMARY KEY | 세션 ID |
| ip_address | VARCHAR(45) | NULL | IP 주소 |
| user_agent | TEXT | NULL | 브라우저 정보 |
| language | VARCHAR(10) | NOT NULL | 선택한 언어 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 세션 생성 시간 |
| last_active | TIMESTAMP | NOT NULL | 마지막 활동 시간 |
| metadata | JSONB | NULL | 추가 정보 (국가, 브라우저 등) |

**인덱스:**
- PRIMARY KEY: `id`
- INDEX: `created_at`, `last_active`

---

### 6. `translation_cache` (번역 캐시)
번역 결과를 캐싱하여 성능 향상

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | VARCHAR(64) | PRIMARY KEY | 캐시 키 (source_text + source_lang + target_lang의 해시) |
| source_text | TEXT | NOT NULL | 원문 |
| source_lang | VARCHAR(10) | NOT NULL | 원문 언어 |
| target_lang | VARCHAR(10) | NOT NULL | 번역 대상 언어 |
| translated_text | TEXT | NOT NULL | 번역문 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 캐시 생성 시간 |
| hit_count | INTEGER | DEFAULT 0 | 캐시 히트 횟수 |

**인덱스:**
- PRIMARY KEY: `id`
- INDEX: `created_at` (TTL 정책 적용)

---

### 7. `medical_glossary` (의료 용어집)
의료 전문 용어 다국어 사전

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | SERIAL | PRIMARY KEY | 용어 ID |
| term_ko | VARCHAR(200) | NOT NULL | 한국어 용어 |
| term_en | VARCHAR(200) | NOT NULL | 영어 용어 |
| term_ja | VARCHAR(200) | NULL | 일본어 용어 |
| term_zh | VARCHAR(200) | NULL | 중국어 용어 |
| term_vi | VARCHAR(200) | NULL | 베트남어 용어 |
| term_th | VARCHAR(200) | NULL | 태국어 용어 |
| category | VARCHAR(50) | NOT NULL | 카테고리 (진료, 증상, 검사 등) |
| usage_count | INTEGER | DEFAULT 0 | 사용 횟수 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 등록 시간 |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 수정 시간 |

**인덱스:**
- PRIMARY KEY: `id`
- INDEX: `term_ko`, `term_en`, `category`
- FULLTEXT INDEX: `term_ko`, `term_en` (검색 최적화)

---

### 8. `quick_responses` (빠른 답변 템플릿)
상담사용 빠른 답변 템플릿

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | SERIAL | PRIMARY KEY | 템플릿 ID |
| category | VARCHAR(50) | NOT NULL | 카테고리 (인사, 예약, 검사 등) |
| title | VARCHAR(100) | NOT NULL | 템플릿 제목 |
| content_ko | TEXT | NOT NULL | 한국어 내용 |
| content_en | TEXT | NOT NULL | 영어 내용 |
| content_ja | TEXT | NULL | 일본어 내용 |
| content_zh | TEXT | NULL | 중국어 내용 |
| content_vi | TEXT | NULL | 베트남어 내용 |
| content_th | TEXT | NULL | 태국어 내용 |
| usage_count | INTEGER | DEFAULT 0 | 사용 횟수 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 등록 시간 |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 수정 시간 |

**인덱스:**
- PRIMARY KEY: `id`
- INDEX: `category`, `usage_count`

---

## 관계 (Relationships)

```
agents (1) ──────< (N) chat_rooms
agents (1) ──────< (N) agent_sessions
chat_rooms (1) ──< (N) messages
```

### 주요 관계:
1. **agents ↔ chat_rooms**: 1:N 관계
   - 한 명의 상담사는 여러 채팅방을 담당할 수 있음

2. **chat_rooms ↔ messages**: 1:N 관계
   - 한 채팅방에는 여러 메시지가 포함됨

3. **agents ↔ agent_sessions**: 1:N 관계
   - 한 상담사는 여러 세션을 가질 수 있음 (다중 기기 로그인)

---

## 데이터 보관 정책

| 테이블 | 보관 기간 | 정책 |
|--------|-----------|------|
| messages | 1년 | 1년 후 아카이빙 또는 삭제 |
| chat_rooms | 1년 | 1년 후 아카이빙 또는 삭제 |
| translation_cache | 30일 | Redis TTL 30일 적용 |
| customer_sessions | 30일 | 30일 후 자동 삭제 |
| agent_sessions | 7일 | 만료된 세션 자동 삭제 |
| agents | 영구 | 퇴사 시 soft delete (status = 'deleted') |
| medical_glossary | 영구 | 정기 업데이트 |
| quick_responses | 영구 | 정기 업데이트 |

---

## 백업 전략

### 정기 백업
- **빈도**: 매일 새벽 3시 (KST)
- **보관**: 최근 30일 백업 유지
- **방식**: PostgreSQL `pg_dump` 전체 백업

### 실시간 복제
- **Master-Slave Replication** 구성
- **Read Replica**: 읽기 부하 분산

### 재해 복구 (DR)
- **RPO (Recovery Point Objective)**: 1시간
- **RTO (Recovery Time Objective)**: 4시간
- **방식**: AWS RDS 자동 백업 + 스냅샷

---

## 마이그레이션 히스토리

| 버전 | 날짜 | 설명 |
|------|------|------|
| 001 | 2025-01-XX | 초기 스키마: chat_rooms, messages 테이블 생성 |
| 002 | 예정 | agents, agent_sessions 테이블 추가 |
| 003 | 예정 | customer_sessions, translation_cache 테이블 추가 |
| 004 | 예정 | medical_glossary, quick_responses 테이블 추가 |
