from datetime import date, datetime
from typing import Optional, Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar('T')


class CreateTombstoneDto(BaseModel):
    user_id: int = Field(default=1, description="Always 1 in MVP")
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    unlock_date: date = Field(..., description="Date when tombstone unlocks")


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

    class Config:
        from_attributes = True


class ApiSuccessResponse(BaseModel, Generic[T]):
    status: int
    data: dict  # Contains 'result' and optional 'response'


class ApiErrorResponse(BaseModel):
    status: int
    error: dict  # Contains 'message'
