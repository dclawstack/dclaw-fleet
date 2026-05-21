"""Expense categorization + fraud detection."""
from collections import defaultdict
from datetime import date, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.expense import Expense
from app.repositories.expense_repo import ExpenseRepository
from app.schemas.expense import ExpenseAnalytics

VENDOR_RULES: dict[str, str] = {
    "shell": "fuel",
    "chevron": "fuel",
    "bp": "fuel",
    "exxon": "fuel",
    "ezpass": "toll",
    "fastrak": "toll",
    "geico": "insurance",
    "progressive": "insurance",
    "marriott": "lodging",
    "holiday inn": "lodging",
}

DUPLICATE_WINDOW_DAYS = 1
OVERSIZED_AMOUNT = 2_500.0


def auto_categorize(vendor: str | None, fallback: str) -> str:
    if not vendor:
        return fallback
    v = vendor.lower()
    for keyword, cat in VENDOR_RULES.items():
        if keyword in v:
            return cat
    return fallback


def detect_flags(expenses: list[Expense]) -> list[str]:
    flags: list[str] = []
    by_vendor_amount: dict[tuple[str, float, date], int] = defaultdict(int)
    for e in expenses:
        key = ((e.vendor or "").lower(), float(e.amount), e.expense_date)
        by_vendor_amount[key] += 1
        if float(e.amount) > OVERSIZED_AMOUNT:
            flags.append(
                f"Oversized expense ${float(e.amount):,.0f} from {e.vendor or 'unknown'} on {e.expense_date}"
            )
    for (vendor, amount, day), count in by_vendor_amount.items():
        if count >= 2 and vendor:
            flags.append(
                f"Possible duplicate: {count}× ${amount:,.2f} from {vendor} on {day}"
            )
    # Near-duplicates across consecutive days
    sorted_exp = sorted(expenses, key=lambda e: (e.vendor or "", e.expense_date))
    for a, b in zip(sorted_exp, sorted_exp[1:]):
        if (
            (a.vendor or "").lower() == (b.vendor or "").lower()
            and float(a.amount) == float(b.amount)
            and abs((b.expense_date - a.expense_date).days) <= DUPLICATE_WINDOW_DAYS
            and a.id != b.id
            and a.expense_date != b.expense_date
        ):
            flags.append(
                f"Same amount ${float(a.amount):,.2f} from {a.vendor} on consecutive days"
            )
    return flags


async def analytics(db: AsyncSession) -> ExpenseAnalytics:
    repo = ExpenseRepository(db)
    expenses = await repo.all_expenses()
    pending = [e for e in expenses if e.approval_status == "pending"]
    by_category: dict[str, float] = defaultdict(float)
    for e in expenses:
        by_category[e.category] += float(e.amount)
    flags = detect_flags(expenses)
    return ExpenseAnalytics(
        total_amount=sum(float(e.amount) for e in expenses),
        by_category=dict(by_category),
        pending_approval_count=len(pending),
        pending_approval_amount=sum(float(e.amount) for e in pending),
        flagged_count=len(flags),
        flags=flags,
    )
