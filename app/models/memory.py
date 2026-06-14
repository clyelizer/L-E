"""UserMemory — SRS state for each user/expression pair."""

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, new_uuid


class UserMemory(Base, TimestampMixin):
    __tablename__ = "user_memory"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    expression_id: Mapped[str] = mapped_column(String(36), ForeignKey("expressions.id"), nullable=False, index=True)

    # SM-2 state
    mastery_score: Mapped[float] = mapped_column(Float, default=0.0)
    interval: Mapped[int] = mapped_column(Integer, default=0)
    ease_factor: Mapped[float] = mapped_column(Float, default=2.50)
    repetitions: Mapped[int] = mapped_column(Integer, default=0)
    lapses: Mapped[int] = mapped_column(Integer, default=0)

    # Scheduling
    last_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    next_review_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    # Stats
    total_reviews: Mapped[int] = mapped_column(Integer, default=0)
    correct_count: Mapped[int] = mapped_column(Integer, default=0)
    incorrect_count: Mapped[int] = mapped_column(Integer, default=0)
    streak: Mapped[int] = mapped_column(Integer, default=0)
    max_streak: Mapped[int] = mapped_column(Integer, default=0)
    avg_response_time_ms: Mapped[int | None] = mapped_column(Integer, default=None)
    is_learning: Mapped[bool] = mapped_column(Boolean, default=True)

    __table_args__ = (
        UniqueConstraint("user_id", "expression_id", name="uq_user_expression"),
        CheckConstraint("mastery_score BETWEEN 0 AND 1", name="ck_mastery_score_range"),
        CheckConstraint("ease_factor BETWEEN 1.30 AND 3.00", name="ck_ease_factor_range"),
        CheckConstraint("interval >= 0", name="ck_interval_non_negative"),
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="memories")
    expression: Mapped["Expression"] = relationship(back_populates="memories")
