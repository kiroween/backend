# 친구 초대 기능 테스트 가이드

## 사전 준비

### 1. 서버 실행
```bash
# 개발 서버 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 테스트용 사용자 2명 준비
- **사용자 A** (묘비 주인): user_id=1, token=TOKEN_A
- **사용자 B** (친구): user_id=2, token=TOKEN_B

회원가입이 필요하면:
```bash
# 사용자 A 회원가입
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user_a",
    "password": "password123",
    "email": "usera@example.com"
  }'

# 사용자 B 회원가입
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user_b",
    "password": "password123",
    "email": "userb@example.com"
  }'
```

로그인:
```bash
# 사용자 A 로그인
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user_a",
    "password": "password123"
  }'
# 응답에서 access_token 복사 → TOKEN_A

# 사용자 B 로그인
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user_b",
    "password": "password123"
  }'
# 응답에서 access_token 복사 → TOKEN_B
```

---

## 테스트 시나리오

### 시나리오 1: 초대 링크로 친구 초대 (추천 ⭐)

#### Step 1: 사용자 A가 묘비 생성
```bash
curl -X POST http://localhost:8000/api/graves \
  -H "Authorization: Bearer TOKEN_A" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "우리의 추억",
    "content": "함께 쓰는 타임캡슐입니다",
    "unlock_date": "2026-12-01"
  }'

# 참고: enroll, share는 선택사항입니다
# 생략하면 enroll은 자동으로 본인(user_id)으로 설정됩니다
```

**예상 응답:**
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
      "share": null,
      "days_remaining": 365
    },
    "response": "기억이 안전하게 봉인되었습니다. 365일 후에 다시 만나요."
  }
}
```

#### Step 2: 사용자 A가 초대 링크 생성
```bash
curl -X POST http://localhost:8000/api/graves/1/invite \
  -H "Authorization: Bearer TOKEN_A"
```

**예상 응답:**
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

**✅ invite_token 복사하기!** (예: `abc123-xyz-456`)

#### Step 3: 사용자 B가 초대 수락
```bash
# invite_token을 실제 값으로 교체
curl -X POST http://localhost:8000/api/graves/invite/abc123-xyz-456/accept \
  -H "Authorization: Bearer TOKEN_B"
```

**예상 응답:**
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
      "share": [2],  // ← 사용자 B가 추가됨!
      "days_remaining": 365
    },
    "message": "초대를 수락했습니다. 이제 이 묘비에 함께 쓸 수 있습니다."
  }
}
```

#### Step 4: 확인 - 사용자 A가 묘비 조회
```bash
curl -X GET http://localhost:8000/api/graves/1 \
  -H "Authorization: Bearer TOKEN_A"
```

**예상 응답:**
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
      "share": [2],  // ← 사용자 B가 share 배열에 있음!
      "days_remaining": 365
    }
  }
}
```

---

### 시나리오 2: 묘비 생성 시 친구 미리 추가 (선택사항)

#### Step 1: 사용자 A가 묘비 생성하면서 친구 추가
```bash
curl -X POST http://localhost:8000/api/graves \
  -H "Authorization: Bearer TOKEN_A" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "우리의 추억",
    "content": "함께 쓰는 타임캡슐입니다",
    "unlock_date": "2026-12-01",
    "enroll": 1,
    "share": [2, 3]
  }'
```

**예상 응답:**
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

**✅ 이미 userId를 알고 있는 친구를 바로 추가 가능!**

---

### 시나리오 3: 수동으로 친구 추가/제거

#### Step 1: 사용자 A가 사용자 B를 수동 추가
```bash
curl -X PATCH http://localhost:8000/api/graves/1/share \
  -H "Authorization: Bearer TOKEN_A" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "add",
    "user_id": 2
  }'
```

**예상 응답:**
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
      "share": [2],
      "days_remaining": 365,
      "created_at": "2025-12-02T10:00:00",
      "updated_at": "2025-12-02T10:00:00"
    },
    "message": "쓰기 권한이 업데이트되었습니다."
  }
}
```

#### Step 2: 사용자 A가 사용자 B를 제거
```bash
curl -X PATCH http://localhost:8000/api/graves/1/share \
  -H "Authorization: Bearer TOKEN_A" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "remove",
    "user_id": 2
  }'
```

**예상 응답:**
```json
{
  "status": 200,
  "data": {
    "result": {
      "id": 1,
      "share": []  // ← 제거됨
    },
    "message": "쓰기 권한이 업데이트되었습니다."
  }
}
```

---

### 시나리오 4: 여러 친구 초대

#### Step 1: 사용자 C도 같은 초대 링크로 수락
```bash
# 사용자 C 로그인 후
curl -X POST http://localhost:8000/api/graves/invite/abc123-xyz-456/accept \
  -H "Authorization: Bearer TOKEN_C"
```

**예상 응답:**
```json
{
  "status": 200,
  "data": {
    "result": {
      "id": 1,
      "share": [2, 3]  // ← 사용자 B, C 모두 추가됨!
    },
    "message": "초대를 수락했습니다. 이제 이 묘비에 함께 쓸 수 있습니다."
  }
}
```

---

## 공유 링크 vs 초대 링크 차이점

### 1. 공유 링크 (share_token) - 읽기 전용
```bash
# 생성
curl -X POST http://localhost:8000/api/graves/1/share \
  -H "Authorization: Bearer TOKEN_A"

# 조회 (로그인 필요)
curl -X GET http://localhost:8000/api/graves/shared/{share_token} \
  -H "Authorization: Bearer TOKEN_B"
```

**용도:**
- ✅ 잠금 해제된 묘비를 친구에게 보여주기
- ✅ 읽기 전용 (수정 불가)
- ✅ 복사 가능 (`POST /api/graves/shared/{share_token}/copy`)

### 2. 초대 링크 (invite_token) - 쓰기 권한
```bash
# 생성
curl -X POST http://localhost:8000/api/graves/1/invite \
  -H "Authorization: Bearer TOKEN_A"

# 수락 (로그인 필요)
curl -X POST http://localhost:8000/api/graves/invite/{invite_token}/accept \
  -H "Authorization: Bearer TOKEN_B"
```

**용도:**
- ✅ 친구를 공동 작성자로 초대
- ✅ 쓰기 권한 부여 (share 배열에 추가)
- ✅ 여러 친구가 같은 링크로 참여 가능

---

## 에러 케이스 테스트

### 1. 권한 없는 사용자가 초대 링크 생성 시도
```bash
# 사용자 B가 사용자 A의 묘비에 초대 링크 생성 시도
curl -X POST http://localhost:8000/api/graves/1/invite \
  -H "Authorization: Bearer TOKEN_B"
```

**예상 응답:**
```json
{
  "status": 403,
  "error": {
    "message": "You don't have permission to create invite link for this tombstone"
  }
}
```

### 2. 잘못된 초대 토큰으로 수락 시도
```bash
curl -X POST http://localhost:8000/api/graves/invite/invalid-token/accept \
  -H "Authorization: Bearer TOKEN_B"
```

**예상 응답:**
```json
{
  "status": 404,
  "error": {
    "message": "Invalid invite token"
  }
}
```

### 3. 중복 수락 (이미 share 배열에 있는 경우)
```bash
# 사용자 B가 다시 수락 시도
curl -X POST http://localhost:8000/api/graves/invite/abc123-xyz-456/accept \
  -H "Authorization: Bearer TOKEN_B"
```

**예상 응답:**
```json
{
  "status": 200,
  "data": {
    "result": {
      "id": 1,
      "share": [2]  // ← 중복 추가 안 됨 (그대로 유지)
    },
    "message": "초대를 수락했습니다. 이제 이 묘비에 함께 쓸 수 있습니다."
  }
}
```

---

## Swagger UI로 테스트

더 쉬운 방법:

1. 브라우저에서 http://localhost:8000/docs 접속
2. 우측 상단 **Authorize** 버튼 클릭
3. Bearer Token 입력 (예: `TOKEN_A`)
4. API 엔드포인트 선택:
   - `POST /api/graves/{grave_id}/invite` - 초대 링크 생성
   - `POST /api/graves/invite/{invite_token}/accept` - 초대 수락
   - `PATCH /api/graves/{grave_id}/share` - 수동 추가/제거
5. **Try it out** 클릭 → 파라미터 입력 → **Execute**

---

## 데이터베이스 직접 확인

```bash
# share 필드 확인
sqlite3 data/timegrave.db "SELECT id, user_id, title, enroll, share, invite_token FROM tombstones;"

# 예상 결과:
# 1|1|우리의 추억|1|[2,3]|abc123-xyz-456
```

---

## 빠른 테스트 스크립트

```bash
#!/bin/bash

# 환경 변수 설정
export TOKEN_A="your_token_a_here"
export TOKEN_B="your_token_b_here"

echo "1. 묘비 생성..."
curl -X POST http://localhost:8000/api/graves \
  -H "Authorization: Bearer $TOKEN_A" \
  -H "Content-Type: application/json" \
  -d '{"title":"테스트 묘비","content":"테스트 내용","unlock_date":"2026-12-01"}'

echo -e "\n\n2. 초대 링크 생성..."
INVITE_RESPONSE=$(curl -s -X POST http://localhost:8000/api/graves/1/invite \
  -H "Authorization: Bearer $TOKEN_A")
echo $INVITE_RESPONSE

# invite_token 추출 (jq 필요)
INVITE_TOKEN=$(echo $INVITE_RESPONSE | jq -r '.data.result.invite_token')
echo "Invite Token: $INVITE_TOKEN"

echo -e "\n\n3. 친구가 초대 수락..."
curl -X POST http://localhost:8000/api/graves/invite/$INVITE_TOKEN/accept \
  -H "Authorization: Bearer $TOKEN_B"

echo -e "\n\n4. 묘비 확인..."
curl -X GET http://localhost:8000/api/graves/1 \
  -H "Authorization: Bearer $TOKEN_A"
```

---

## 체크리스트

- [ ] 서버 실행 확인
- [ ] 사용자 A, B 로그인 및 토큰 획득
- [ ] 묘비 생성 성공
- [ ] 초대 링크 생성 성공
- [ ] invite_token 확인
- [ ] 친구가 초대 수락 성공
- [ ] share 배열에 친구 userId 추가 확인
- [ ] 중복 수락 시 중복 추가 안 됨 확인
- [ ] 권한 없는 사용자 접근 차단 확인
- [ ] 잘못된 토큰 에러 처리 확인

모두 통과하면 ✅ 완료!
