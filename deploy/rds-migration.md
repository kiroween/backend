# SQLite에서 PostgreSQL (RDS)로 마이그레이션

## 1. RDS PostgreSQL 인스턴스 생성

### AWS Console에서 설정:
1. RDS > 데이터베이스 생성
2. 엔진 옵션: PostgreSQL
3. 템플릿: 프리 티어 (또는 프로덕션)
4. DB 인스턴스 식별자: `timegrave-db`
5. 마스터 사용자 이름: `timegrave_admin`
6. 마스터 암호: 강력한 암호 설정
7. DB 인스턴스 클래스: db.t3.micro (프리 티어)
8. 스토리지: 20GB (필요에 따라 조정)
9. 퍼블릭 액세스: 예 (초기 설정용, 나중에 제한 가능)
10. VPC 보안 그룹: 새로 생성 또는 기존 선택

### 보안 그룹 설정:
- 인바운드 규칙 추가:
  - 유형: PostgreSQL
  - 프로토콜: TCP
  - 포트: 5432
  - 소스: EC2 인스턴스의 보안 그룹 또는 IP

## 2. PostgreSQL 드라이버 설치

`pyproject.toml`에 PostgreSQL 드라이버 추가:

```toml
dependencies = [
    # ... 기존 의존성
    "psycopg2-binary>=2.9.9",  # PostgreSQL 드라이버
]
```

EC2에서 재빌드 필요:
```bash
docker build -f Dockerfile.prod -t timegrave-api:latest .
```

## 3. 환경변수 설정

`deploy/.env` 파일 수정:

```bash
# PostgreSQL RDS 연결
DATABASE_URL=postgresql://timegrave_admin:YOUR_PASSWORD@timegrave-db.xxxxx.region.rds.amazonaws.com:5432/timegrave
```

## 4. 데이터 마이그레이션 (선택사항)

기존 SQLite 데이터를 PostgreSQL로 이전하려면:

### 방법 1: 수동 마이그레이션 스크립트

```python
# migrate_data.py
import sqlite3
import psycopg2
from urllib.parse import urlparse

# SQLite 연결
sqlite_conn = sqlite3.connect('./data/timegrave.db')
sqlite_cursor = sqlite_conn.cursor()

# PostgreSQL 연결
pg_url = "postgresql://user:pass@host:5432/dbname"
parsed = urlparse(pg_url)
pg_conn = psycopg2.connect(
    database=parsed.path[1:],
    user=parsed.username,
    password=parsed.password,
    host=parsed.hostname,
    port=parsed.port
)
pg_cursor = pg_conn.cursor()

# 테이블별 데이터 복사
# users 테이블
sqlite_cursor.execute("SELECT * FROM users")
for row in sqlite_cursor.fetchall():
    pg_cursor.execute(
        "INSERT INTO users VALUES (%s, %s, %s, %s, %s)",
        row
    )

# tombstones 테이블
sqlite_cursor.execute("SELECT * FROM tombstones")
for row in sqlite_cursor.fetchall():
    pg_cursor.execute(
        "INSERT INTO tombstones VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        row
    )

pg_conn.commit()
print("✅ 마이그레이션 완료")
```

### 방법 2: 새로 시작 (권장)

SQLAlchemy가 자동으로 테이블을 생성하므로, 새로운 데이터베이스로 시작하는 것이 가장 간단합니다.

## 5. 연결 테스트

```bash
# EC2에서 PostgreSQL 연결 테스트
docker exec -it timegrave-api python -c "
from app.models.database import engine
try:
    with engine.connect() as conn:
        print('✅ PostgreSQL 연결 성공')
except Exception as e:
    print(f'❌ 연결 실패: {e}')
"
```

## 6. 데이터베이스 백업 설정

RDS 자동 백업 활성화:
- 백업 보존 기간: 7일 (권장)
- 백업 시간대: 트래픽이 적은 시간대 선택

## 주의사항

1. **연결 문자열 형식**: SQLite와 PostgreSQL의 URL 형식이 다릅니다
   - SQLite: `sqlite:///./data/timegrave.db`
   - PostgreSQL: `postgresql://user:pass@host:5432/dbname`

2. **데이터 타입 차이**: SQLAlchemy가 대부분 처리하지만, 일부 쿼리는 수정이 필요할 수 있습니다

3. **보안**: 프로덕션에서는 RDS 퍼블릭 액세스를 비활성화하고 VPC 내부에서만 접근하도록 설정

4. **성능**: PostgreSQL은 연결 풀링이 중요합니다. SQLAlchemy의 `pool_size`와 `max_overflow` 설정 고려
