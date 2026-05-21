import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class ExpenseBase(BaseModel):
    vehicle_id: uuid.UUID | None = None
    driver_id: uuid.UUID | None = None
    category: str
    amount: float
    vendor: str | None = None
    expense_date: date
    notes: str | None = None


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    category: str | None = None
    amount: float | None = None
    vendor: str | None = None
    expense_date: date | None = None
    notes: str | None = None


class ExpenseApproval(BaseModel):
    approved_by: str
    approve: bool


class ExpenseRead(ExpenseBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    approval_status: str
    approved_by: str | None
    created_at: datetime
    updated_at: datetime


class ExpenseAnalytics(BaseModel):
    total_amount: float
    by_category: dict[str, float]
    pending_approval_count: int
    pending_approval_amount: float
    flagged_count: int
    flags: list[str]
