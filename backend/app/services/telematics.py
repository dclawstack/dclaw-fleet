"""Telematics ingestion + anomaly detection.

Treats incoming vendor payloads as opaque; detects basic anomalies (missing
payload, unexpected fields, stale heartbeat).
"""
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.telematics_repo import TelematicsRepository
from app.schemas.telematics import TelematicsHeartbeat, TelematicsHeartbeatResult

EXPECTED_FIELDS = {"speed", "rpm", "engine_temp", "fuel_level"}


async def ingest_heartbeat(
    db: AsyncSession, payload: TelematicsHeartbeat
) -> TelematicsHeartbeatResult:
    repo = TelematicsRepository(db)
    device = await repo.by_device_id(payload.device_id)
    if device is None:
        raise ValueError(f"Unknown device_id {payload.device_id}")

    ts = payload.timestamp or datetime.now(timezone.utc)
    await repo.update(device, {"last_seen_at": ts})

    anomalies: list[str] = []
    if not payload.payload:
        anomalies.append("Empty payload")
    else:
        missing = EXPECTED_FIELDS - payload.payload.keys()
        if missing:
            anomalies.append(f"Missing expected fields: {sorted(missing)}")
        speed = payload.payload.get("speed")
        if isinstance(speed, (int, float)) and speed > 120:
            anomalies.append(f"Implausible speed {speed} mph")
        engine_temp = payload.payload.get("engine_temp")
        if isinstance(engine_temp, (int, float)) and engine_temp > 240:
            anomalies.append(f"Engine temp {engine_temp}°F above safe threshold")

    return TelematicsHeartbeatResult(
        device_id=device.device_id,
        vehicle_id=device.vehicle_id,
        anomalies=anomalies,
    )
