from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class UserSignUpDto(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)
    username: str = Field(..., min_length=1, max_length=100)


class UserSignInDto(BaseModel):
    email: EmailStr
    password: str


class UserResponseDto(BaseModel):
    id: int
    email: str
    username: str
    created_at: str

    class Config:
        from_attributes = True


class TokenResponseDto(BaseModel):
    user: UserResponseDto
    session_token: str
    expires_at: str


class SignInResponseDto(BaseModel):
    status: int
    data: dict  # Contains result with TokenResponseDto and message
