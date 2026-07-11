from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.schemas.enums import DataHealthStatus, Provider

DETECTOR_VERSION = "unusual-activity-rules-v1"
LOOKBACK_MINUTES = 180
RECENT_MINUTES = 60


@dataclass(frozen=True)
class PeerBaseline:
    recent_count_median: float
    recent_volume_median: float


@dataclass(frozen=True)
class Evidence:
    code: str
    description: str
    measured_value: float
    baseline_value: float | None
    contribution: float


@dataclass(frozen=True)
class AnomalyEvaluation:
    agent_id: str
    provider: Provider
    score: float
    review_level: str
    confidence: float
    blocked: bool
    data_quality_status: DataHealthStatus
    evidence: tuple[Evidence, ...]
    baseline: PeerBaseline
    recent_count: int
    recent_volume_minor: int
    legitimate_explanations: tuple[str, ...]
    limitations: tuple[str, ...]
    start_at: datetime
    end_at: datetime
