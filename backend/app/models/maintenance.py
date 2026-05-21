import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class MaintenanceTask(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "maintenance_tasks"

    vehicle_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    task_type: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str | None] = mapped_column(String(512), nullable=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    due_mileage: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="scheduled", nullable=False)
    completed_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    cost: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
