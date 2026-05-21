from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.expense import Expense
from app.repositories.base_repo import BaseRepository


class ExpenseRepository(BaseRepository[Expense]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Expense)

    async def pending(self) -> list[Expense]:
        result = await self.db.execute(
            select(Expense)
            .where(Expense.approval_status == "pending")
            .order_by(desc(Expense.expense_date))
        )
        return list(result.scalars().all())

    async def all_expenses(self) -> list[Expense]:
        result = await self.db.execute(
            select(Expense).order_by(desc(Expense.expense_date))
        )
        return list(result.scalars().all())
