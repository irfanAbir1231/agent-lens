from __future__ import annotations

from datetime import datetime

from pydantic import Field

from app.schemas.common import AgentLensSchema, PaginationMetadata
from app.schemas.enums import DataHealthStatus, Provider, ScenarioId


class ProviderDataHealth(AgentLensSchema):
    provider: Provider
    status: DataHealthStatus
    confidence_multiplier: float = Field(ge=0.0, le=1.0)


class DataQualityWindow(AgentLensSchema):
    start_at: datetime
    end_at: datetime
    recent_window_start_at: datetime
    lookback_minutes: int = Field(ge=1)
    recent_window_minutes: int = Field(ge=1)


class DataQualityComponentScores(AgentLensSchema):
    freshness: float = Field(ge=0.0, le=1.0)
    completeness: float = Field(ge=0.0, le=1.0)
    consistency: float = Field(ge=0.0, le=1.0)
    timeliness: float = Field(ge=0.0, le=1.0)
    validity: float = Field(ge=0.0, le=1.0)


class DataQualityMeasuredEvidence(AgentLensSchema):
    feed_delay_minutes: float | None = Field(default=None, ge=0.0)
    transaction_count: int = Field(ge=0)
    recent_window_transaction_count: int = Field(ge=0)
    max_transaction_gap_minutes: float | None = Field(default=None, ge=0.0)
    feed_reported_balance_minor: int | None = None
    ledger_balance_minor: int | None = None
    duplicate_transaction_ids: list[str]
    duplicate_transaction_record_count: int = Field(ge=0)
    timestamp_order_check_available: bool
    out_of_order_timestamp_count: int | None = Field(default=None, ge=0)
    future_timestamp_count: int = Field(ge=0)
    invalid_monetary_value_count: int = Field(ge=0)


class ProviderDataQualityResult(AgentLensSchema):
    provider: Provider
    status: DataHealthStatus
    confidence_multiplier: float = Field(ge=0.0, le=1.0)
    allow_forecast: bool
    allow_ai_advisory: bool
    component_scores: DataQualityComponentScores
    issue_codes: list[str]
    issue_descriptions: list[str]
    measured_evidence: DataQualityMeasuredEvidence
    data_window: DataQualityWindow
    recommended_verification_steps: list[str]


class AgentDataQualityIssue(AgentLensSchema):
    provider: Provider
    code: str
    description: str


class AgentDataQualityResult(AgentLensSchema):
    agent_id: str
    display_label: str
    area: str
    evaluated_at: datetime
    overall_status: DataHealthStatus
    overall_confidence_multiplier: float = Field(ge=0.0, le=1.0)
    allow_forecast: bool
    allow_ai_advisory: bool
    data_window: DataQualityWindow
    evaluator_version: str
    issues: list[AgentDataQualityIssue]
    recommended_verification_steps: list[str]
    provider_results: list[ProviderDataQualityResult]


class DataQualityResponse(AgentLensSchema):
    generated_at: datetime
    active_scenario_id: ScenarioId
    is_synthetic_data: bool
    status_counts: dict[DataHealthStatus, int]
    results: list[AgentDataQualityResult]
    pagination: PaginationMetadata
