# 데이터베이스 인덱스 전략 및 백업 정책

## 1. 인덱스 전략

### 기본 원칙
- 자주 조회되는 컬럼에 인덱스 생성
- WHERE, JOIN, ORDER BY 절에 사용되는 컬럼 우선
- 카디널리티(고유값 비율)가 높은 컬럼 우선
- Write 성능과 Read 성능 간 균형 유지

### 테이블별 인덱스

#### chat_rooms
```sql
-- Primary Key (자동 생성)
CREATE INDEX idx_chat_rooms_pk ON chat_rooms(id);

-- 상담사별 채팅방 조회 (상담사 대시보드)
CREATE INDEX idx_chat_rooms_agent_id ON chat_rooms(agent_id);

-- 상태별 채팅방 조회 (대기 중인 방 찾기)
CREATE INDEX idx_chat_rooms_status ON chat_rooms(status);

-- 생성 시간 기준 정렬 (최근 채팅 목록)
CREATE INDEX idx_chat_rooms_created_at ON chat_rooms(created_at DESC);

-- 복합 인덱스: 상담사 + 상태 (상담사의 활성 채팅방)
CREATE INDEX idx_chat_rooms_agent_status ON chat_rooms(agent_id, status);
```

#### messages
```sql
-- Primary Key (자동 생성)
CREATE INDEX idx_messages_pk ON messages(id);

-- 채팅방별 메시지 조회 (가장 빈번한 쿼리)
CREATE INDEX idx_messages_room_id ON messages(room_id);

-- 시간순 정렬 (메시지 히스토리)
CREATE INDEX idx_messages_timestamp ON messages(created_at DESC);

-- 복합 인덱스: 채팅방 + 시간 (채팅 히스토리 조회 최적화)
CREATE INDEX idx_messages_room_timestamp ON messages(room_id, created_at DESC);
```

#### agents
```sql
-- Primary Key (자동 생성)
CREATE INDEX idx_agents_pk ON agents(id);

-- 이메일로 조회 (로그인, UNIQUE 제약조건으로 자동 인덱스)
CREATE UNIQUE INDEX idx_agents_email ON agents(email);

-- 상태별 상담사 조회 (온라인 상담사 찾기)
CREATE INDEX idx_agents_status ON agents(status);

-- 마지막 로그인 시간 (통계)
CREATE INDEX idx_agents_last_login ON agents(last_login DESC);
```

#### agent_sessions
```sql
-- Primary Key (자동 생성)
CREATE INDEX idx_agent_sessions_pk ON agent_sessions(id);

-- 토큰으로 세션 조회 (인증, UNIQUE 제약조건으로 자동 인덱스)
CREATE UNIQUE INDEX idx_agent_sessions_token ON agent_sessions(token);

-- 상담사별 세션 조회
CREATE INDEX idx_agent_sessions_agent_id ON agent_sessions(agent_id);

-- 만료된 세션 정리 (배치 작업)
CREATE INDEX idx_agent_sessions_expires_at ON agent_sessions(expires_at);
```

#### customer_sessions
```sql
-- Primary Key (자동 생성)
CREATE INDEX idx_customer_sessions_pk ON customer_sessions(id);

-- 생성 시간 (정리 작업)
CREATE INDEX idx_customer_sessions_created_at ON customer_sessions(created_at);

-- 마지막 활동 시간 (비활성 세션 정리)
CREATE INDEX idx_customer_sessions_last_active ON customer_sessions(last_active);
```

### 인덱스 생성 SQL 스크립트

```sql
-- backend/scripts/create_indexes.sql

-- chat_rooms 인덱스
CREATE INDEX IF NOT EXISTS idx_chat_rooms_agent_id ON chat_rooms(agent_id);
CREATE INDEX IF NOT EXISTS idx_chat_rooms_status ON chat_rooms(status);
CREATE INDEX IF NOT EXISTS idx_chat_rooms_created_at ON chat_rooms(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_chat_rooms_agent_status ON chat_rooms(agent_id, status);

-- messages 인덱스
CREATE INDEX IF NOT EXISTS idx_messages_room_id ON messages(room_id);
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_room_timestamp ON messages(room_id, created_at DESC);

-- agents 인덱스
CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);
CREATE INDEX IF NOT EXISTS idx_agents_last_login ON agents(last_login DESC);

-- agent_sessions 인덱스
CREATE INDEX IF NOT EXISTS idx_agent_sessions_agent_id ON agent_sessions(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_sessions_expires_at ON agent_sessions(expires_at);

-- customer_sessions 인덱스
CREATE INDEX IF NOT EXISTS idx_customer_sessions_created_at ON customer_sessions(created_at);
CREATE INDEX IF NOT EXISTS idx_customer_sessions_last_active ON customer_sessions(last_active);
```

### 인덱스 유지보수

#### 정기 분석 및 최적화
```sql
-- 매주 실행 (일요일 새벽 4시)
ANALYZE chat_rooms;
ANALYZE messages;
ANALYZE agents;
ANALYZE agent_sessions;
ANALYZE customer_sessions;

-- 인덱스 재구축 (필요시)
REINDEX TABLE chat_rooms;
REINDEX TABLE messages;
```

#### 인덱스 사용률 모니터링
```sql
-- 사용되지 않는 인덱스 찾기
SELECT
  schemaname,
  tablename,
  indexname,
  idx_scan,
  idx_tup_read,
  idx_tup_fetch
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND indexname NOT LIKE '%_pkey'
ORDER BY schemaname, tablename;
```

---

## 2. 백업 정책

### 백업 전략 개요

| 백업 타입 | 빈도 | 보관 기간 | RPO | RTO |
|-----------|------|-----------|-----|-----|
| 전체 백업 | 매일 | 30일 | 24시간 | 4시간 |
| 증분 백업 | 매시간 | 7일 | 1시간 | 2시간 |
| WAL 아카이빙 | 실시간 | 7일 | 5분 | 1시간 |
| 스냅샷 | 매주 | 12주 | - | - |

**용어 설명:**
- **RPO (Recovery Point Objective)**: 데이터 손실 허용 시간
- **RTO (Recovery Time Objective)**: 시스템 복구 목표 시간

### 백업 방법

#### 1. 전체 백업 (Daily Full Backup)

**실행 시간**: 매일 새벽 3시 (KST)

```bash
#!/bin/bash
# backend/scripts/backup_full.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/postgresql/full"
DB_NAME="medtranslate"
DB_USER="user"
BACKUP_FILE="$BACKUP_DIR/medtranslate_full_$DATE.sql.gz"

# 백업 디렉토리 생성
mkdir -p $BACKUP_DIR

# PostgreSQL 전체 백업 (압축)
pg_dump -h localhost -p 54321 -U $DB_USER -d $DB_NAME \
  --format=plain \
  --no-owner \
  --no-acl \
  --verbose \
  | gzip > $BACKUP_FILE

# 백업 성공 여부 확인
if [ $? -eq 0 ]; then
  echo "$(date): Backup successful - $BACKUP_FILE" >> /var/log/db_backup.log
else
  echo "$(date): Backup failed!" >> /var/log/db_backup.log
  exit 1
fi

# 30일 이전 백업 삭제
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

# S3 업로드 (선택사항)
# aws s3 cp $BACKUP_FILE s3://medtranslate-backup/postgresql/full/
```

**Crontab 등록:**
```bash
0 3 * * * /home/k8s-admin/medtranslate-v1/backend/scripts/backup_full.sh
```

#### 2. 증분 백업 (Incremental Backup)

**실행 시간**: 매시간

```bash
#!/bin/bash
# backend/scripts/backup_incremental.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/postgresql/incremental"
BACKUP_FILE="$BACKUP_DIR/medtranslate_inc_$DATE.tar.gz"

mkdir -p $BACKUP_DIR

# WAL 아카이브 기반 증분 백업
pg_basebackup -h localhost -p 54321 -U user -D $BACKUP_DIR/basebackup_$DATE \
  --format=tar \
  --gzip \
  --progress \
  --verbose

# 7일 이전 백업 삭제
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

**Crontab 등록:**
```bash
0 * * * * /home/k8s-admin/medtranslate-v1/backend/scripts/backup_incremental.sh
```

#### 3. WAL 아카이빙 (Write-Ahead Logging)

**postgresql.conf 설정:**
```conf
# WAL 설정
wal_level = replica
archive_mode = on
archive_command = 'cp %p /backup/postgresql/wal/%f'
archive_timeout = 300  # 5분마다 강제 아카이브
```

**WAL 정리 스크립트:**
```bash
#!/bin/bash
# backend/scripts/cleanup_wal.sh

WAL_DIR="/backup/postgresql/wal"

# 7일 이전 WAL 파일 삭제
find $WAL_DIR -name "*.wal" -mtime +7 -delete
```

#### 4. 스냅샷 백업 (Weekly Snapshot)

**실행 시간**: 매주 일요일 새벽 2시

```bash
#!/bin/bash
# backend/scripts/backup_snapshot.sh

DATE=$(date +%Y%m%d)
SNAPSHOT_NAME="medtranslate_snapshot_$DATE"

# AWS RDS 스냅샷 생성 (프로덕션 환경)
# aws rds create-db-snapshot \
#   --db-instance-identifier medtranslate-prod \
#   --db-snapshot-identifier $SNAPSHOT_NAME

# 로컬 Docker 볼륨 스냅샷 (개발 환경)
docker exec medtranslate-db pg_dumpall > /backup/snapshots/snapshot_$DATE.sql

# 12주 이전 스냅샷 삭제
find /backup/snapshots -name "snapshot_*.sql" -mtime +84 -delete
```

**Crontab 등록:**
```bash
0 2 * * 0 /home/k8s-admin/medtranslate-v1/backend/scripts/backup_snapshot.sh
```

### 복구 절차

#### 전체 백업 복구
```bash
# 1. 데이터베이스 삭제 및 재생성
dropdb -h localhost -p 54321 -U user medtranslate
createdb -h localhost -p 54321 -U user medtranslate

# 2. 백업 복원
gunzip -c /backup/postgresql/full/medtranslate_full_20250127_030000.sql.gz \
  | psql -h localhost -p 54321 -U user -d medtranslate

# 3. 연결 확인
psql -h localhost -p 54321 -U user -d medtranslate -c "SELECT COUNT(*) FROM chat_rooms;"
```

#### Point-in-Time Recovery (PITR)
```bash
# 1. 기본 백업 복원
pg_basebackup 복원

# 2. WAL 파일 적용
# recovery.conf 설정 (PostgreSQL 12 이전)
restore_command = 'cp /backup/postgresql/wal/%f %p'
recovery_target_time = '2025-01-27 14:30:00'

# PostgreSQL 12 이상: postgresql.auto.conf
echo "restore_command = 'cp /backup/postgresql/wal/%f %p'" >> postgresql.auto.conf
echo "recovery_target_time = '2025-01-27 14:30:00'" >> postgresql.auto.conf
```

### 백업 검증

**매월 1회 복구 테스트 (첫째 주 토요일)**
```bash
#!/bin/bash
# backend/scripts/test_restore.sh

# 최신 백업 파일 찾기
LATEST_BACKUP=$(ls -t /backup/postgresql/full/*.sql.gz | head -1)

# 테스트 데이터베이스에 복원
createdb -h localhost -p 54321 -U user medtranslate_test
gunzip -c $LATEST_BACKUP | psql -h localhost -p 54321 -U user -d medtranslate_test

# 데이터 무결성 검증
TEST_COUNT=$(psql -h localhost -p 54321 -U user -d medtranslate_test -t -c "SELECT COUNT(*) FROM chat_rooms;")

if [ $TEST_COUNT -gt 0 ]; then
  echo "$(date): Restore test successful - $TEST_COUNT rooms found" >> /var/log/restore_test.log
else
  echo "$(date): Restore test failed!" >> /var/log/restore_test.log
fi

# 테스트 데이터베이스 삭제
dropdb -h localhost -p 54321 -U user medtranslate_test
```

### 백업 모니터링

**백업 실패 알림 (Slack/Email)**
```python
# backend/scripts/backup_monitor.py

import os
import datetime
import requests

def check_backup_status():
    backup_log = "/var/log/db_backup.log"

    # 최근 24시간 백업 확인
    with open(backup_log, 'r') as f:
        lines = f.readlines()
        recent_backups = [l for l in lines if 'Backup successful' in l]

        if not recent_backups:
            send_slack_alert("⚠️ 백업 실패: 최근 24시간 백업 없음")
        elif 'failed' in lines[-1]:
            send_slack_alert("❌ 백업 실패: 에러 발생")
        else:
            print("✅ 백업 정상")

def send_slack_alert(message):
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    requests.post(webhook_url, json={"text": message})

if __name__ == "__main__":
    check_backup_status()
```

### 재해 복구 계획 (Disaster Recovery Plan)

#### 시나리오 1: 데이터베이스 서버 장애
1. **즉시 조치** (0-15분):
   - Read Replica로 트래픽 전환
   - 장애 원인 파악
2. **복구 작업** (15-60분):
   - 최신 전체 백업 복원
   - WAL 로그 적용
3. **검증** (60-90분):
   - 데이터 무결성 확인
   - 애플리케이션 연결 테스트
4. **서비스 재개** (90-120분):
   - DNS 업데이트
   - 모니터링 강화

#### 시나리오 2: 데이터 손상/삭제
1. **즉시 조치** (0-10분):
   - 서비스 일시 중단
   - 추가 손상 방지
2. **복구 작업** (10-60분):
   - Point-in-Time Recovery 실행
   - 손상 이전 시점으로 복원
3. **검증 및 재개** (60-120분):
   - 데이터 확인 후 서비스 재개

### 백업 체크리스트

**일일 점검:**
- [ ] 전체 백업 성공 여부 확인
- [ ] 백업 파일 크기 확인 (급격한 증감 체크)
- [ ] 디스크 공간 확인 (80% 이상 시 알림)

**주간 점검:**
- [ ] 스냅샷 백업 성공 여부 확인
- [ ] 백업 파일 S3 업로드 확인
- [ ] 오래된 백업 파일 정리 확인

**월간 점검:**
- [ ] 복구 테스트 실행
- [ ] 백업 정책 검토
- [ ] 디스크 사용량 트렌드 분석

---

## 3. 보안 및 암호화

### 백업 파일 암호화
```bash
# GPG를 사용한 백업 파일 암호화
pg_dump -h localhost -p 54321 -U user -d medtranslate \
  | gzip \
  | gpg --symmetric --cipher-algo AES256 \
  > medtranslate_encrypted_$(date +%Y%m%d).sql.gz.gpg

# 복호화
gpg --decrypt medtranslate_encrypted_20250127.sql.gz.gpg \
  | gunzip \
  | psql -h localhost -p 54321 -U user -d medtranslate
```

### 접근 제어
- 백업 파일 권한: `600` (소유자만 읽기/쓰기)
- 백업 디렉토리 권한: `700`
- S3 버킷: 암호화 활성화, 버전 관리 활성화

### 민감 정보 보호
- 백업에 비밀번호 해시 포함 시 별도 암호화
- 프로덕션 백업의 개발 환경 사용 금지
- 백업 파일 전송 시 HTTPS/SFTP 사용

---

## 4. 참고 문서
- [PostgreSQL Backup Documentation](https://www.postgresql.org/docs/current/backup.html)
- [WAL Archiving Guide](https://www.postgresql.org/docs/current/continuous-archiving.html)
- [AWS RDS Backup Best Practices](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_CommonTasks.BackupRestore.html)
