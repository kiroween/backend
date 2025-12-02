# TimeGrave API 문서

## 개요

TimeGrave는 디지털 타임캡슐(묘비) 관리 API입니다. 사용자는 미래의 특정 날짜에 열리는 타임캡슐을 생성하고, 설정한 날짜가 되면 자동으로 잠금이 해제되어 내용을 확인할 수 있습니다.

## Base URL

- **개발**: `http://localhost:8000`
- **프로덕션**: `http://your-domain.com`

## Swagger UI

- **URL**: `http://localhost:8000/docs`
- 모든 API를 브라우저에서 직접 테스트할 수 있습니다

## 인증

### JWT Bearer Token

대부분의 API는 JWT 인증이 필요합니다.

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 인증 플로우

1. **회원가입** → `POST /api/users`
2. **로그인** → `POST /api/users/sign-in`
3. **토큰 사용** → 다른 API 호출 시 헤더에 포함

---

## API 엔드포인트

### 1. 사용자 관리

#### 1.1 회원가입

```http
POST /api/users
Content-Type: application/json
```

**요청 예시:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123!",
  "username": "김타임"
}
```

**응답 예시 (201):**
```json
{
  "status": 201,
  "data": {
    "result": {
      "id": 1,
      "email": "user@example.com",
      "username": "김타임",
      "created_at": "2025-12-01T10:00:00"
    },
    "message": "환영합니다, 김타임님. TimeGrave에 오신 것을 환영합니다."
  }
}
```

**오류 응답 (400):**
```json
{
  "status": 400,
  "error": {
    "code": "EMAIL_ALREADY_EXISTS",
    "message": "이미 사용 중인 이메일입니다."
  }
}
```

#### 1.2 로그인

```http
POST /api/users/sign-in
Content-Type: application/json
```

**요청 예시:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123!"
}
```

**응답 예시 (200):**
```json
{
  "status": 200,
  "data": {
    "result": {
      "user": {
        "id": 1,
        "email": "user@example.com",
        "username": "김타임"
      },
      "session_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "expires_at": "2025-12-01T10:30:00"
    },
    "message": "다시 돌아오신 것을 환영합니다."
  }
}
```

#### 1.3 로그아웃

```http
POST /api/users/sign-out
Authorization: Bearer {token}
```

**응답 예시 (200):**
```json
{
  "status": 200,
  "data": {
    "message": "안전하게 로그아웃되었습니다. 다음에 또 만나요."
  }
}
```

#### 1.4 회원탈퇴

```http
DELETE /api/users
Authorization: Bearer {token}
```

**응답 예시 (200):**
```json
{
  "status": 200,
  "data": {
    "message": "계정이 영원히 삭제되었습니다. 모든 기억이 함께 사라집니다.",
    "deleted_graves_count": 5
  }
}
```

---

### 2. 묘비(타임캡슐) 관리

#### 2.1 묘비 목록 조회

```http
GET /api/graves
Authorization: Bearer {token}
```

**응답 예시 (200):**
```json
{
  "status": 200,
  "data": {
    "result": [
      {
        "id": 1,
        "user_id": 1,
        "title": "나의 사랑하는 친구들에게",
        "unlock_date": "2025-12-01",
        "is_unlocked": true,
        "created_at": "2025-11-01T10:00:00",
        "updated_at": "2025-12-01T00:00:00"
      },
      {
        "id": 2,
        "user_id": 1,
        "title": "1년 후의 나에게",
        "unlock_date": "2026-12-01",
        "is_unlocked": false,
        "days_remaining": 365,
        "created_at": "2025-12-01T10:00:00",
        "updated_at": "2025-12-01T10:00:00"
      }
    ]
  }
}
```

**특징:**
- 잠금 상태: `days_remaining` 포함
- 잠금 해제 상태: `days_remaining` 없음
- `content`는 상세 조회에서만 제공

#### 2.2 묘비 생성

```http
POST /api/graves
Authorization: Bearer {token}
Content-Type: application/json
```

**요청 예시:**
```json
{
  "title": "나의 사랑하는 친구들에게",
  "content": "안녕, 미래의 나야. 오늘은 2025년 12월 1일이야. 1년 후의 너는 어떤 모습일까? 지금의 나는 새로운 도전을 시작하려고 해. 두렵지만 설레기도 해. 1년 후, 이 메시지를 듣는 너는 그 도전을 이뤄냈기를 바라.",
  "unlock_date": "2026-12-01"
}
```

**응답 예시 (201):**
```json
{
  "status": 201,
  "data": {
    "result": {
      "id": 1,
      "user_id": 1,
      "title": "나의 사랑하는 친구들에게",
      "unlock_date": "2026-12-01",
      "is_unlocked": false,
      "days_remaining": 365,
      "created_at": "2025-12-01T10:00:00",
      "updated_at": "2025-12-01T10:00:00"
    },
    "response": "기억이 안전하게 봉인되었습니다. 365일 후에 다시 만나요."
  }
}
```

**오류 응답 (400):**
```json
{
  "status": 400,
  "error": {
    "message": "Unlock date must be in the future"
  }
}
```

#### 2.3 묘비 상세 조회

```http
GET /api/graves/{grave_id}
Authorization: Bearer {token}
```

**응답 예시 - 잠금 상태 (200):**
```json
{
  "status": 200,
  "data": {
    "result": {
      "id": 1,
      "user_id": 1,
      "title": "나의 사랑하는 친구들에게",
      "unlock_date": "2026-12-01",
      "is_unlocked": false,
      "days_remaining": 365,
      "created_at": "2025-12-01T10:00:00",
      "updated_at": "2025-12-01T10:00:00"
    }
  }
}
```

**응답 예시 - 잠금 해제 (200):**
```json
{
  "status": 200,
  "data": {
    "result": {
      "id": 1,
      "user_id": 1,
      "title": "나의 사랑하는 친구들에게",
      "content": "안녕, 미래의 나야. 오늘은 2025년 12월 1일이야...",
      "audio_url": "https://kiroween.s3.ap-northeast-2.amazonaws.com/tombstone_1_1_1733011200.123.mp3",
      "unlock_date": "2025-12-01",
      "is_unlocked": true,
      "created_at": "2025-11-01T10:00:00",
      "updated_at": "2025-12-01T00:00:00"
    }
  }
}
```

**특징:**
- 잠금 해제 시 첫 조회: TTS 자동 생성 → S3 업로드 → `audio_url` 저장
- 이후 조회: 저장된 `audio_url` 재사용

**오류 응답 (404):**
```json
{
  "status": 404,
  "error": {
    "message": "Grave not found"
  }
}
```

**오류 응답 (403):**
```json
{
  "status": 403,
  "error": {
    "code": "ACCESS_DENIED",
    "message": "이 묘지에 접근할 권한이 없습니다."
  }
}
```

#### 2.4 수동 잠금 해제 체크 (테스트용)

```http
POST /api/graves/unlock-check
Authorization: Bearer {token}
```

**응답 예시 (200):**
```json
{
  "status": 200,
  "data": {
    "result": {
      "unlocked_count": 3,
      "message": "3개의 묘비가 잠금 해제되었습니다."
    }
  }
}
```

**용도:**
- 개발/테스트 환경에서 즉시 확인
- 자정 스케줄러를 기다리지 않고 수동 실행

---

### 3. 묘비 공유 기능

#### 3.1 공유 링크 생성

```http
POST /api/graves/{grave_id}/share
Authorization: Bearer {token}
```

**응답 예시 (200):**
```json
{
  "status": 200,
  "data": {
    "result": {
      "share_url": "https://timegrave.com/shared/abc123xyz",
      "share_token": "abc123xyz",
      "expires_at": null
    },
    "message": "공유 링크가 생성되었습니다. 친구에게 전달하세요!"
  }
}
```

**오류 응답 (403):**
```json
{
  "status": 403,
  "error": {
    "message": "You don't have permission to share this tombstone"
  }
}
```

**특징:**
- 본인의 묘비만 공유 가능
- 고유한 share_token 생성
- 링크는 무제한 유효 (expires_at: null)

#### 3.2 공유된 묘비 조회

```http
GET /api/graves/shared/{share_token}
Authorization: Bearer {token}
```

**응답 예시 (200):**
```json
{
  "status": 200,
  "data": {
    "result": {
      "id": 1,
      "title": "나의 사랑하는 친구들에게",
      "content": "안녕, 미래의 나야...",
      "audio_url": "https://kiroween.s3.ap-northeast-2.amazonaws.com/tombstone_1.mp3",
      "unlock_date": "2025-12-01",
      "is_unlocked": true,
      "created_at": "2025-11-01T10:00:00",
      "author_username": "홍길동"
    }
  }
}
```

**오류 응답 (404):**
```json
{
  "status": 404,
  "error": {
    "message": "유효하지 않은 공유 링크입니다."
  }
}
```

**오류 응답 (403):**
```json
{
  "status": 403,
  "error": {
    "message": "아직 잠금 해제되지 않은 묘비입니다."
  }
}
```

**특징:**
- 회원가입/로그인 필수
- 잠금 해제된 묘비만 조회 가능
- 작성자 이름 포함

#### 3.3 공유된 묘비를 내 계정에 저장

```http
POST /api/graves/shared/{share_token}/copy
Authorization: Bearer {token}
```

**응답 예시 (201):**
```json
{
  "status": 201,
  "data": {
    "result": {
      "id": 5,
      "user_id": 2,
      "title": "[공유받음] 나의 사랑하는 친구들에게",
      "content": "안녕, 미래의 나야...",
      "audio_url": "https://kiroween.s3.ap-northeast-2.amazonaws.com/tombstone_1.mp3",
      "unlock_date": "2025-12-01",
      "is_unlocked": true,
      "created_at": "2025-12-02T15:30:00",
      "updated_at": "2025-12-02T15:30:00"
    },
    "message": "친구의 묘비가 내 계정에 저장되었습니다."
  }
}
```

**오류 응답 (404):**
```json
{
  "status": 404,
  "error": {
    "message": "유효하지 않은 공유 링크입니다."
  }
}
```

**오류 응답 (403):**
```json
{
  "status": 403,
  "error": {
    "message": "This tombstone is not yet unlocked and cannot be shared"
  }
}
```

**특징:**
- 회원가입/로그인 필수
- 잠금 해제된 묘비만 복사 가능
- 제목에 "[공유받음]" 접두사 자동 추가
- 동일한 audio_url 재사용 (중복 생성 방지)
- 복사본은 자동으로 잠금 해제 상태

---

## 자동 잠금 해제

### 스케줄러

- **실행 시간**: 매일 자정 00:00 (KST)
- **동작**: `unlock_date <= 오늘` 인 묘비를 `is_unlocked = true`로 변경
- **자동 실행**: 사용자 개입 불필요

### TTS 생성

- **시점**: 잠금 해제된 묘비를 처음 조회할 때
- **과정**: content → TTS 음성 생성 → S3 업로드 → DB에 `audio_url` 저장
- **재사용**: 이후 조회 시 저장된 `audio_url` 사용 (중복 생성 방지)

---

## 오류 코드

| 상태 코드 | 오류 코드 | 설명 |
|---------|---------|------|
| 400 | `EMAIL_ALREADY_EXISTS` | 이미 사용 중인 이메일 |
| 400 | `VALIDATION_ERROR` | 입력값 검증 실패 |
| 401 | `INVALID_CREDENTIALS` | 이메일 또는 비밀번호 불일치 |
| 401 | `UNAUTHORIZED` | 인증 토큰 없음 또는 만료 |
| 403 | `ACCESS_DENIED` | 권한 없음 |
| 404 | - | 리소스를 찾을 수 없음 |
| 500 | - | 서버 내부 오류 |

---

## 시간대

모든 시간은 **한국 표준시(KST, UTC+9)** 기준입니다.

- `created_at`: 생성 시간 (KST)
- `updated_at`: 수정 시간 (KST)
- `unlock_date`: 잠금 해제 날짜 (날짜만, 시간 없음)
- `expires_at`: 토큰 만료 시간 (KST)

---

## 제약사항

### 사용자
- 이메일: 유효한 이메일 형식
- 비밀번호: 8-72자
- 사용자 이름: 1-100자

### 묘비
- 제목: 1-255자
- 내용: 1자 이상
- 잠금 해제 날짜: 미래 날짜여야 함

---

## 예제 코드

### JavaScript (Fetch)

```javascript
// 로그인
const loginResponse = await fetch('http://localhost:8000/api/users/sign-in', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'securePassword123!'
  })
});

const { data } = await loginResponse.json();
const token = data.result.session_token;

// 묘비 목록 조회
const gravesResponse = await fetch('http://localhost:8000/api/graves', {
  headers: { 'Authorization': `Bearer ${token}` }
});

const graves = await gravesResponse.json();
console.log(graves);
```

### Python (requests)

```python
import requests

# 로그인
response = requests.post('http://localhost:8000/api/users/sign-in', json={
    'email': 'user@example.com',
    'password': 'securePassword123!'
})

token = response.json()['data']['result']['session_token']

# 묘비 목록 조회
headers = {'Authorization': f'Bearer {token}'}
graves = requests.get('http://localhost:8000/api/graves', headers=headers)

print(graves.json())
```

### cURL

```bash
# 로그인
curl -X POST http://localhost:8000/api/users/sign-in \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"securePassword123!"}'

# 묘비 목록 조회
curl -X GET http://localhost:8000/api/graves \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 참고 자료

- [Swagger UI](http://localhost:8000/docs) - 대화형 API 문서
- [ReDoc](http://localhost:8000/redoc) - 읽기 전용 API 문서
- [GitHub Repository](https://github.com/kiroween/backend)
