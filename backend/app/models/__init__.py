from app.models.ai_chat import AIChatMessage, AIChatSession
from app.models.asset import Asset
from app.models.base import Base
from app.models.driver import Driver
from app.models.fuel import FuelLog
from app.models.geofence import Geofence
from app.models.location import LocationPing
from app.models.maintenance import MaintenanceTask
from app.models.route import Route, RouteStop
from app.models.vehicle import Vehicle

__all__ = [
    "Base",
    "AIChatMessage",
    "AIChatSession",
    "Asset",
    "Driver",
    "FuelLog",
    "Geofence",
    "LocationPing",
    "MaintenanceTask",
    "Route",
    "RouteStop",
    "Vehicle",
]
