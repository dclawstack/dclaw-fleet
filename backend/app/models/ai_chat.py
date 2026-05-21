import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AIChatSession(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "ai_chat_sessions"

    title: Mapped[str] = mapped_column(String(255), default="Fleet Copilot", nullable=False)

    messages: Mapped[list["AIChatMessage"]] = relationship(
        "AIChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="AIChatMessage.created_at",
    )


class AIChatMessage(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "ai_chat_messages"

    session_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("ai_chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(String(16), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utcnow,
        nullable=False,
    )

    session: Mapped["AIChatSession"] = relationship("AIChatSession", back_populates="messages")
