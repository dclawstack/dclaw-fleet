"""Demo data seed + reset.

Every record carries a DEMO- marker so reset() is provably scoped:
- vehicles: license_plate starts with DEMO-
- drivers:  email ends with @demo.dclaw.io
- demo user: demo@dclaw.io

reset() deletes ONLY rows carrying those markers. Real data is untouchable
even if ENABLE_DEMO_MODE is left on against a populated instance.
"""
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.driver import Driver
from app.models.fuel import FuelLog
from app.models.geofence import Geofence
from app.models.maintenance import MaintenanceTask
from app.models.user import User
from app.models.vehicle import Vehicle
from app.services.auth import hash_password

DEMO_VEHICLE_PREFIX = "DEMO-"
DEMO_DRIVER_DOMAIN = "@demo.dclaw.io"
DEMO_USER_EMAIL = "demo@dclaw.io"
DEMO_USER_PASSWORD = "DemoPass123!"
DEMO_GEOFENCE_NAME = "DEMO-Depot"


VEHICLES = [
    {"plate": "DEMO-101", "vin": "DEMO1HGCM82633A0001", "make": "Ford", "model": "Transit", "year": 2024, "fuel_type": "diesel", "miles": 12_400},
    {"plate": "DEMO-102", "vin": "DEMO1HGCM82633A0002", "make": "Tesla", "model": "Semi", "year": 2025, "fuel_type": "electric", "miles": 4_800},
    {"plate": "DEMO-103", "vin": "DEMO1HGCM82633A0003", "make": "Chevy", "model": "Silverado", "year": 2022, "fuel_type": "gasoline", "miles": 48_900},
    {"plate": "DEMO-104", "vin": "DEMO1HGCM82633A0004", "make": "Freightliner", "model": "Cascadia", "year": 2023, "fuel_type": "diesel", "miles": 87_300},
    {"plate": "DEMO-105", "vin": "DEMO1HGCM82633A0005", "make": "Ford", "model": "F-150", "year": 2024, "fuel_type": "hybrid", "miles": 21_650},
]

DRIVERS = [
    {"name": "Alex Demo", "email": "alex" + DEMO_DRIVER_DOMAIN, "license": "DEMO-DL-1", "score": 88},
    {"name": "Jordan Demo", "email": "jordan" + DEMO_DRIVER_DOMAIN, "license": "DEMO-DL-2", "score": 62},
    {"name": "Sam Demo", "email": "sam" + DEMO_DRIVER_DOMAIN, "license": "DEMO-DL-3", "score": 95},
]


async def status(db: AsyncSession) -> dict:
    """Return current demo state — used by the landing-page probe."""
    veh_q = await db.execute(
        select(func.count()).select_from(Vehicle).where(Vehicle.license_plate.like(f"{DEMO_VEHICLE_PREFIX}%"))
    )
    drv_q = await db.execute(
        select(func.count()).select_from(Driver).where(Driver.email.like(f"%{DEMO_DRIVER_DOMAIN}"))
    )
    user_q = await db.execute(select(User).where(User.email == DEMO_USER_EMAIL))
    return {
        "vehicle_count": veh_q.scalar() or 0,
        "driver_count": drv_q.scalar() or 0,
        "demo_user_exists": user_q.scalar_one_or_none() is not None,
    }


async def seed(db: AsyncSession) -> dict:
    """Idempotent — running twice doesn't double-seed."""
    existing_user = (await db.execute(select(User).where(User.email == DEMO_USER_EMAIL))).scalar_one_or_none()
    if existing_user is None:
        db.add(User(
            email=DEMO_USER_EMAIL,
            name="Demo Dispatcher",
            password_hash=hash_password(DEMO_USER_PASSWORD),
            role="admin",
            is_active=True,
        ))

    # Drivers
    existing_drivers = {
        d.email: d for d in (
            await db.execute(select(Driver).where(Driver.email.like(f"%{DEMO_DRIVER_DOMAIN}")))
        ).scalars().all()
    }
    driver_objs: list[Driver] = []
    for spec in DRIVERS:
        d = existing_drivers.get(spec["email"])
        if d is None:
            d = Driver(
                name=spec["name"],
                email=spec["email"],
                license_number=spec["license"],
                safety_score=spec["score"],
            )
            db.add(d)
        driver_objs.append(d)
    await db.flush()

    # Vehicles
    existing_vehicles = {
        v.license_plate: v for v in (
            await db.execute(select(Vehicle).where(Vehicle.license_plate.like(f"{DEMO_VEHICLE_PREFIX}%")))
        ).scalars().all()
    }
    vehicles_created: list[Vehicle] = []
    for i, spec in enumerate(VEHICLES):
        v = existing_vehicles.get(spec["plate"])
        if v is None:
            v = Vehicle(
                vin=spec["vin"],
                license_plate=spec["plate"],
                make=spec["make"],
                model=spec["model"],
                year=spec["year"],
                fuel_type=spec["fuel_type"],
                odometer_miles=spec["miles"],
                driver_id=driver_objs[i % len(driver_objs)].id if driver_objs else None,
            )
            db.add(v)
        vehicles_created.append(v)
    await db.flush()

    # Geofence (single demo depot)
    existing_fence = (
        await db.execute(select(Geofence).where(Geofence.name == DEMO_GEOFENCE_NAME))
    ).scalar_one_or_none()
    if existing_fence is None:
        db.add(Geofence(
            name=DEMO_GEOFENCE_NAME,
            fence_type="inclusion",
            center_lat=37.7749,
            center_lng=-122.4194,
            radius_m=2000,
        ))

    # Maintenance — one overdue, one upcoming per vehicle
    existing_tasks_q = await db.execute(
        select(MaintenanceTask.vehicle_id).where(
            MaintenanceTask.vehicle_id.in_([v.id for v in vehicles_created])
        )
    )
    vehicles_with_tasks = {row[0] for row in existing_tasks_q.all()}
    for i, v in enumerate(vehicles_created):
        if v.id in vehicles_with_tasks:
            continue
        # one overdue (alternating vehicles)
        if i % 2 == 0:
            db.add(MaintenanceTask(
                vehicle_id=v.id,
                task_type="oil_change",
                description="DEMO overdue oil change",
                due_date=date.today() - timedelta(days=5),
                due_mileage=v.odometer_miles + 200,
                status="scheduled",
            ))
        db.add(MaintenanceTask(
            vehicle_id=v.id,
            task_type="tire_rotation",
            description="DEMO upcoming tire rotation",
            due_date=date.today() + timedelta(days=30),
            due_mileage=v.odometer_miles + 5_000,
            status="scheduled",
        ))

    # Fuel logs for one ICE vehicle so MPG report has data
    ice_vehicle = next((v for v in vehicles_created if v.fuel_type in ("diesel", "gasoline")), None)
    if ice_vehicle:
        fuel_count = (await db.execute(
            select(func.count()).select_from(FuelLog).where(FuelLog.vehicle_id == ice_vehicle.id)
        )).scalar() or 0
        if fuel_count == 0:
            base_time = datetime.now(timezone.utc) - timedelta(days=60)
            for n in range(3):
                db.add(FuelLog(
                    vehicle_id=ice_vehicle.id,
                    driver_id=ice_vehicle.driver_id,
                    gallons=22.0,
                    cost=85.0,
                    odometer_miles=ice_vehicle.odometer_miles - 600 + n * 300,
                    fuel_type=ice_vehicle.fuel_type,
                    filled_at=base_time + timedelta(days=n * 20),
                ))

    await db.commit()
    return await status(db)


async def reset(db: AsyncSession) -> dict:
    """Delete ONLY DEMO-marked records. Real data is untouchable."""
    demo_vehicle_ids_q = await db.execute(
        select(Vehicle.id).where(Vehicle.license_plate.like(f"{DEMO_VEHICLE_PREFIX}%"))
    )
    demo_vehicle_ids = [row[0] for row in demo_vehicle_ids_q.all()]
    if demo_vehicle_ids:
        await db.execute(delete(FuelLog).where(FuelLog.vehicle_id.in_(demo_vehicle_ids)))
        await db.execute(delete(MaintenanceTask).where(MaintenanceTask.vehicle_id.in_(demo_vehicle_ids)))
        await db.execute(delete(Vehicle).where(Vehicle.id.in_(demo_vehicle_ids)))

    await db.execute(delete(Driver).where(Driver.email.like(f"%{DEMO_DRIVER_DOMAIN}")))
    await db.execute(delete(Geofence).where(Geofence.name == DEMO_GEOFENCE_NAME))
    await db.execute(delete(User).where(User.email == DEMO_USER_EMAIL))
    await db.commit()
    return await status(db)
