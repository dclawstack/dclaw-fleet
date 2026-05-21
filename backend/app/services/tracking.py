import math
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.geofence import Geofence
from app.models.location import LocationPing
from app.repositories.geofence_repo import GeofenceRepository
from app.repositories.location_repo import LocationRepository
from app.schemas.location import GeofenceBreachAlert

EARTH_RADIUS_M = 6_371_000.0


def haversine_m(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Great-circle distance between two lat/lng points, in meters."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lng2 - lng1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(a))


def evaluate_geofences(
    ping_lat: float,
    ping_lng: float,
    vehicle_id: uuid.UUID,
    fences: list[Geofence],
) -> list[GeofenceBreachAlert]:
    """Return breach alerts for a ping against all fences.

    inclusion fence => alert when vehicle is OUTSIDE the radius
    exclusion fence => alert when vehicle is INSIDE the radius
    """
    alerts: list[GeofenceBreachAlert] = []
    for f in fences:
        d = haversine_m(ping_lat, ping_lng, f.center_lat, f.center_lng)
        if f.fence_type == "inclusion" and d > f.radius_m:
            alerts.append(
                GeofenceBreachAlert(
                    vehicle_id=vehicle_id,
                    geofence_id=f.id,
                    geofence_name=f.name,
                    fence_type=f.fence_type,
                    breach_type="exit",
                    distance_m=d,
                )
            )
        elif f.fence_type == "exclusion" and d <= f.radius_m:
            alerts.append(
                GeofenceBreachAlert(
                    vehicle_id=vehicle_id,
                    geofence_id=f.id,
                    geofence_name=f.name,
                    fence_type=f.fence_type,
                    breach_type="entry",
                    distance_m=d,
                )
            )
    return alerts


async def record_ping(
    db: AsyncSession,
    vehicle_id: uuid.UUID,
    lat: float,
    lng: float,
    speed_mph: float = 0.0,
    heading_deg: float = 0.0,
) -> tuple[LocationPing, list[GeofenceBreachAlert]]:
    loc_repo = LocationRepository(db)
    fence_repo = GeofenceRepository(db)
    fences, _ = await fence_repo.list_all(limit=1000)
    ping = LocationPing(
        vehicle_id=vehicle_id,
        lat=lat,
        lng=lng,
        speed_mph=speed_mph,
        heading_deg=heading_deg,
    )
    ping = await loc_repo.create(ping)
    alerts = evaluate_geofences(lat, lng, vehicle_id, fences)
    return ping, alerts
