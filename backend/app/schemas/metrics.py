from __future__ import annotations

from datetime import datetime

from pydantic import Field

from app.schemas.common import AgentLensSchema
from app.schemas.enums import ScenarioId
from app.schemas.provider import ProviderFeedSummary, ProviderTotalSummary


class OverviewResponse(AgentLensSchema):
    generated_at: datetime
    active_scenario_id: ScenarioId
    agent_count: int = Field(ge=0)
    total_shared_cash_minor: int = Field(ge=0)
    provider_totals: list[ProviderTotalSummary]
    feed_summary: list[ProviderFeedSummary]
    is_synthetic_data: bool = True
