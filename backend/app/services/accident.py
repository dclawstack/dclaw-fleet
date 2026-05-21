"""Accident management — severity scoring + claim-amount prediction.

Severity-to-cost lookup is a stub; replace with a regression model trained on
historical claims.
"""
from app.models.accident import AccidentReport

SEVERITY_BASE_COST = {
    1: 500,
    2: 1_500,
    3: 3_500,
    4: 7_000,
    5: 12_000,
    6: 20_000,
    7: 35_000,
    8: 60_000,
    9: 100_000,
    10: 250_000,
}


def predict_claim_amount(report: AccidentReport) -> float:
    """Predict total claim from severity + photos (proxy for damage extent)."""
    base = SEVERITY_BASE_COST.get(report.severity_score, 5_000)
    multiplier = 1.0 + min(report.photos_count, 10) * 0.05  # up to +50% for many photos
    return round(base * multiplier, 2)
