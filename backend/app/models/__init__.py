from app.models.accident import AccidentReport
from app.models.ai_chat import AIChatMessage, AIChatSession
from app.models.asset import Asset
from app.models.base import Base
from app.models.charging import ChargingSession
from app.models.dashcam import DashcamEvent
from app.models.driver import Driver
from app.models.driving_event import DrivingEvent
from app.models.dvir import DVIRReport
from app.models.expense import Expense
from app.models.fuel import FuelLog
from app.models.geofence import Geofence
from app.models.hos import HOSLog
from app.models.location import LocationPing
from app.models.maintenance import MaintenanceTask
from app.models.part import Part
from app.models.permit import Permit
from app.models.route import Route, RouteStop
from app.models.telematics import TelematicsDevice
from app.models.vehicle import Vehicle

__all__ = [
    "Base",
    "AccidentReport",
    "AIChatMessage",
    "AIChatSession",
    "Asset",
    "ChargingSession",
    "DashcamEvent",
    "Driver",
    "DrivingEvent",
    "DVIRReport",
    "Expense",
    "FuelLog",
    "Geofence",
    "HOSLog",
    "LocationPing",
    "MaintenanceTask",
    "Part",
    "Permit",
    "Route",
    "RouteStop",
    "TelematicsDevice",
    "Vehicle",
]
