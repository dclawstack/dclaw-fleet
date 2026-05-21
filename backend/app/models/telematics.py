import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class TelematicsDevice(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "telematics_devices"

    vehicle_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    vendor: Mapped[str] = mapped_column(String(64), nullable=False)  # oem | aftermarket | obd2
    device_id: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
