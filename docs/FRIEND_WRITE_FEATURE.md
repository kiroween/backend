# 친구 묘비 쓰기 기능

## 개요
친구를 초대하여 함께 묘비를 작성할 수 있는 기능입니다.

## 추가된 필드

### Tombstone 모델
```python
enroll: int         # 작성자 userId (본인 또는 친구)
share: str          # 쓰기 권한 있는 친구들 (JSON array of userIds)
invite_token: str   # 초대 링크용 UUID (쓰기 권한)
share_token: str    # 공유 링크용 토큰 (읽기 전용)
```

### 토큰 구분
- **invite_token**: 쓰기 권한 초대용 (UUID)
- **share_token**: 읽기 전용 공유용 (기존)

## API 엔드포인트

### 1. 묘비 생성 (기존 API 확장)
```http
POST /api/graves
```

**Request Body:**
```json
{
  "title": "우리의 추억",
  "content": "함께 쓰는 타임캡슐",
  "unlock_date": "2026-12-01",
  "enroll": 1,           // 작성자 (생략 시 본인)
  "share": [2, 3]        // 쓰기 권한 있는 친구들
}
```

**Response:**
```json
{
  "status": 201,
  "data": {
    "result": {
      "id": 1,
      "user_id": 1,
      "title": "우리의 추억",
      "unlock_date": "2026-12-01",
      "is_unlocked": false,
      "enroll": 1,
      "share": [2, 3],
      "days_remaining": 365,
      "created_at": "2025-12-02T10:00:00",
      "updated_at": "2025-12-02T10:00:00"
    },
    "response": "기억이 안전하게 봉인되었습니다. 365일 후에 다시 만나요."
  }
}
```

### 2. 쓰기 권한 관리 (신규 API)
```http
PATCH /api/graves/{grave_id}/share
```

**Request Body:**
```json
{
  "action": "add",      // "add" 또는 "remove"
  "user_id": 2          // 추가/제거할 친구 userId
}
```

**Response:**
```json
{
  "status": 200,
  "data": {
    "result": {
      "id": 1,
      "user_id": 1,
      "title": "우리의 추억",
      "unlock_date": "2026-12-01",
      "is_unlocked": false,
      "enroll": 1,
      "share": [2, 3, 4],  // 업데이트된 목록
      "created_at": "2025-12-02T10:00:00",
      "updated_at": "2025-12-02T10:00:00"
    },
    "message": "쓰기 권한이 업데이트되었습니다."
  }
}
```

### 3. 초대 링크 생성 (신규 API - 추천)
```http
POST /api/graves/{grave_id}/invite
```

**Response:**
```json
{
  "status": 200,
  "data": {
    "result": {
      "invite_url": "https://timegrave.com/invite/abc123-xyz-456",
      "invite_token": "abc123-xyz-456",
      "message": "친구들에게 이 링크를 공유하세요. 링크를 통해 가입한 친구는 자동으로 쓰기 권한을 받습니다."
    }
  }
}
```

### 4. 초대 수락 (신규 API)
```http
POST /api/graves/invite/{invite_token}/accept
```

**Response:**
```json
{
  "status": 200,
  "data": {
    "result": {
      "id": 1,
      "user_id": 1,
      "title": "우리의 추억",
      "unlock_date": "2026-12-01",
      "is_unlocked": false,
      "share": [2, 3],
      "created_at": "2025-12-02T10:00:00",
      "updated_at": "2025-12-02T10:00:00"
    },
    "message": "초대를 수락했습니다. 이제 이 묘비에 함께 쓸 수 있습니다."
  }
}
```

## 사용 시나리오

### 시나리오 1: 초대 링크로 친구 초대 (추천 ⭐)
```bash
# 1. 묘비 생성
curl -X POST http://localhost:8000/api/graves \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "우리의 추억",
    "content": "함께 쓰는 타임캡슐",
    "unlock_date": "2026-12-01"
  }'

# 2. 초대 링크 생성
curl -X POST http://localhost:8000/api/graves/1/invite \
  -H "Authorization: Bearer YOUR_TOKEN"

# 3. 친구에게 링크 공유 (카톡, 문자 등)
# https://timegrave.com/invite/abc123-xyz-456

# 4. 친구가 링크 클릭 → 회원가입/로그인

# 5. 친구가 초대 수락
curl -X POST http://localhost:8000/api/graves/invite/abc123-xyz-456/accept \
  -H "Authorization: Bearer FRIEND_TOKEN"
```

### 시나리오 2: 친구 초대하여 묘비 생성
```bash
# 1. 묘비 생성 시 친구 추가
curl -X POST http://localhost:8000/api/graves \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "우리의 추억",
    "content": "함께 쓰는 타임캡슐",
    "unlock_date": "2026-12-01",
    "share": [2, 3]
  }'
```

### 시나리오 2: 나중에 친구 추가
```bash
# 1. 묘비 생성 (친구 없이)
curl -X POST http://localhost:8000/api/graves \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "우리의 추억",
    "content": "함께 쓰는 타임캡슐",
    "unlock_date": "2026-12-01"
  }'

# 2. 친구 추가
curl -X PATCH http://localhost:8000/api/graves/1/share \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "add",
    "user_id": 2
  }'
```

### 시나리오 3: 친구 제거
```bash
curl -X PATCH http://localhost:8000/api/graves/1/share \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "remove",
    "user_id": 2
  }'
```

## 권한 체크

### 묘비 주인만 가능한 작업
- 쓰기 권한 추가/제거 (`PATCH /api/graves/{grave_id}/share`)
- 묘비 삭제 (향후 구현)

### share 배열에 있는 친구들이 가능한 작업 (향후 구현)
- 묘비 내용 수정
- 묘비 조회

## 데이터 저장 방식

### enroll 필드
- 타입: `INTEGER`
- 의미: 작성자 userId
- 기본값: 묘비 주인 (user_id)

### share 필드
- 타입: `TEXT` (JSON array)
- 의미: 쓰기 권한 있는 친구들의 userId 목록
- 예시: `"[2, 3, 4]"`
- 파싱: `json.loads(tombstone.share)` → `[2, 3, 4]`

### invite_token 필드
- 타입: `VARCHAR(100)` (UUID)
- 의미: 초대 링크용 고유 토큰
- 예시: `"abc123-xyz-456-789"`
- 특징: 여러 친구가 같은 링크로 참여 가능

### share_token vs invite_token
| 구분 | share_token | invite_token |
|------|-------------|--------------|
| 용도 | 읽기 전용 공유 | 쓰기 권한 초대 |
| 생성 | `POST /api/graves/{id}/share` | `POST /api/graves/{id}/invite` |
| 수락 | `GET /api/graves/shared/{token}` | `POST /api/graves/invite/{token}/accept` |
| 권한 | 조회만 가능 | share 배열에 추가 |

## 마이그레이션

```sql
-- 1. enroll, share 필드 추가
ALTER TABLE tombstones ADD COLUMN enroll INTEGER;
ALTER TABLE tombstones ADD COLUMN share TEXT;
CREATE INDEX IF NOT EXISTS idx_tombstones_enroll ON tombstones(enroll);
UPDATE tombstones SET enroll = user_id WHERE enroll IS NULL;

-- 2. invite_token 필드 추가
ALTER TABLE tombstones ADD COLUMN invite_token VARCHAR(100);
CREATE UNIQUE INDEX IF NOT EXISTS idx_tombstones_invite_token ON tombstones(invite_token);
```

## 초대 링크 플로우

```
[묘비 주인]
    ↓
1. POST /api/graves/{id}/invite
    ↓
2. invite_token (UUID) 생성
    ↓
3. 링크 공유 (카톡, 문자 등)
    ↓
[친구]
    ↓
4. 링크 클릭 → 회원가입/로그인
    ↓
5. POST /api/graves/invite/{token}/accept
    ↓
6. share 배열에 자동 추가
    ↓
7. 쓰기 권한 획득 ✅
```

## 향후 개선 사항

1. **권한 체크 미들웨어**
   - share 배열에 있는 친구도 묘비 수정 가능하도록

3. **알림 기능**
   - 친구가 추가되면 알림 전송
   - 친구가 묘비를 수정하면 알림 전송

4. **UI 개선**
   - 친구 목록 표시
   - 친구 검색 기능
   - 드래그 앤 드롭으로 친구 추가
