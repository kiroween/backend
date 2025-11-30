from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class UserSignUpDto(BaseModel):
    email: EmailStr = Field(..., description="이메일 주소")
    password: str = Field(..., min_length=8, max_length=72, description="비밀번호 (8-72자)")
    username: str = Field(..., min_length=1, max_length=100, description="사용자 이름")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "user@example.com",
                    "password": "securePassword123!",
                    "username": "김타임"
                }
            ]
        }
    }


class UserSignInDto(BaseModel):
    email: EmailStr = Field(..., description="이메일 주소")
    password: str = Field(..., description="비밀번호")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "user@example.com",
                    "password": "securePassword123!"
                }
            ]
        }
    }


class UserResponseDto(BaseModel):
    id: int = Field(..., description="사용자 ID")
    email: str = Field(..., description="이메일 주소")
    username: str = Field(..., description="사용자 이름")
    created_at: str = Field(..., description="가입 시간 (ISO 8601, KST)")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "email": "user@example.com",
                    "username": "김타임",
                    "created_at": "2025-12-01T10:00:00"
                }
            ]
        }
    }


class TokenResponseDto(BaseModel):
    user: UserResponseDto = Field(..., description="사용자 정보")
    session_token: str = Field(..., description="JWT 세션 토큰")
    expires_at: str = Field(..., description="토큰 만료 시간 (ISO 8601)")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user": {
                        "id": 1,
                        "email": "user@example.com",
                        "username": "김타임",
                        "created_at": "2025-12-01T10:00:00"
                    },
                    "session_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "expires_at": "2025-12-01T10:30:00"
                }
            ]
        }
    }


class SignInResponseDto(BaseModel):
    status: int
    data: dict  # Contains result with TokenResponseDto and message
