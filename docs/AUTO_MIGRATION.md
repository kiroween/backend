# 자동 마이그레이션 가이드

## 개요
TimeGrave API는 애플리케이션 시작 시 자동으로 데이터베이스 마이그레이션을 실행합니다.

## 작동 방식

### 1. 데이터베이스 타입 자동 감지
- `DATABASE_URL` 환경 변수를 확인
- SQLite 또는 PostgreSQL 자동 감지
- 적절한 마이그레이션 파일 실행

### 2. 마이그레이션 실행
```
🚀 TimeGrave API starting up...
✅ Database initialized
🔧 Running database migrations...
🔧 Detected SQLite database
  Running: add_enroll_share_fields.sql
  ✓ add_enroll_share_fields.sql completed
  Running: add_invite_token.sql
  ✓ add_invite_token.sql completed
✅ SQLite migrations completed
Migration status:
  - enroll: ✓
  - share: ✓
  - invite_token: ✓
✅ Scheduler started
```

### 3. 안전성 보장
- ✅ 멱등성: 여러 번 실행해도 안전
- ✅ 에러 처리: 실패해도 앱은 계속 실행
- ✅ 상태 확인: 마이그레이션 적용 여부 자동 확인

---

## 사용 방법

### 로컬 개발 (SQLite)

```bash
# 1. 환경 변수 설정 (선택사항, 기본값 사용 가능)
export DATABASE_URL='sqlite:///./data/timegrave.db'

# 2. 애플리케이션 시작
uvicorn app.main:app --reload

# 또는 도커
docker-compose up -d
```

### 운영 환경 (PostgreSQL)

```bash
# 1. 환경 변수 설정
export DATABASE_URL='postgresql://username:password@host:5432/database_name'

# 2. 애플리케이션 시작
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 또는 도커
docker run -e DATABASE_URL='postgresql://...' -p 8000:8000 timegrave-api
```

---

## 환경 변수 설정

### .env 파일 사용
```bash
# .env
DATABASE_URL=postgresql://username:password@host:5432/database_name
```

### Docker Compose
```yaml
# docker-compose.yml
services:
  api:
    environment:
      - DATABASE_URL=postgresql://username:password@host:5432/database_name
```

### Kubernetes
```yaml
# deployment.yaml
env:
  - name: DATABASE_URL
    valueFrom:
      secretKeyRef:
        name: db-secret
        key: database-url
```

---

## 마이그레이션 파일

### SQLite
- `migrations/add_enroll_share_fields.sql`
- `migrations/add_invite_token.sql`

### PostgreSQL
- `migrations/add_enroll_share_fields_postgresql.sql`
- `migrations/add_invite_token_postgresql.sql`

---

## 로그 확인

### 성공 케이스
```
INFO:app.utils.migration:🔧 Detected PostgreSQL database
INFO:app.utils.migration:  Running: add_enroll_share_fields_postgresql.sql
INFO:app.utils.migration:  ✓ add_enroll_share_fields_postgresql.sql completed
INFO:app.utils.migration:✅ PostgreSQL migrations completed
INFO:app.utils.migration:Migration status:
INFO:app.utils.migration:  - enroll: ✓
INFO:app.utils.migration:  - share: ✓
INFO:app.utils.migration:  - invite_token: ✓
```

### 이미 적용된 경우
```
INFO:app.utils.migration:  Running: add_enroll_share_fields_postgresql.sql
INFO:app.utils.migration:  ✓ add_enroll_share_fields_postgresql.sql completed (already applied)
```

### 에러 케이스
```
ERROR:app.utils.migration:❌ Migration failed: connection refused
WARNING:app.utils.migration:⚠️ Continuing without migrations...
```

---

## 트러블슈팅

### 1. 마이그레이션이 실행되지 않음
**원인:** migrations 폴더가 없음

**해결:**
```bash
# 도커 이미지 재빌드
docker-compose up -d --build
```

### 2. PostgreSQL 연결 실패
**원인:** DATABASE_URL이 잘못됨

**해결:**
```bash
# 올바른 형식 확인
export DATABASE_URL='postgresql://user:password@host:5432/dbname'

# 연결 테스트
psql "$DATABASE_URL" -c "SELECT 1"
```

### 3. 권한 오류
**원인:** 데이터베이스 사용자 권한 부족

**해결:**
```sql
GRANT ALL PRIVILEGES ON TABLE tombstones TO your_user;
GRANT ALL PRIVILEGES ON DATABASE your_db TO your_user;
```

### 4. 마이그레이션 파일을 찾을 수 없음
**원인:** Dockerfile에 migrations 폴더가 복사되지 않음

**해결:**
```dockerfile
# Dockerfile
COPY ./migrations ./migrations
```

---

## 수동 마이그레이션 (필요 시)

자동 마이그레이션이 실패하거나 수동으로 실행하고 싶은 경우:

### SQLite
```bash
sqlite3 data/timegrave.db < migrations/add_enroll_share_fields.sql
sqlite3 data/timegrave.db < migrations/add_invite_token.sql
```

### PostgreSQL
```bash
psql "$DATABASE_URL" -f migrations/add_enroll_share_fields_postgresql.sql
psql "$DATABASE_URL" -f migrations/add_invite_token_postgresql.sql
```

---

## 새로운 마이그레이션 추가하기

### 1. 마이그레이션 파일 생성
```bash
# SQLite
touch migrations/new_migration.sql

# PostgreSQL
touch migrations/new_migration_postgresql.sql
```

### 2. app/utils/migration.py 수정
```python
def run_sqlite_migrations():
    migrations = [
        "add_enroll_share_fields.sql",
        "add_invite_token.sql",
        "new_migration.sql",  # 추가
    ]
    # ...

def run_postgresql_migrations():
    migrations = [
        "add_enroll_share_fields_postgresql.sql",
        "add_invite_token_postgresql.sql",
        "new_migration_postgresql.sql",  # 추가
    ]
    # ...
```

### 3. 테스트
```bash
# 로컬에서 테스트
uvicorn app.main:app --reload

# 로그 확인
# ✓ new_migration.sql completed
```

---

## 베스트 프랙티스

### 1. 항상 백업
```bash
# PostgreSQL
pg_dump "$DATABASE_URL" > backup_$(date +%Y%m%d_%H%M%S).sql

# SQLite
cp data/timegrave.db data/timegrave.db.backup
```

### 2. 스테이징 환경에서 먼저 테스트
```bash
# 스테이징
export DATABASE_URL='postgresql://staging...'
uvicorn app.main:app

# 로그 확인 후 프로덕션 배포
```

### 3. 롤백 계획 준비
```sql
-- 롤백 스크립트 작성
ALTER TABLE tombstones DROP COLUMN IF EXISTS new_column;
```

### 4. 모니터링
```bash
# 로그 모니터링
docker logs -f timegrave-api | grep migration

# 헬스 체크
curl http://localhost:8000/
```

---

## FAQ

### Q: 마이그레이션이 실패하면 앱이 시작되지 않나요?
A: 아니요. 마이그레이션이 실패해도 앱은 계속 실행됩니다. 로그에 에러만 출력됩니다.

### Q: 여러 번 실행해도 안전한가요?
A: 네. 모든 마이그레이션은 멱등성을 보장합니다. PostgreSQL은 `IF NOT EXISTS`를 사용하고, SQLite는 중복 컬럼 에러를 무시합니다.

### Q: 다른 데이터베이스(MySQL 등)도 지원하나요?
A: 현재는 SQLite와 PostgreSQL만 지원합니다. 다른 데이터베이스를 추가하려면 `app/utils/migration.py`를 수정하세요.

### Q: 마이그레이션 순서가 중요한가요?
A: 네. `migrations` 배열의 순서대로 실행되므로 의존성이 있는 경우 순서를 지켜야 합니다.

---

## 참고 문서

- [마이그레이션 README](../migrations/README.md)
- [친구 초대 기능 문서](./FRIEND_WRITE_FEATURE.md)
- [테스트 가이드](../TEST_INVITE_FEATURE.md)
