import uuid
from datetime import date

from sqlalchemy import Date, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Permit(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Polymorphic permit — attached to either a vehicle or a driver."""
    __tablename__ = "permits"

    entity_type: Mapped[str] = mapped_column(String(16), nullable=False)  # 'vehicle' | 'driver'
    entity_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False, index=True)
    permit_type: Mapped[str] = mapped_column(String(64), nullable=False)
    issuer: Mapped[str | None] = mapped_column(String(128), nullable=True)
    permit_number: Mapped[str] = mapped_column(String(128), nullable=False)
    issued_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)
