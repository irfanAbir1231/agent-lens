from __future__ import annotations

from app.schemas.enums import PressureLevel


def pressure_level(
    *, estimated_minutes: int | None, evidence_sufficient: bool, blocked: bool
) -> PressureLevel:
    if blocked or not evidence_sufficient:
        return PressureLevel.UNKNOWN
    if estimated_minutes is None or estimated_minutes > 360:
        return PressureLevel.NORMAL
    if estimated_minutes <= 60:
        return PressureLevel.CRITICAL
    if estimated_minutes <= 180:
        return PressureLevel.HIGH
    return PressureLevel.WATCH


def shortage_risk_estimate(
    *, estimated_minutes: int | None, confidence: float, pressure: PressureLevel
) -> float | None:
    if pressure == PressureLevel.UNKNOWN:
        return None
    if estimated_minutes == 0:
        return 1.0
    if estimated_minutes is not None and estimated_minutes <= 60:
        return round(max(0.0, min(confidence * (1 - estimated_minutes / 120), 1.0)), 3)
    return 0.0
