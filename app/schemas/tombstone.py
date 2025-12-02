from datetime import date, datetime
from typing import Optional, Generic, TypeVar, List
from pydantic import BaseModel, Field

T = TypeVar('T')


class CreateTombstoneDto(BaseModel):
    user_id: int = Field(default=1, description="Always 1 in MVP")
    title: str = Field(..., min_length=1, max_length=255, description="묘비 제목")
    content: str = Field(..., min_length=1, description="묘비 내용 (잠금 해제 시 TTS로 변환됨)")
    unlock_date: date = Field(..., description="잠금 해제 날짜 (YYYY-MM-DD)")
    enroll: Optional[int] = Field(None, description="작성자 userId (본인 또는 친구)")
    share: Optional[List[int]] = Field(None, description="쓰기 권한 있는 친구들 userId 목록")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "나의 사랑하는 친구들에게",
                    "content": "안녕, 미래의 나야. 오늘은 2025년 12월 1일이야. 1년 후의 너는 어떤 모습일까? 지금의 나는 새로운 도전을 시작하려고 해. 두렵지만 설레기도 해. 1년 후, 이 메시지를 듣는 너는 그 도전을 이뤄냈기를 바라.",
                    "unlock_date": "2026-12-01",
                    "enroll": 1,
                    "share": [2, 3]
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
    share_token: Optional[str] = Field(None, description="공유 링크 토큰 (읽기 전용)")
    invite_token: Optional[str] = Field(None, description="초대 링크 토큰 (쓰기 권한)")
    enroll: Optional[int] = Field(None, description="작성자 userId")
    share: Optional[List[int]] = Field(None, description="쓰기 권한 있는 친구들 userId 목록")
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


class ShareTombstoneResponseDto(BaseModel):
    share_url: str = Field(..., description="공유 링크 URL")
    share_token: str = Field(..., description="공유 토큰")
    expires_at: Optional[str] = Field(None, description="만료 시간 (현재는 무제한)")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "share_url": "https://timegrave.com/shared/abc123xyz",
                    "share_token": "abc123xyz",
                    "expires_at": None
                }
            ]
        }
    }


class SharedTombstoneViewDto(BaseModel):
    id: int = Field(..., description="묘비 ID")
    title: str = Field(..., description="묘비 제목")
    content: str = Field(..., description="묘비 내용")
    audio_url: Optional[str] = Field(None, description="TTS 음성 파일 S3 URL")
    unlock_date: str = Field(..., description="잠금 해제 날짜")
    is_unlocked: bool = Field(..., description="잠금 해제 여부")
    created_at: str = Field(..., description="생성 시간")
    author_username: str = Field(..., description="작성자 이름")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "title": "나의 사랑하는 친구들에게",
                    "content": "안녕, 미래의 나야...",
                    "audio_url": "https://kiroween.s3.ap-northeast-2.amazonaws.com/tombstone_1.mp3",
                    "unlock_date": "2025-12-01",
                    "is_unlocked": True,
                    "created_at": "2025-11-01T10:00:00",
                    "author_username": "홍길동"
                }
            ]
        }
    }


class UpdateShareDto(BaseModel):
    action: str = Field(..., description="add 또는 remove")
    user_id: int = Field(..., description="추가/제거할 친구 userId")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "action": "add",
                    "user_id": 2
                }
            ]
        }
    }


class InviteLinkResponseDto(BaseModel):
    invite_url: str = Field(..., description="초대 링크 URL")
    invite_token: str = Field(..., description="초대 토큰")
    message: str = Field(..., description="안내 메시지")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "invite_url": "https://timegrave.com/invite/abc123xyz",
                    "invite_token": "abc123xyz",
                    "message": "친구들에게 이 링크를 공유하세요. 링크를 통해 가입한 친구는 자동으로 쓰기 권한을 받습니다."
                }
            ]
        }
    }
