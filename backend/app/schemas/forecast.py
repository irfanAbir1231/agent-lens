from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field

from app.schemas.common import AgentLensSchema
from app.schemas.data_quality import DataQualityWindow
from app.schemas.enums import (
    DataHealthStatus,
    PressureLevel,
    Provider,
    ScenarioId,
)


class ForecastSummary(AgentLensSchema):
    provider: Provider
    current_balance_minor: int = Field(ge=0)
    predicted_net_outflow_minor: int = Field(ge=0)
    pressure_level: PressureLevel
    confidence: float = Field(ge=0.0, le=1.0)


class ForecastFactor(AgentLensSchema):
    code: str
    label: str
    value: str
    effect: str


class ProviderForecastDataQuality(AgentLensSchema):
    provider: Provider
    status: DataHealthStatus
    confidence_multiplier: float = Field(ge=0.0, le=1.0)
    allow_forecast: bool
    limitations: list[str]


class ForecastDataQualitySummary(AgentLensSchema):
    evaluator_version: str
    overall_status: DataHealthStatus
    overall_confidence_multiplier: float = Field(ge=0.0, le=1.0)
    shared_cash_allow_forecast: bool
    provider_results: list[ProviderForecastDataQuality]


class ProviderLiquidityForecast(AgentLensSchema):
    forecast_id: str
    agent_id: str
    provider: Provider
    generated_at: datetime
    forecast_horizon_minutes: int = Field(ge=1)
    current_balance_minor: int
    predicted_net_outflow_minor: int = Field(ge=0)
    shortage_probability: float | None = Field(default=None, ge=0.0, le=1.0)
    shortage_probability_is_calibrated: Literal[False] = False
    estimated_shortage_minutes: int | None = Field(default=None, ge=0)
    pressure_level: PressureLevel
    confidence: float = Field(ge=0.0, le=1.0)
    top_factors: list[ForecastFactor]
    data_quality_status: DataHealthStatus
    data_quality_limitations: list[str]
    method_version: str
    data_window: DataQualityWindow
    fallback_used: bool
    fallback_reason: str | None
    forecast_blocked: bool
    recommended_verification_steps: list[str]
    prediction_source: Literal["XGBOOST_MODEL", "DETERMINISTIC_FALLBACK"]
    model_version: str


class SharedCashLiquidityForecast(AgentLensSchema):
    forecast_id: str
    agent_id: str
    target: Literal["SHARED_CASH"]
    generated_at: datetime
    forecast_horizon_minutes: int = Field(ge=1)
    current_balance_minor: int
    predicted_net_outflow_minor: int = Field(ge=0)
    shortage_probability: float | None = Field(default=None, ge=0.0, le=1.0)
    shortage_probability_is_calibrated: Literal[False] = False
    estimated_shortage_minutes: int | None = Field(default=None, ge=0)
    pressure_level: PressureLevel
    confidence: float = Field(ge=0.0, le=1.0)
    top_factors: list[ForecastFactor]
    data_quality_status: DataHealthStatus
    data_quality_limitations: list[str]
    method_version: str
    data_window: DataQualityWindow
    fallback_used: bool
    fallback_reason: str | None
    forecast_blocked: bool
    recommended_verification_steps: list[str]
    prediction_source: Literal["XGBOOST_MODEL", "DETERMINISTIC_FALLBACK"]
    model_version: str


class LiquidityForecastResponse(AgentLensSchema):
    generated_at: datetime
    active_scenario_id: ScenarioId
    is_synthetic_data: bool
    forecast_horizon_minutes: int = Field(ge=1)
    method_version: str
    data_quality_summary: ForecastDataQualitySummary
    shared_cash_forecast: SharedCashLiquidityForecast
    provider_forecasts: list[ProviderLiquidityForecast]
