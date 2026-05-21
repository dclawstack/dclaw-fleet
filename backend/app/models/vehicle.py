import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.driver import Driver


class Vehicle(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "vehicles"

    vin: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    license_plate: Mapped[str] = mapped_column(String(32), nullable=False)
    make: Mapped[str] = mapped_column(String(64), nullable=False)
    model: Mapped[str] = mapped_column(String(64), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)
    fuel_type: Mapped[str] = mapped_column(String(32), default="gasoline", nullable=False)
    odometer_miles: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    engine_hours: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    driver_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("drivers.id", ondelete="SET NULL"),
        nullable=True,
    )
    driver: Mapped["Driver | None"] = relationship(
        "Driver",
        back_populates="vehicles",
        lazy="selectin",
    )
