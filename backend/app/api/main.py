from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health
from app.api.v1 import (
    ai_chat,
    assets,
    drivers,
    driving_events,
    dvir,
    expenses,
    fuel,
    geofences,
    hos,
    locations,
    maintenance,
    permits,
    route_integration,
    routes_api,
    vehicles,
)
from app.core.config import settings
from app.core.database import init_db


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

app.include_router(health.router, prefix="/health", tags=["health"])

API_V1 = "/api/v1"
app.include_router(vehicles.router, prefix=f"{API_V1}/vehicles", tags=["vehicles"])
app.include_router(drivers.router, prefix=f"{API_V1}/drivers", tags=["drivers"])
app.include_router(assets.router, prefix=f"{API_V1}/assets", tags=["assets"])
app.include_router(geofences.router, prefix=f"{API_V1}/geofences", tags=["geofences"])
app.include_router(locations.router, prefix=f"{API_V1}/locations", tags=["tracking"])
app.include_router(maintenance.router, prefix=f"{API_V1}/maintenance", tags=["maintenance"])
app.include_router(fuel.router, prefix=f"{API_V1}/fuel-logs", tags=["fuel"])
app.include_router(routes_api.router, prefix=f"{API_V1}/routes", tags=["routes"])
app.include_router(ai_chat.router, prefix=f"{API_V1}/ai", tags=["ai"])

# P1 features (v1.2)
app.include_router(driving_events.router, prefix=f"{API_V1}/driving-events", tags=["driver-behavior"])
app.include_router(hos.router, prefix=f"{API_V1}/hos-logs", tags=["compliance"])
app.include_router(dvir.router, prefix=f"{API_V1}/dvir", tags=["compliance"])
app.include_router(permits.router, prefix=f"{API_V1}/permits", tags=["compliance"])
app.include_router(expenses.router, prefix=f"{API_V1}/expenses", tags=["expenses"])
app.include_router(route_integration.router, prefix=f"{API_V1}/route-integration", tags=["integrations"])
