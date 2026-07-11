from __future__ import annotations

from pydantic import Field

from app.schemas.common import AgentLensSchema


class AnomalySummary(AgentLensSchema):
    anomaly_score: float = Field(ge=0.0, le=1.0)
    evidence: list[str]
