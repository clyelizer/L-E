"""Expression, Tag, and ExpressionTag ORM models."""

from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, new_uuid


class Expression(Base, TimestampMixin):
    __tablename__ = "expressions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    text: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    meaning: Mapped[str] = mapped_column(Text, nullable=False)
    metaphor: Mapped[str | None] = mapped_column(Text, default=None)
    part_of_speech: Mapped[str | None] = mapped_column(String(30), default=None)
    difficulty: Mapped[int] = mapped_column(Integer, default=3)
    frequency_score: Mapped[float | None] = mapped_column(Float, default=None)
    example_sentence: Mapped[str | None] = mapped_column(Text, default=None)
    notes: Mapped[str | None] = mapped_column(Text, default=None)
    source: Mapped[str | None] = mapped_column(String(100), default=None)
    tags: Mapped[list] = mapped_column(ARRAY(String), default=list)
    tier: Mapped[int | None] = mapped_column(Integer, default=None)

    __table_args__ = (
        CheckConstraint("difficulty BETWEEN 1 AND 5", name="ck_expression_difficulty"),
        CheckConstraint("tier IS NULL OR tier BETWEEN 1 AND 3", name="ck_expression_tier"),
    )

    # Relationships
    memories: Mapped[list["UserMemory"]] = relationship(back_populates="expression", cascade="all, delete-orphan")
    images: Mapped[list["Image"]] = relationship(back_populates="expression", cascade="all, delete-orphan")
    session_answers: Mapped[list["SessionAnswer"]] = relationship(back_populates="expression")
    mistakes: Mapped[list["Mistake"]] = relationship(back_populates="expression")


class Image(Base, TimestampMixin):
    __tablename__ = "images"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    expression_id: Mapped[str] = mapped_column(String(36), ForeignKey("expressions.id"), nullable=False, index=True)
    path: Mapped[str] = mapped_column(String(500), nullable=False)
    prompt_used: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1)
    width: Mapped[int | None] = mapped_column(Integer, default=None)
    height: Mapped[int | None] = mapped_column(Integer, default=None)
    file_size_bytes: Mapped[int | None] = mapped_column(Integer, default=None)
    hash_sha256: Mapped[str | None] = mapped_column(String(64), default=None)
    is_active: Mapped[bool] = mapped_column(default=True)

    __table_args__ = (
        {"sqlite_autoincrement": True},  # dummy for compat
    )

    # Relationships
    expression: Mapped["Expression"] = relationship(back_populates="images")
