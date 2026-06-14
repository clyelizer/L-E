"""StudySession and SessionAnswer ORM models."""

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, new_uuid


class StudySession(Base, TimestampMixin):
    __tablename__ = "study_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    session_type: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="in_progress")
    score: Mapped[float | None] = mapped_column(Float, default=None)
    total_questions: Mapped[int] = mapped_column(Integer, default=0)
    correct_answers: Mapped[int] = mapped_column(Integer, default=0)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, default=None)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

    __table_args__ = (
        CheckConstraint("session_type IN ('learn', 'review', 'mixed')", name="ck_session_type"),
        CheckConstraint("status IN ('in_progress', 'completed', 'abandoned')", name="ck_session_status"),
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="sessions")
    answers: Mapped[list["SessionAnswer"]] = relationship(back_populates="session", cascade="all, delete-orphan")


class SessionAnswer(Base, TimestampMixin):
    __tablename__ = "session_answers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("study_sessions.id"), nullable=False, index=True)
    expression_id: Mapped[str] = mapped_column(String(36), ForeignKey("expressions.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    question_type: Mapped[str] = mapped_column(String(30), nullable=False)
    question_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    user_answer: Mapped[str | None] = mapped_column(Text, default=None)
    correct_answer: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    response_time_ms: Mapped[int | None] = mapped_column(Integer, default=None)
    hint_used: Mapped[bool] = mapped_column(Boolean, default=False)
    confidence: Mapped[str | None] = mapped_column(String(10), default=None)

    # Relationships
    session: Mapped["StudySession"] = relationship(back_populates="answers")
    expression: Mapped["Expression"] = relationship(back_populates="session_answers")
