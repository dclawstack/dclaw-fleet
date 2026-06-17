from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health
from app.api.v1 import (
    accidents,
    ai_chat,
    assets,
    auth,
    charging,
    dashcam,
    demo,
    drivers,
    driving_events,
    dvir,
    expenses,
    fuel,
    geofences,
    hos,
    locations,
    maintenance,
    parts,
    permits,
    predictive,
    route_integration,
    routes_api,
    telematics,
    vehicles,
)
from app.core.cache import register_cache
from app.core.config import settings
from app.core.database import init_db
from app.core.errors import register_exception_handlers
from app.core.security import get_current_user


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_cache(app)
register_exception_handlers(app)

app.include_router(health.router, prefix="/health", tags=["health"])

API_V1 = "/api/v1"

# Auth routes — public except /me and /register (those declare their own deps)
app.include_router(auth.router, prefix=f"{API_V1}/auth", tags=["auth"])

# Demo routes — public, gated by ENABLE_DEMO_MODE inside the router
app.include_router(demo.router, prefix=f"{API_V1}/demo", tags=["demo"])

# All other /api/v1/* require a valid JWT.
PROTECTED = [Depends(get_current_user)]

app.include_router(vehicles.router, prefix=f"{API_V1}/vehicles", tags=["vehicles"], dependencies=PROTECTED)
app.include_router(drivers.router, prefix=f"{API_V1}/drivers", tags=["drivers"], dependencies=PROTECTED)
app.include_router(assets.router, prefix=f"{API_V1}/assets", tags=["assets"], dependencies=PROTECTED)
app.include_router(geofences.router, prefix=f"{API_V1}/geofences", tags=["geofences"], dependencies=PROTECTED)
app.include_router(locations.router, prefix=f"{API_V1}/locations", tags=["tracking"], dependencies=PROTECTED)
app.include_router(maintenance.router, prefix=f"{API_V1}/maintenance", tags=["maintenance"], dependencies=PROTECTED)
app.include_router(fuel.router, prefix=f"{API_V1}/fuel-logs", tags=["fuel"], dependencies=PROTECTED)
app.include_router(routes_api.router, prefix=f"{API_V1}/routes", tags=["routes"], dependencies=PROTECTED)
app.include_router(ai_chat.router, prefix=f"{API_V1}/ai", tags=["ai"], dependencies=PROTECTED)

# P1 features (v1.2)
app.include_router(driving_events.router, prefix=f"{API_V1}/driving-events", tags=["driver-behavior"], dependencies=PROTECTED)
app.include_router(hos.router, prefix=f"{API_V1}/hos-logs", tags=["compliance"], dependencies=PROTECTED)
app.include_router(dvir.router, prefix=f"{API_V1}/dvir", tags=["compliance"], dependencies=PROTECTED)
app.include_router(permits.router, prefix=f"{API_V1}/permits", tags=["compliance"], dependencies=PROTECTED)
app.include_router(expenses.router, prefix=f"{API_V1}/expenses", tags=["expenses"], dependencies=PROTECTED)
app.include_router(route_integration.router, prefix=f"{API_V1}/route-integration", tags=["integrations"], dependencies=PROTECTED)

# P2 features (v1.3+)
app.include_router(charging.router, prefix=f"{API_V1}/charging", tags=["ev"], dependencies=PROTECTED)
app.include_router(accidents.router, prefix=f"{API_V1}/accidents", tags=["accidents"], dependencies=PROTECTED)
app.include_router(parts.router, prefix=f"{API_V1}/parts", tags=["inventory"], dependencies=PROTECTED)
app.include_router(telematics.router, prefix=f"{API_V1}/telematics", tags=["telematics"], dependencies=PROTECTED)
app.include_router(dashcam.router, prefix=f"{API_V1}/dashcam", tags=["dashcam"], dependencies=PROTECTED)
app.include_router(predictive.router, prefix=f"{API_V1}/predictive", tags=["predictive"], dependencies=PROTECTED)
