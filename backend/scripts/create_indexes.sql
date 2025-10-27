-- MedTranslate Database Indexes
-- 프로젝트 초기 인덱스 생성 스크립트

-- ============================================
-- chat_rooms 인덱스
-- ============================================

-- 상담사별 채팅방 조회 (상담사 대시보드)
CREATE INDEX IF NOT EXISTS idx_chat_rooms_agent_id ON chat_rooms(agent_id);

-- 상태별 채팅방 조회 (대기 중인 방 찾기)
CREATE INDEX IF NOT EXISTS idx_chat_rooms_status ON chat_rooms(status);

-- 생성 시간 기준 정렬 (최근 채팅 목록)
CREATE INDEX IF NOT EXISTS idx_chat_rooms_created_at ON chat_rooms(created_at DESC);

-- 복합 인덱스: 상담사 + 상태 (상담사의 활성 채팅방)
CREATE INDEX IF NOT EXISTS idx_chat_rooms_agent_status ON chat_rooms(agent_id, status);

-- ============================================
-- messages 인덱스
-- ============================================

-- 채팅방별 메시지 조회 (가장 빈번한 쿼리)
CREATE INDEX IF NOT EXISTS idx_messages_room_id ON messages(room_id);

-- 시간순 정렬 (메시지 히스토리)
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(created_at DESC);

-- 복합 인덱스: 채팅방 + 시간 (채팅 히스토리 조회 최적화)
CREATE INDEX IF NOT EXISTS idx_messages_room_timestamp ON messages(room_id, created_at DESC);

-- ============================================
-- agents 인덱스
-- ============================================

-- 상태별 상담사 조회 (온라인 상담사 찾기)
CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);

-- 마지막 로그인 시간 (통계)
CREATE INDEX IF NOT EXISTS idx_agents_last_login ON agents(last_login DESC);

-- ============================================
-- agent_sessions 인덱스
-- ============================================

-- 상담사별 세션 조회
CREATE INDEX IF NOT EXISTS idx_agent_sessions_agent_id ON agent_sessions(agent_id);

-- 만료된 세션 정리 (배치 작업)
CREATE INDEX IF NOT EXISTS idx_agent_sessions_expires_at ON agent_sessions(expires_at);

-- ============================================
-- customer_sessions 인덱스
-- ============================================

-- 생성 시간 (정리 작업)
CREATE INDEX IF NOT EXISTS idx_customer_sessions_created_at ON customer_sessions(created_at);

-- 마지막 활동 시간 (비활성 세션 정리)
CREATE INDEX IF NOT EXISTS idx_customer_sessions_last_active ON customer_sessions(last_active);

-- ============================================
-- 완료 메시지
-- ============================================
SELECT 'All indexes created successfully!' AS status;
