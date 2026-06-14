"""User and UserSettings ORM models."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, new_uuid


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    settings: Mapped["UserSettings"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    memories: Mapped[list["UserMemory"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    sessions: Mapped[list["StudySession"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    mistakes: Mapped[list["Mistake"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class UserSettings(Base, TimestampMixin):
    __tablename__ = "user_settings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    daily_new_words: Mapped[int] = mapped_column(Integer, default=5)
    daily_review_cap: Mapped[int] = mapped_column(Integer, default=50)
    question_types: Mapped[list] = mapped_column(ARRAY(String), default=["MCQ", "FILL_BLANK", "FR_TO_EN"])
    difficulty_bias: Mapped[str] = mapped_column(String(20), default="adaptive")
    ai_generation_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    native_language: Mapped[str] = mapped_column(String(10), default="fr")
    mini_test_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    timezone: Mapped[str] = mapped_column(String(50), default="UTC")

    __table_args__ = (
        CheckConstraint("daily_new_words > 0", name="ck_daily_new_words_positive"),
        CheckConstraint("daily_review_cap > 0", name="ck_daily_review_cap_positive"),
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="settings")
