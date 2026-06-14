"""Auth & User Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


# ─── Auth ───

class RegisterRequest(BaseModel):
    email: str = Field(..., max_length=255)
    username: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=6, max_length=128)


class LoginRequest(BaseModel):
    email: str = Field(..., max_length=255)
    password: str = Field(..., max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


# ─── User ───

class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserSettingsResponse(BaseModel):
    daily_new_words: int
    daily_review_cap: int
    question_types: list[str]
    difficulty_bias: str
    ai_generation_enabled: bool
    native_language: str
    mini_test_enabled: bool
    timezone: str

    model_config = {"from_attributes": True}


class UserSettingsUpdate(BaseModel):
    daily_new_words: int | None = Field(None, ge=1, le=100)
    daily_review_cap: int | None = Field(None, ge=1, le=200)
    question_types: list[str] | None = None
    difficulty_bias: str | None = None
    ai_generation_enabled: bool | None = None
    native_language: str | None = None
    mini_test_enabled: bool | None = None
    timezone: str | None = None
