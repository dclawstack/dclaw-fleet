import math

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.route import Route
from app.repositories.route_repo import RouteRepository
from app.services.tracking import haversine_m

AVG_SPEED_MPH = 30.0


def _miles(meters: float) -> float:
    return meters / 1609.344


async def optimize_route(db: AsyncSession, route: Route) -> Route:
    """Greedy nearest-neighbor stop ordering, starting from the first stop.

    Computes total distance + duration estimates and persists them on the route.
    """
    if not route.stops or len(route.stops) <= 1:
        route.optimized_distance_miles = 0.0
        route.optimized_duration_min = 0
        repo = RouteRepository(db)
        return await repo.update(route, {})

    remaining = list(route.stops)
    ordered = [remaining.pop(0)]
    while remaining:
        last = ordered[-1]
        nearest = min(
            remaining,
            key=lambda s: haversine_m(last.lat, last.lng, s.lat, s.lng),
        )
        remaining.remove(nearest)
        ordered.append(nearest)

    total_m = 0.0
    for a, b in zip(ordered, ordered[1:]):
        total_m += haversine_m(a.lat, a.lng, b.lat, b.lng)

    for idx, stop in enumerate(ordered):
        stop.sequence = idx

    miles = _miles(total_m)
    route.optimized_distance_miles = round(miles, 2)
    route.optimized_duration_min = int(math.ceil(miles / AVG_SPEED_MPH * 60))
    route.status = "optimized"

    await db.commit()
    await db.refresh(route)
    return route
