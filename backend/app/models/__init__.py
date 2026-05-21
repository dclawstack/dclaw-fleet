from app.models.ai_chat import AIChatMessage, AIChatSession
from app.models.asset import Asset
from app.models.base import Base
from app.models.driver import Driver
from app.models.driving_event import DrivingEvent
from app.models.dvir import DVIRReport
from app.models.expense import Expense
from app.models.fuel import FuelLog
from app.models.geofence import Geofence
from app.models.hos import HOSLog
from app.models.location import LocationPing
from app.models.maintenance import MaintenanceTask
from app.models.permit import Permit
from app.models.route import Route, RouteStop
from app.models.vehicle import Vehicle

__all__ = [
    "Base",
    "AIChatMessage",
    "AIChatSession",
    "Asset",
    "Driver",
    "DrivingEvent",
    "DVIRReport",
    "Expense",
    "FuelLog",
    "Geofence",
    "HOSLog",
    "LocationPing",
    "MaintenanceTask",
    "Permit",
    "Route",
    "RouteStop",
    "Vehicle",
]
