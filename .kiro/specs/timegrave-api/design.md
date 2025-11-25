# Design Document

## Overview

TimeGrave API는 RESTful 아키텍처를 기반으로 한 백엔드 서비스로, 타임캡슐(Tombstone) 관리 기능을 제공합니다. 이 시스템은 Python FastAPI 프레임워크를 사용하여 구현되며, SQLite 데이터베이스를 사용하여 데이터를 영구 저장합니다. Docker를 통해 컨테이너화되어 배포됩니다. MVP 버전에서는 단일 사용자(userId=1)만 지원하며, 인증 기능은 포함하지 않습니다.

## Architecture

### System Architecture

```mermaid
graph TB
    Client[Client Application]
    API[API Gateway / Express Router]
    Controller[Controllers]
    Service[Service Layer]
    Repository[Repository Layer]
    DB[(Database)]
    Scheduler[Cron Scheduler]
    
    Client -->|HTTP| API
    API --> Controller
    Controller --> Service
    Service --> Repository
    Repository --> DB
    Scheduler -->|Check Unlock Dates| Service
```

### Layer Responsibilities

1. **API Router (FastAPI Router)**
   - HTTP 요청 라우팅
   - 자동 요청/응답 검증 (Pydantic)
   - CORS 관리
   - OpenAPI 문서 자동 생성

2. **Route Handlers**
   - HTTP 요청 처리
   - Pydantic 모델을 통한 입력 검증
   - 응답 형식 변환

3. **Service Layer**
   - 비즈니스 로직 구현
   - 날짜 계산 및 상태 관리
   - 트랜잭션 관리

4. **Repository Layer**
   - 데이터베이스 쿼리 실행
   - SQLAlchemy ORM 매핑
   - 데이터 접근 추상화

5. **Background Scheduler (APScheduler)**
   - 주기적인 Tombstone 상태 확인
   - 자동 잠금 해제 처리

## Components and Interfaces

### API Endpoints

```
POST /users/sign-in          # 로그인
POST /users/sign-out         # 로그아웃
POST /users                  # 회원가입
DELETE /users                # 회원탈퇴

GET /graves                  # 묘지 대시보드 목록 조회
POST /graves                 # 묘지 생성
GET /graves/{id}             # 묘지 조회
```

### Core Models (Pydantic)

#### Tombstone Model

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Tombstone(BaseModel):
    id: int
    user_id: int
    title: str
    content: str
    unlock_date: datetime
    is_unlocked: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

#### API Response Models

```python
from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar('T')

class ApiSuccessResponse(BaseModel, Generic[T]):
    status: int
    data: dict  # Contains 'result' and optional 'response'

class ApiErrorResponse(BaseModel):
    status: int
    error: dict  # Contains 'message'
```

### Service Interface

#### TombstoneService

```python
from typing import List, Optional

class TombstoneService:
    def create_tombstone(self, data: CreateTombstoneDto) -> Tombstone:
        pass
    
    def get_tombstone(self, tombstone_id: int) -> Optional[Tombstone]:
        pass
    
    def list_tombstones(self) -> List[Tombstone]:
        pass
    
    def check_and_unlock_tombstones(self) -> None:
        pass
```

## Data Models

### Database Schema

#### Tombstones Table

```sql
CREATE TABLE tombstones (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL DEFAULT 1,
  title VARCHAR(255) NOT NULL,
  content TEXT NOT NULL,
  unlock_date DATE NOT NULL,
  is_unlocked BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tombstones_user_id ON tombstones(user_id);
CREATE INDEX idx_tombstones_unlock_date ON tombstones(unlock_date);
CREATE INDEX idx_tombstones_is_unlocked ON tombstones(is_unlocked);
```

### Data Transfer Objects (Pydantic Schemas)

#### CreateTombstoneDto

```python
from pydantic import BaseModel, Field
from datetime import date

class CreateTombstoneDto(BaseModel):
    user_id: int = Field(default=1, description="Always 1 in MVP")
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    unlock_date: date = Field(..., description="Date when tombstone unlocks")
```

#### TombstoneResponseDto

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TombstoneResponseDto(BaseModel):
    id: int
    user_id: int
    title: str
    content: Optional[str] = None  # Only included if unlocked
    unlock_date: str
    is_unlocked: bool
    days_remaining: Optional[int] = None  # Only included if locked
    created_at: str
    updated_at: str
```

### API Request/Response Examples

#### POST /users (회원가입)

**Request:**
```json
{
  "email": "ghost@timegrave.com",
  "password": "eternal2024!",
  "username": "영혼의수호자"
}
```

**Response (201 Created):**
```json
{
  "status": 201,
  "data": {
    "result": {
      "id": 42,
      "email": "ghost@timegrave.com",
      "username": "영혼의수호자",
      "createdAt": "2025-11-26T14:30:00Z"
    },
    "message": "환영합니다, 영혼의수호자님. TimeGrave에 오신 것을 환영합니다."
  }
}
```

**Error Response (400 Bad Request - 이메일 중복):**
```json
{
  "status": 400,
  "error": {
    "code": "EMAIL_ALREADY_EXISTS",
    "message": "이미 사용 중인 이메일입니다."
  }
}
```

#### POST /users/sign-in (로그인)

**Request:**
```json
{
  "email": "ghost@timegrave.com",
  "password": "eternal2024!"
}
```

**Response (200 OK):**
```json
{
  "status": 200,
  "data": {
    "result": {
      "user": {
        "id": 42,
        "email": "ghost@timegrave.com",
        "username": "영혼의수호자"
      },
      "sessionToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "expiresAt": "2025-11-27T14:30:00Z"
    },
    "message": "다시 돌아오신 것을 환영합니다."
  }
}
```

**Error Response (401 Unauthorized):**
```json
{
  "status": 401,
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "이메일 또는 비밀번호가 올바르지 않습니다."
  }
}
```

#### POST /users/sign-out (로그아웃)

**Request Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK):**
```json
{
  "status": 200,
  "data": {
    "message": "안전하게 로그아웃되었습니다. 다음에 또 만나요."
  }
}
```

#### DELETE /users (회원탈퇴)

**Request Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK):**
```json
{
  "status": 200,
  "data": {
    "message": "계정이 영원히 삭제되었습니다. 모든 기억이 함께 사라집니다.",
    "deletedGravesCount": 7
  }
}
```

#### GET /graves (묘지 대시보드 목록 조회)

**Request Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK):**
```json
{
  "status": 200,
  "data": {
    "result": {
      "graves": [
        {
          "id": 15,
          "title": "2024년 여름의 약속",
          "unlockDate": "2030-07-15",
          "isLocked": true,
          "daysRemaining": 1692,
          "createdAt": "2025-11-20T10:00:00Z",
          "preview": "그날의 햇살이 아직도..."
        },
        {
          "id": 8,
          "title": "할머니께 드리는 편지",
          "unlockDate": "2024-12-25",
          "isLocked": false,
          "createdAt": "2023-12-25T00:00:00Z",
          "preview": "할머니, 보고 싶어요..."
        },
        {
          "id": 3,
          "title": "첫 직장의 추억",
          "unlockDate": "2026-03-01",
          "isLocked": true,
          "daysRemaining": 95,
          "createdAt": "2025-01-15T09:30:00Z",
          "preview": "떨리는 마음으로 출근했던..."
        }
      ],
      "totalCount": 3,
      "lockedCount": 2,
      "unlockedCount": 1
    }
  }
}
```

**Response (200 OK - 빈 묘지):**
```json
{
  "status": 200,
  "data": {
    "result": {
      "graves": [],
      "totalCount": 0,
      "lockedCount": 0,
      "unlockedCount": 0
    },
    "message": "아직 묻힌 기억이 없습니다. 첫 번째 기억을 묻어보세요."
  }
}
```

#### POST /graves (묘지 생성)

**Request Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Request Body:**
```json
{
  "title": "파리에서의 마지막 밤",
  "content": "에펠탑 아래에서 마신 와인의 맛, 센강의 야경, 그리고 당신과 나눈 대화. 모든 것이 꿈만 같았어. 10년 후 이 기억을 다시 열어볼 때, 우리는 어떤 모습일까? 여전히 함께일까? 이 순간을 영원히 간직하고 싶어.",
  "unlockDate": "2035-11-26",
  "tags": ["여행", "파리", "추억"],
  "mood": "nostalgic"
}
```

**Response (201 Created):**
```json
{
  "status": 201,
  "data": {
    "result": {
      "id": 24,
      "title": "파리에서의 마지막 밤",
      "unlockDate": "2035-11-26",
      "isLocked": true,
      "daysRemaining": 3652,
      "createdAt": "2025-11-26T15:45:00Z",
      "tags": ["여행", "파리", "추억"],
      "mood": "nostalgic"
    },
    "message": "기억이 안전하게 봉인되었습니다. 3652일 후에 다시 만나요."
  }
}
```

**Error Response (400 Bad Request - 과거 날짜):**
```json
{
  "status": 400,
  "error": {
    "code": "INVALID_UNLOCK_DATE",
    "message": "잠금 해제 날짜는 미래여야 합니다.",
    "field": "unlockDate"
  }
}
```

**Error Response (400 Bad Request - 필수 필드 누락):**
```json
{
  "status": 400,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "필수 항목이 누락되었습니다.",
    "fields": {
      "title": "제목은 필수입니다.",
      "content": "내용은 필수입니다."
    }
  }
}
```

#### GET /graves/{id} (묘지 조회)

**Request Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK - 잠긴 상태):**
```json
{
  "status": 200,
  "data": {
    "result": {
      "id": 24,
      "title": "파리에서의 마지막 밤",
      "unlockDate": "2035-11-26",
      "isLocked": true,
      "daysRemaining": 3652,
      "createdAt": "2025-11-26T15:45:00Z",
      "tags": ["여행", "파리", "추억"],
      "mood": "nostalgic",
      "preview": "에펠탑 아래에서 마신 와인의 맛...",
      "lockMessage": "이 기억은 아직 봉인되어 있습니다. 3652일 후에 열립니다."
    }
  }
}
```

**Response (200 OK - 열린 상태):**
```json
{
  "status": 200,
  "data": {
    "result": {
      "id": 8,
      "title": "할머니께 드리는 편지",
      "content": "할머니, 보고 싶어요. 할머니가 만들어주시던 김치찌개 맛이 그리워요. 할머니의 따뜻한 손길, 부드러운 목소리, 그리고 항상 저를 응원해주시던 그 미소. 모든 것이 그립습니다. 할머니 덕분에 제가 이렇게 성장할 수 있었어요. 감사합니다, 사랑합니다.",
      "unlockDate": "2024-12-25",
      "isLocked": false,
      "unlockedAt": "2024-12-25T00:00:00Z",
      "createdAt": "2023-12-25T00:00:00Z",
      "tags": ["가족", "할머니", "감사"],
      "mood": "grateful",
      "unlockMessage": "봉인이 해제되었습니다. 과거의 당신이 남긴 메시지입니다."
    }
  }
}
```

**Error Response (404 Not Found):**
```json
{
  "status": 404,
  "error": {
    "code": "GRAVE_NOT_FOUND",
    "message": "존재하지 않는 묘지입니다."
  }
}
```

**Error Response (403 Forbidden - 다른 사용자의 묘지):**
```json
{
  "status": 403,
  "error": {
    "code": "ACCESS_DENIED",
    "message": "이 묘지에 접근할 권한이 없습니다."
  }
}
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Graveyard Dashboard Properties

Property 1: Graveyard completeness
*For any* database state, querying the graveyard should return all tombstones with userId=1
**Validates: Requirements 1.1**

Property 2: Locked tombstone days remaining
*For any* locked tombstone, the response should include a daysRemaining field with the correct number of days between current date and unlock date
**Validates: Requirements 1.2**

Property 3: Unlocked tombstone indication
*For any* unlocked tombstone in the graveyard list, the isUnlocked field should be true
**Validates: Requirements 1.3**

### Tombstone Creation Properties

Property 4: Valid tombstone creation
*For any* valid title, content, and future unlock date, creating a tombstone should result in a new tombstone with isUnlocked=false
**Validates: Requirements 2.1**

Property 5: Past date rejection
*For any* unlock date in the past, tombstone creation should be rejected with status 400
**Validates: Requirements 2.2**

Property 6: Tombstone userId assignment
*For any* created tombstone, the userId field should equal 1
**Validates: Requirements 2.3**

Property 7: Creation response format
*For any* successful tombstone creation, the response should have status 201 and include the created tombstone data
**Validates: Requirements 2.4**

Property 8: Required fields validation
*For any* tombstone creation request missing title, content, or unlockDate, the request should be rejected with status 400
**Validates: Requirements 2.5**

### Tombstone Retrieval Properties

Property 9: Unlocked content accessibility
*For any* unlocked tombstone, requesting that tombstone should return the content field in the response
**Validates: Requirements 3.1**

Property 10: Locked content filtering
*For any* locked tombstone, requesting that tombstone should not include the content field in the response
**Validates: Requirements 3.2**

Property 11: Non-existent tombstone error
*For any* non-existent tombstone ID, requesting that tombstone should return status 404
**Validates: Requirements 3.3**

Property 12: Automatic unlock on date
*For any* tombstone with unlock date <= current date, the tombstone should have isUnlocked=true
**Validates: Requirements 3.4, 4.1**

Property 13: Content accessible after unlock
*For any* tombstone that transitions to unlocked state, subsequent requests should include the content field
**Validates: Requirements 4.2**

Property 14: Batch unlock
*For any* set of tombstones with the same unlock date, when that date arrives, all tombstones should have isUnlocked=true
**Validates: Requirements 4.3**

### API Response Format Properties

Property 15: Success response format
*For any* successful API request, the response should include a status field and a data.result field
**Validates: Requirements 5.1**

Property 16: Error response format
*For any* failed API request, the response should include a status field and an error.message field
**Validates: Requirements 5.2**

Property 17: JSON response format
*For any* API response, the content should be valid JSON
**Validates: Requirements 5.3**

Property 18: Creation response message
*For any* successful tombstone creation, the response should include a data.response field with a user-friendly message
**Validates: Requirements 5.4**

## Error Handling

### Error Categories

1. **Validation Errors (400 Bad Request)**
   - Missing required fields (title, content, unlockDate)
   - Invalid date format
   - Past unlock date
   - Invalid data types

2. **Not Found Errors (404 Not Found)**
   - Non-existent tombstone ID

3. **Server Errors (500 Internal Server Error)**
   - Database connection failure
   - Unexpected system errors

### Error Response Format

All error responses follow this structure:

```json
{
  "status": 400,
  "error": {
    "message": "Human-readable error message"
  }
}
```

### Error Handling Strategy

1. **Input Validation**: Validate all inputs at the controller layer before passing to services
2. **Try-Catch Blocks**: Wrap all async operations in try-catch blocks
3. **Logging**: Log all errors with appropriate severity levels
4. **User-Friendly Messages**: Return clear, actionable error messages to clients

## Testing Strategy

### Unit Testing

Unit tests will verify specific functionality of individual components:

- **Service Layer Tests**: Test business logic in isolation using mocked repositories
- **Repository Layer Tests**: Test database queries using a test database
- **Utility Function Tests**: Test date calculation functions

Example unit test cases:
- Test date calculation for days remaining
- Test unlock date validation (past vs future)
- Test tombstone state transitions

### Property-Based Testing

Property-based tests will verify universal properties across many randomly generated inputs using **fast-check** library for Node.js/TypeScript.

Each property-based test will:
- Run a minimum of 100 iterations with randomly generated data
- Be tagged with a comment explicitly referencing the correctness property in the design document
- Use the format: `**Feature: timegrave-api, Property {number}: {property_text}**`

Property test generators will:
- Generate valid and invalid dates (past, present, future)
- Generate various string lengths for title and content
- Generate valid and invalid tombstone IDs
- Generate edge cases (empty strings, very long strings, special characters)

Example property test structure:

```typescript
// **Feature: timegrave-api, Property 4: Valid tombstone creation**
test('Property 4: Valid tombstone creation', async () => {
  await fc.assert(
    fc.asyncProperty(
      fc.string({ minLength: 1, maxLength: 255 }),
      fc.string({ minLength: 1, maxLength: 10000 }),
      fc.date({ min: new Date() }),
      async (title, content, unlockDate) => {
        const result = await tombstoneService.createTombstone({
          userId: 1,
          title,
          content,
          unlockDate: unlockDate.toISOString()
        });
        expect(result.isUnlocked).toBe(false);
        expect(result.userId).toBe(1);
      }
    ),
    { numRuns: 100 }
  );
});
```

### Integration Testing

Integration tests will verify the interaction between multiple components:

- API endpoint tests using supertest
- Database integration tests
- Tombstone lifecycle tests (create → lock → unlock → access)
- Scheduler tests for automatic unlocking

### Test Coverage Goals

- Unit test coverage: 80% minimum
- Property-based tests: One test per correctness property
- Integration tests: Cover all API endpoints

### Testing Tools

- **Test Framework**: pytest
- **Property-Based Testing**: Hypothesis
- **API Testing**: httpx (FastAPI TestClient)
- **Test Database**: SQLite (in-memory for tests)
- **Mocking**: unittest.mock
