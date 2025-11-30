from datetime import date, datetime
from typing import Optional, Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar('T')


class CreateTombstoneDto(BaseModel):
    user_id: int = Field(default=1, description="Always 1 in MVP")
    title: str = Field(..., min_length=1, max_length=255, description="묘비 제목")
    content: str = Field(..., min_length=1, description="묘비 내용 (잠금 해제 시 TTS로 변환됨)")
    unlock_date: date = Field(..., description="잠금 해제 날짜 (YYYY-MM-DD)")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "나의 사랑하는 친구들에게",
                    "content": "안녕, 미래의 나야. 오늘은 2025년 12월 1일이야. 1년 후의 너는 어떤 모습일까? 지금의 나는 새로운 도전을 시작하려고 해. 두렵지만 설레기도 해. 1년 후, 이 메시지를 듣는 너는 그 도전을 이뤄냈기를 바라.",
                    "unlock_date": "2026-12-01"
                }
            ]
        }
    }


class TombstoneResponseDto(BaseModel):
    id: int = Field(..., description="묘비 ID")
    user_id: int = Field(..., description="사용자 ID")
    title: str = Field(..., description="묘비 제목")
    content: Optional[str] = Field(None, description="묘비 내용 (잠금 해제된 경우에만 포함)")
    audio_url: Optional[str] = Field(None, description="TTS 음성 파일 S3 URL (잠금 해제된 경우에만 포함)")
    unlock_date: str = Field(..., description="잠금 해제 날짜 (ISO 8601)")
    is_unlocked: bool = Field(..., description="잠금 해제 여부")
    days_remaining: Optional[int] = Field(None, description="잠금 해제까지 남은 일수 (잠금 상태인 경우에만 포함)")
    created_at: str = Field(..., description="생성 시간 (ISO 8601, KST)")
    updated_at: str = Field(..., description="수정 시간 (ISO 8601, KST)")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "user_id": 1,
                    "title": "나의 사랑하는 친구들에게",
                    "content": "안녕, 미래의 나야. 오늘은 2025년 12월 1일이야...",
                    "audio_url": "https://kiroween.s3.ap-northeast-2.amazonaws.com/tombstone_1_1_1733011200.123.mp3",
                    "unlock_date": "2025-12-01",
                    "is_unlocked": True,
                    "created_at": "2025-12-01T10:30:00",
                    "updated_at": "2025-12-01T10:30:00"
                }
            ]
        }
    }


class ApiSuccessResponse(BaseModel, Generic[T]):
    status: int
    data: dict  # Contains 'result' and optional 'response'


class ApiErrorResponse(BaseModel):
    status: int
    error: dict  # Contains 'message'
