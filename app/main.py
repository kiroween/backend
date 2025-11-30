"""
TimeGrave API - Main Application Entry Point
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
import json

from app.models.database import init_db
from app.routers import tombstone_router
from app.routers import user as user_router
from app.services.scheduler import start_scheduler, stop_scheduler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Custom JSONResponse to handle Korean characters properly
class UnicodeJSONResponse(JSONResponse):
    def render(self, content) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")


app = FastAPI(
    title="TimeGrave API",
    description="""
# TimeGrave API

디지털 타임캡슐(묘비) 관리 API

## 주요 기능

- 🔐 **사용자 인증**: JWT 기반 회원가입/로그인
- 📝 **묘비 관리**: 디지털 타임캡슐 생성 및 조회
- 🔒 **자동 잠금 해제**: 설정한 날짜에 자동으로 잠금 해제
- 🎙️ **TTS 음성 변환**: 잠금 해제 시 content를 음성으로 변환
- ☁️ **클라우드 저장**: AWS S3에 음성 파일 저장

## 인증 방식

대부분의 API는 JWT Bearer 토큰 인증이 필요합니다.

1. `/api/users/sign-in`으로 로그인
2. 응답의 `session_token` 사용
3. 요청 헤더에 추가: `Authorization: Bearer {session_token}`

## 응답 형식

### 성공 응답
```json
{
  "status": 200,
  "data": {
    "result": { ... },
    "message": "optional message"
  }
}
```

### 오류 응답
```json
{
  "status": 400,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description"
  }
}
```

## 시간대

모든 시간은 **한국 표준시(KST, UTC+9)** 기준입니다.

## 버전

v1.0.0
    """,
    version="1.0.0",
    default_response_class=UnicodeJSONResponse,
    contact={
        "name": "TimeGrave Team",
        "email": "support@timegrave.com"
    },
    license_info={
        "name": "MIT"
    }
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(user_router.router)
app.include_router(tombstone_router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=400,
        content={
            "status": 400,
            "error": {
                "message": "Validation error",
                "details": exc.errors()
            }
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "status": 500,
            "error": {
                "message": "Internal server error"
            }
        }
    )


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": 200,
        "data": {
            "result": {
                "message": "TimeGrave API is running",
                "version": "1.0.0"
            }
        }
    }


@app.on_event("startup")
async def startup_event():
    """Initialize database and scheduler on startup"""
    logger.info("🚀 TimeGrave API starting up...")
    init_db()
    logger.info("✅ Database initialized")
    start_scheduler()
    logger.info("✅ Scheduler started")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("👋 TimeGrave API shutting down...")
    stop_scheduler()
    logger.info("✅ Scheduler stopped")
