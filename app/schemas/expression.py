"""Expression, Image, Tag Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class ExpressionResponse(BaseModel):
    id: str
    text: str
    meaning: str
    metaphor: str | None = None
    part_of_speech: str | None = None
    difficulty: int
    frequency_score: float | None = None
    example_sentence: str | None = None
    notes: str | None = None
    source: str | None = None
    tags: list[str]
    tier: int | None = None
    created_at: datetime
    updated_at: datetime
    image_path: str | None = None

    model_config = {"from_attributes": True}


class ExpressionListResponse(BaseModel):
    items: list[ExpressionResponse]
    total: int
    page: int
    page_size: int


class ExpressionCreate(BaseModel):
    text: str = Field(..., max_length=500)
    meaning: str = Field(..., min_length=1)
    metaphor: str | None = None
    part_of_speech: str | None = None
    difficulty: int = Field(default=3, ge=1, le=5)
    frequency_score: float | None = Field(default=None, ge=0, le=100)
    example_sentence: str | None = None
    notes: str | None = None
    source: str | None = None
    tags: list[str] = []
    tier: int | None = Field(default=None, ge=1, le=3)


class ExpressionUpdate(BaseModel):
    text: str | None = None
    meaning: str | None = None
    metaphor: str | None = None
    part_of_speech: str | None = None
    difficulty: int | None = Field(default=None, ge=1, le=5)
    frequency_score: float | None = Field(default=None, ge=0, le=100)
    example_sentence: str | None = None
    notes: str | None = None
    source: str | None = None
    tags: list[str] | None = None
    tier: int | None = Field(default=None, ge=1, le=3)


class ImageResponse(BaseModel):
    id: str
    expression_id: str
    path: str
    version: int
    width: int | None = None
    height: int | None = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
