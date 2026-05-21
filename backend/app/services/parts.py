"""Parts inventory — reorder recommendations."""
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.part_repo import PartRepository
from app.schemas.part import ReorderRecommendation


async def reorder_recommendations(db: AsyncSession) -> list[ReorderRecommendation]:
    repo = PartRepository(db)
    low = await repo.low_stock()
    recs: list[ReorderRecommendation] = []
    for p in low:
        # Order back to 2x threshold for headroom
        target = max(p.reorder_threshold * 2, 1)
        qty = max(target - p.stock, 1)
        recs.append(
            ReorderRecommendation(
                part_id=p.id,
                sku=p.sku,
                name=p.name,
                current_stock=p.stock,
                reorder_threshold=p.reorder_threshold,
                suggested_order_qty=qty,
                estimated_cost=round(float(p.unit_cost) * qty, 2),
            )
        )
    return recs
