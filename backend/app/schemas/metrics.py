from __future__ import annotations

from datetime import datetime
from typing import Literal

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


class MetricMetadata(AgentLensSchema):
    availability: Literal["AVAILABLE", "UNAVAILABLE"]
    sample_count: int = Field(ge=0)
    measured_at: datetime | None
    version: str | None


class ForecastMetricGroup(MetricMetadata):
    mae_net_outflow_minor: float | None
    rmse_net_outflow_minor: float | None
    smape_percent: float | None
    shortage_detection_lead_time_minutes: float | None
    shortage_lead_time_sample_count: int | None


class AnomalyMetricGroup(MetricMetadata):
    precision: float | None
    recall: float | None
    f1: float | None
    false_positive_rate: float | None
    contextual_false_positive_rate: float | None
    evidence_coverage: float | None


class AIMetricGroup(MetricMetadata):
    completed_count: int | None
    failed_count: int | None
    blocked_count: int | None
    fallback_count: int | None
    average_latency_ms: float | None
    validation_pass_count: int | None
    validation_failure_count: int | None
    source_coverage_rate: float | None
    one_call_evidence_available: bool
    one_call_compliance_rate: float | None


class WorkflowMetricGroup(MetricMetadata):
    case_counts: dict[str, int] | None
    decision_count: int | None
    average_acknowledgement_seconds: float | None
    average_resolution_seconds: float | None
    resolution_rate: float | None
    dismissal_rate: float | None


class MetricsResponse(AgentLensSchema):
    generated_at: datetime
    forecast: ForecastMetricGroup
    anomaly: AnomalyMetricGroup
    ai: AIMetricGroup
    workflow: WorkflowMetricGroup
