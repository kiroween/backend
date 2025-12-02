# 데이터베이스 마이그레이션

## 개요
친구 초대 기능을 위한 데이터베이스 마이그레이션입니다.

## 추가된 필드

### 1. enroll (INTEGER)
- 작성자 userId (본인 또는 친구)
- 기본값: user_id

### 2. share (TEXT)
- 쓰기 권한 있는 친구들 (JSON array of userIds)
- 예시: `"[2, 3, 4]"`

### 3. invite_token (VARCHAR(100))
- 초대 링크용 UUID 토큰
- 쓰기 권한 부여용

---

## SQLite 마이그레이션 (개발 환경)

### 방법 1: 직접 실행
```bash
# enroll, share 필드 추가
sqlite3 data/timegrave.db < migrations/add_enroll_share_fields.sql

# invite_token 필드 추가
sqlite3 data/timegrave.db < migrations/add_invite_token.sql
```

### 방법 2: 확인
```bash
# 테이블 구조 확인
sqlite3 data/timegrave.db "PRAGMA table_info(tombstones);"
```

---

## PostgreSQL 마이그레이션 (운영 환경)

### 사전 준비

1. **DATABASE_URL 환경 변수 설정**
```bash
export DATABASE_URL='postgresql://username:password@host:5432/database_name'

# 또는 .env 파일에 추가
echo "DATABASE_URL=postgresql://username:password@host:5432/database_name" >> .env
```

2. **psycopg2 설치 (Python 스크립트 사용 시)**
```bash
pip install psycopg2-binary
```

### 방법 1: Bash 스크립트 (추천)
```bash
./migrations/run_postgresql_migrations.sh
```

### 방법 2: Python 스크립트
```bash
python migrations/run_postgresql_migrations.py
```

### 방법 3: 수동 실행
```bash
# enroll, share 필드 추가
psql "$DATABASE_URL" -f migrations/add_enroll_share_fields_postgresql.sql

# invite_token 필드 추가
psql "$DATABASE_URL" -f migrations/add_invite_token_postgresql.sql
```

### 방법 4: psql 대화형 모드
```bash
psql "$DATABASE_URL"

# 마이그레이션 파일 실행
\i migrations/add_enroll_share_fields_postgresql.sql
\i migrations/add_invite_token_postgresql.sql

# 테이블 구조 확인
\d tombstones

# 종료
\q
```

---

## 마이그레이션 확인

### SQLite
```bash
sqlite3 data/timegrave.db "PRAGMA table_info(tombstones);"
```

**예상 결과:**
```
10|enroll|INTEGER|0||0
11|share|TEXT|0||0
12|invite_token|VARCHAR(100)|0||0
```

### PostgreSQL
```bash
psql "$DATABASE_URL" -c "\d tombstones"
```

**예상 결과:**
```
Column       | Type          | Nullable | Default
-------------+---------------+----------+---------
enroll       | integer       | YES      | NULL
share        | text          | YES      | NULL
invite_token | varchar(100)  | YES      | NULL
```

---

## 롤백 (필요 시)

### SQLite
```sql
-- enroll, share 제거
ALTER TABLE tombstones DROP COLUMN enroll;
ALTER TABLE tombstones DROP COLUMN share;

-- invite_token 제거
ALTER TABLE tombstones DROP COLUMN invite_token;
```

### PostgreSQL
```sql
-- enroll, share 제거
ALTER TABLE tombstones DROP COLUMN IF EXISTS enroll;
ALTER TABLE tombstones DROP COLUMN IF EXISTS share;
DROP INDEX IF EXISTS idx_tombstones_enroll;

-- invite_token 제거
ALTER TABLE tombstones DROP COLUMN IF EXISTS invite_token;
DROP INDEX IF EXISTS idx_tombstones_invite_token;
```

---

## 트러블슈팅

### 1. DATABASE_URL 환경 변수가 없음
```bash
export DATABASE_URL='postgresql://user:password@host:5432/dbname'
```

### 2. psql 명령어를 찾을 수 없음
PostgreSQL 클라이언트를 설치하세요:
```bash
# macOS
brew install postgresql

# Ubuntu/Debian
sudo apt-get install postgresql-client

# CentOS/RHEL
sudo yum install postgresql
```

### 3. 권한 오류
데이터베이스 사용자에게 ALTER TABLE 권한이 있는지 확인하세요:
```sql
GRANT ALL PRIVILEGES ON TABLE tombstones TO your_user;
```

### 4. 이미 컬럼이 존재함
PostgreSQL 마이그레이션은 `IF NOT EXISTS`를 사용하므로 안전합니다.
SQLite는 수동으로 확인 필요:
```bash
sqlite3 data/timegrave.db "PRAGMA table_info(tombstones);"
```

---

## 마이그레이션 파일 목록

### SQLite
- `add_enroll_share_fields.sql` - enroll, share 필드 추가
- `add_invite_token.sql` - invite_token 필드 추가

### PostgreSQL
- `add_enroll_share_fields_postgresql.sql` - enroll, share 필드 추가
- `add_invite_token_postgresql.sql` - invite_token 필드 추가

### 실행 스크립트
- `run_postgresql_migrations.sh` - Bash 스크립트
- `run_postgresql_migrations.py` - Python 스크립트

---

## 자동 마이그레이션 (추천 ⭐)

애플리케이션 시작 시 자동으로 마이그레이션이 실행됩니다!

### 설정 방법

1. **환경 변수 설정**
```bash
# SQLite (개발 환경)
export DATABASE_URL='sqlite:///./data/timegrave.db'

# PostgreSQL (운영 환경)
export DATABASE_URL='postgresql://username:password@host:5432/database_name'
```

2. **애플리케이션 시작**
```bash
uvicorn app.main:app --reload
```

3. **로그 확인**
```
🚀 TimeGrave API starting up...
✅ Database initialized
🔧 Running database migrations...
🔧 Detected PostgreSQL database
  Running: add_enroll_share_fields_postgresql.sql
  ✓ add_enroll_share_fields_postgresql.sql completed
  Running: add_invite_token_postgresql.sql
  ✓ add_invite_token_postgresql.sql completed
✅ PostgreSQL migrations completed
Migration status:
  - enroll: ✓
  - share: ✓
  - invite_token: ✓
✅ Scheduler started
```

### 특징
- ✅ 데이터베이스 타입 자동 감지 (SQLite/PostgreSQL)
- ✅ 멱등성 보장 (여러 번 실행해도 안전)
- ✅ 에러 발생 시에도 앱 시작 (로그만 출력)
- ✅ 마이그레이션 상태 자동 확인

---

## 운영 환경 배포 체크리스트

- [ ] DATABASE_URL 환경 변수 설정 확인
- [ ] 데이터베이스 백업 완료
- [ ] 스테이징 환경에서 테스트
- [ ] 애플리케이션 시작 (자동 마이그레이션 실행)
- [ ] 로그에서 마이그레이션 성공 확인
- [ ] 테이블 구조 확인
- [ ] API 테스트 (초대 링크 생성/수락)
- [ ] 롤백 계획 준비

---

## 참고

- 마이그레이션은 멱등성(idempotent)을 보장합니다
- PostgreSQL은 `IF NOT EXISTS` 사용
- 기존 데이터는 영향받지 않습니다
- `enroll`은 기존 레코드에 대해 `user_id`로 자동 설정됩니다
