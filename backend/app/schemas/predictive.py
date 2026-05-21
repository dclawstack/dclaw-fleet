import uuid

from pydantic import BaseModel


class PartFailurePrediction(BaseModel):
    vehicle_id: uuid.UUID
    component: str
    probability: float  # 0-1
    suggested_action: str
    reason: str


class PredictiveReport(BaseModel):
    vehicle_id: uuid.UUID
    overall_risk: str  # low | medium | high
    predictions: list[PartFailurePrediction]


class CarbonReport(BaseModel):
    vehicle_id: uuid.UUID | None  # None = fleet-wide
    co2_kg: float
    fuel_gallons: float
    miles: int
    co2_per_mile_g: float
    suggestions: list[str]


class AutonomousDispatchResult(BaseModel):
    assignments: list[dict]
    rejected: list[dict]
    score: float
