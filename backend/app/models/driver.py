from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.vehicle import Vehicle


class Driver(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "drivers"

    name: Mapped[str] = mapped_column(String(128), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    license_number: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    license_expiry: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)
    safety_score: Mapped[int] = mapped_column(Integer, default=100, nullable=False)

    vehicles: Mapped[list["Vehicle"]] = relationship(
        "Vehicle",
        back_populates="driver",
        lazy="selectin",
    )
