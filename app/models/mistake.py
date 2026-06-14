"""Mistake ORM model."""

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, new_uuid


class Mistake(Base, TimestampMixin):
    __tablename__ = "mistakes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    expression_id: Mapped[str] = mapped_column(String(36), ForeignKey("expressions.id"), nullable=False)
    error_type: Mapped[str] = mapped_column(String(30), nullable=False)
    user_incorrect_answer: Mapped[str | None] = mapped_column(Text, default=None)
    context: Mapped[dict | None] = mapped_column(JSONB, default=None)
    times_repeated: Mapped[int] = mapped_column(Integer, default=1)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="mistakes")
    expression: Mapped["Expression"] = relationship(back_populates="mistakes")
