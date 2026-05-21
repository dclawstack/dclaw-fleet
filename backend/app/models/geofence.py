from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Geofence(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "geofences"

    name: Mapped[str] = mapped_column(String(128), nullable=False)
    fence_type: Mapped[str] = mapped_column(String(32), default="inclusion", nullable=False)
    center_lat: Mapped[float] = mapped_column(Float, nullable=False)
    center_lng: Mapped[float] = mapped_column(Float, nullable=False)
    radius_m: Mapped[float] = mapped_column(Float, nullable=False)
