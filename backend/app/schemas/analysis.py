from __future__ import annotations

from datetime import datetime
from typing import Literal

from app.schemas.advisory import AdvisorySummary
from app.schemas.alert import AlertDetail
from app.schemas.common import AgentLensSchema
from app.schemas.enums import Provider, ScenarioId
from app.schemas.forecast import LiquidityForecastResponse, ProviderLiquidityForecast


class ProviderAnalysisResult(AgentLensSchema):
    provider: Provider
    actionable: bool
    eligible_for_ai: bool
    alert: AlertDetail
    forecast: ProviderLiquidityForecast


class AnalysisResponse(AgentLensSchema):
    analysis_id: str
    agent_id: str
    active_scenario_id: ScenarioId
    created_at: datetime
    completed_at: datetime
    reused: bool
    pipeline_version: str
    prompt_version: str
    input_fingerprint: str
    forecasts: LiquidityForecastResponse
    provider_results: list[ProviderAnalysisResult]
    alert_ids: list[str]
    excluded_providers: list[Provider]
    advisory: AdvisorySummary
    requires_human_review: Literal[True] = True
