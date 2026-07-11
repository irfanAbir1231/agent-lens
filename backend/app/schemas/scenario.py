from __future__ import annotations

from datetime import datetime

from app.schemas.common import AgentLensSchema
from app.schemas.enums import ScenarioId


class ScenarioSummary(AgentLensSchema):
    id: ScenarioId
    name: str
    description: str
    is_active: bool
    generated_at: datetime


class ScenarioListResponse(AgentLensSchema):
    scenarios: list[ScenarioSummary]

