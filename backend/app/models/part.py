from sqlalchemy import Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Part(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "parts"

    name: Mapped[str] = mapped_column(String(128), nullable=False)
    sku: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    category: Mapped[str] = mapped_column(String(32), nullable=False)  # tire | brake | filter | fluid | other
    vendor: Mapped[str | None] = mapped_column(String(128), nullable=True)
    stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reorder_threshold: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    unit_cost: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
