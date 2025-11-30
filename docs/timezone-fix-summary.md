# 시간대 문제 해결 요약

## 문제
- Docker 컨테이너는 KST로 설정되었지만, Python의 `datetime.utcnow()`가 UTC 시간을 사용
- 생성 시간이 실제보다 9시간 느리게 기록됨
- 스케줄러가 UTC 기준으로 작동하여 잠금 해제 시간이 맞지 않음

## 해결 방법

### 1. 유틸리티 함수 생성 (`app/utils/datetime_utils.py`)
```python
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))

def now_kst() -> datetime:
    """현재 한국 시간을 반환"""
    return datetime.now(KST)
```

### 2. 모델 수정
- `app/models/tombstone.py`: `datetime.utcnow` → `get_kst_now`
- `app/models/user.py`: `datetime.utcnow` → `get_kst_now`

### 3. 서비스 수정
- `app/services/tombstone_service.py`: 파일명 생성 시 `now_kst()` 사용

## 변경 전후 비교

### 변경 전
```python
created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
# 결과: 2025-11-30T17:31:01 (UTC 시간)
```

### 변경 후
```python
created_at = Column(DateTime, default=get_kst_now, nullable=False)
# 결과: 2025-12-01T02:31:01 (KST 시간)
```

## 배포 후 확인

### 1. 새 묘비 생성
```bash
POST /api/graves
{
  "title": "테스트",
  "content": "시간 확인",
  "unlock_date": "2025-12-02"
}
```

### 2. 생성 시간 확인
```json
{
  "created_at": "2025-12-01T02:40:00",  // KST 시간
  "updated_at": "2025-12-01T02:40:00"   // KST 시간
}
```

### 3. 스케줄러 확인
```bash
POST /api/graves/unlock-check
```

```json
{
  "current_date": "2025-12-01",  // 현재 한국 날짜
  "unlocked_count": 1
}
```

## 주의사항

1. **기존 데이터**: 이미 생성된 데이터는 UTC 시간으로 저장되어 있습니다. 필요시 마이그레이션 필요.

2. **SQLite 호환성**: SQLite는 timezone-aware datetime을 지원하지 않으므로 naive datetime으로 저장합니다.

3. **PostgreSQL 사용 시**: timezone-aware datetime을 그대로 사용할 수 있습니다.

## 기존 데이터 마이그레이션 (선택사항)

기존 데이터를 KST로 변환하려면:

```sql
-- SQLite
UPDATE tombstones 
SET created_at = datetime(created_at, '+9 hours'),
    updated_at = datetime(updated_at, '+9 hours');

UPDATE users 
SET created_at = datetime(created_at, '+9 hours'),
    updated_at = datetime(updated_at, '+9 hours');
```

```sql
-- PostgreSQL
UPDATE tombstones 
SET created_at = created_at + INTERVAL '9 hours',
    updated_at = updated_at + INTERVAL '9 hours';

UPDATE users 
SET created_at = created_at + INTERVAL '9 hours',
    updated_at = updated_at + INTERVAL '9 hours';
```

## 테스트

```bash
# 1. 배포
cd deploy
./deploy.sh

# 2. 컨테이너 시간 확인
sudo docker exec timegrave-api date
# 출력: Mon Dec  1 02:40:14 KST 2025

# 3. 새 묘비 생성 후 시간 확인
# created_at이 현재 KST 시간과 일치해야 함

# 4. 스케줄러 테스트
POST /api/graves/unlock-check
# current_date가 오늘 날짜와 일치해야 함
```
