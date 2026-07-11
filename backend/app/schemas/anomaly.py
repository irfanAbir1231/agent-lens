from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field

from app.schemas.common import AgentLensSchema
from app.schemas.enums import DataHealthStatus, Provider


class AnomalyEvidence(AgentLensSchema):
    code: str
    description: str
    measured_value: float
    baseline_value: float | None = None
    contribution: float = Field(ge=0.0, le=1.0)


class AnomalyContextualBaseline(AgentLensSchema):
    peer_provider_recent_count_median: float
    peer_provider_recent_volume_minor_median: float
    provider_recent_count: int = Field(ge=0)
    provider_recent_volume_minor: int = Field(ge=0)


class AnomalyResult(AgentLensSchema):
    anomaly_score: float = Field(ge=0.0, le=1.0)
    review_level: str
    confidence: float = Field(ge=0.0, le=1.0)
    scope: Literal["PROVIDER"]
    agent_id: str
    provider: Provider
    evaluation_blocked: bool
    data_quality_status: DataHealthStatus
    evidence: list[AnomalyEvidence]
    contextual_baseline: AnomalyContextualBaseline
    legitimate_explanations: list[str]
    limitations: list[str]
    data_window_start: datetime
    data_window_end: datetime
    detector_version: str


class AnomalySummary(AgentLensSchema):
    """Compatibility summary retained for the protected future analysis schema."""

    anomaly_score: float = Field(ge=0.0, le=1.0)
    evidence: list[str]
