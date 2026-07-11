from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from app.analytics.data_quality.models import DataWindow
from app.schemas.enums import DataHealthStatus, PressureLevel, Provider

FORECAST_HORIZON_MINUTES = 60
LOOKBACK_MINUTES = 180
RECENT_WINDOW_MINUTES = 60
METHOD_VERSION = "liquidity-baseline-v1"


class ForecastTarget(StrEnum):
    SHARED_CASH = "SHARED_CASH"


class FactorEffect(StrEnum):
    INCREASES_PRESSURE = "INCREASES_PRESSURE"
    DECREASES_PRESSURE = "DECREASES_PRESSURE"
    LIMITS_CONFIDENCE = "LIMITS_CONFIDENCE"
    CONTEXT = "CONTEXT"


@dataclass(frozen=True)
class ScenarioContext:
    is_eid: bool
    is_holiday: bool
    is_salary_day: bool
    hour_of_day: int
    day_of_week: int


@dataclass(frozen=True)
class LiquidityFeatures:
    current_balance_minor: int
    recent_cash_in_minor: int
    recent_cash_out_minor: int
    prior_cash_in_minor: int
    prior_cash_out_minor: int
    recent_transaction_count: int
    prior_transaction_count: int
    recent_signed_outflow_rate: float
    prior_signed_outflow_rate: float | None
    recent_acceleration: float | None
    cash_out_ratio: float
    feed_delay_minutes: float | None
    data_quality_multiplier: float
    expected_recent_count: int
    minimum_evidence_count: int
    context: ScenarioContext
    data_window: DataWindow

    @property
    def total_transaction_count(self) -> int:
        return self.recent_transaction_count + self.prior_transaction_count


@dataclass(frozen=True)
class ForecastFactor:
    code: str
    label: str
    value: str
    effect: FactorEffect


@dataclass(frozen=True)
class LiquidityForecast:
    forecast_id: str
    agent_id: str
    provider: Provider | None
    target: ForecastTarget | None
    generated_at: datetime
    current_balance_minor: int
    predicted_net_outflow_minor: int
    shortage_probability: float | None
    estimated_shortage_minutes: int | None
    pressure_level: PressureLevel
    confidence: float
    top_factors: tuple[ForecastFactor, ...]
    data_quality_status: DataHealthStatus
    data_quality_limitations: tuple[str, ...]
    data_window: DataWindow
    fallback_used: bool
    fallback_reason: str | None
    forecast_blocked: bool
    recommended_verification_steps: tuple[str, ...]
    prediction_source: str
    model_version: str
