import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.expense import Expense
from app.repositories.expense_repo import ExpenseRepository
from app.schemas.expense import (
    ExpenseAnalytics,
    ExpenseApproval,
    ExpenseCreate,
    ExpenseRead,
    ExpenseUpdate,
)
from app.services.expense import analytics, auto_categorize

router = APIRouter()


@router.get("", response_model=list[ExpenseRead])
async def list_expenses(db: AsyncSession = Depends(get_db)):
    repo = ExpenseRepository(db)
    items, _ = await repo.list_all(limit=500)
    return [ExpenseRead.model_validate(e) for e in items]


@router.post("", response_model=ExpenseRead, status_code=status.HTTP_201_CREATED)
async def create_expense(payload: ExpenseCreate, db: AsyncSession = Depends(get_db)):
    repo = ExpenseRepository(db)
    data = payload.model_dump()
    data["category"] = auto_categorize(data.get("vendor"), data["category"])
    expense = Expense(**data)
    created = await repo.create(expense)
    return ExpenseRead.model_validate(created)


@router.get("/pending", response_model=list[ExpenseRead])
async def pending(db: AsyncSession = Depends(get_db)):
    repo = ExpenseRepository(db)
    items = await repo.pending()
    return [ExpenseRead.model_validate(e) for e in items]


@router.get("/analytics", response_model=ExpenseAnalytics)
async def expense_analytics(db: AsyncSession = Depends(get_db)):
    return await analytics(db)


@router.patch("/{expense_id}", response_model=ExpenseRead)
async def update_expense(
    expense_id: uuid.UUID,
    payload: ExpenseUpdate,
    db: AsyncSession = Depends(get_db),
):
    repo = ExpenseRepository(db)
    expense = await repo.get_by_id(expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    updated = await repo.update(expense, payload.model_dump(exclude_unset=True))
    return ExpenseRead.model_validate(updated)


@router.post("/{expense_id}/approve", response_model=ExpenseRead)
async def approve_expense(
    expense_id: uuid.UUID,
    payload: ExpenseApproval,
    db: AsyncSession = Depends(get_db),
):
    repo = ExpenseRepository(db)
    expense = await repo.get_by_id(expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    updated = await repo.update(
        expense,
        {
            "approval_status": "approved" if payload.approve else "rejected",
            "approved_by": payload.approved_by,
        },
    )
    return ExpenseRead.model_validate(updated)


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(expense_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = ExpenseRepository(db)
    expense = await repo.get_by_id(expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    await repo.delete(expense)
