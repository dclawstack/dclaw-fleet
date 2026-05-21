import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PartBase(BaseModel):
    name: str
    sku: str
    category: str
    vendor: str | None = None
    stock: int = 0
    reorder_threshold: int = 5
    unit_cost: float = 0.0


class PartCreate(PartBase):
    pass


class PartUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    vendor: str | None = None
    stock: int | None = None
    reorder_threshold: int | None = None
    unit_cost: float | None = None


class PartRead(PartBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ReorderRecommendation(BaseModel):
    part_id: uuid.UUID
    sku: str
    name: str
    current_stock: int
    reorder_threshold: int
    suggested_order_qty: int
    estimated_cost: float
