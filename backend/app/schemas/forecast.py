from __future__ import annotations

from pydantic import Field

from app.schemas.common import AgentLensSchema
from app.schemas.enums import PressureLevel, Provider


class ForecastSummary(AgentLensSchema):
    provider: Provider
    current_balance_minor: int = Field(ge=0)
    predicted_net_outflow_minor: int = Field(ge=0)
    pressure_level: PressureLevel
    confidence: float = Field(ge=0.0, le=1.0)
