from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.analytics.data_quality.evaluator import EVALUATOR_VERSION, DataQualityEvaluator
from app.analytics.data_quality.models import ProviderEvaluation
from app.analytics.liquidity.evaluator import evaluate_liquidity_target
from app.analytics.liquidity.features import (
    build_provider_features,
    build_shared_cash_features,
)
from app.analytics.liquidity.models import (
    FORECAST_HORIZON_MINUTES,
    METHOD_VERSION,
    ForecastTarget,
    LiquidityForecast,
    ScenarioContext,
)
from app.core.config import get_settings
from app.core.errors import NotFoundError
from app.ml.runtime import ModelPrediction, ModelRuntime
from app.repositories.forecast_repository import ForecastRepository
from app.schemas.data_quality import DataQualityWindow
from app.schemas.enums import ScenarioId
from app.schemas.forecast import (
    ForecastDataQualitySummary,
    ForecastFactor,
    LiquidityForecastResponse,
    ProviderForecastDataQuality,
    ProviderLiquidityForecast,
    SharedCashLiquidityForecast,
)


class ForecastService:
    def __init__(self, session: Session) -> None:
        self._repository = ForecastRepository(session)
        self._quality = DataQualityEvaluator()
        settings = get_settings()
        self._model = ModelRuntime(
            settings.model_artifact_dir / settings.model_bundle_name
        )

    def get_forecast(self, *, agent_id: str) -> LiquidityForecastResponse:
        # The scenario clock is authoritative for deterministic synthetic analysis.
        source = self._repository.get_source(agent_id=agent_id)
        if source is None:
            raise NotFoundError(
                code="agent_not_found",
                message=f"Agent {agent_id} was not found.",
                details={"agent_id": agent_id},
            )
        evaluated_at = source.scenario.generated_at
        context = _scenario_context(evaluated_at, source.scenario_metadata)
        quality = self._quality.evaluate_agent(
            source.agent_source, evaluated_at=evaluated_at
        )
        by_provider = {item.provider: item for item in quality.provider_results}
        provider_forecasts = []
        for provider_source in source.agent_source.providers:
            provider_quality = by_provider[provider_source.provider]
            features = build_provider_features(
                provider_source,
                current_balance_minor=provider_source.provider_balance_minor or 0,
                evaluated_at=evaluated_at,
                context=context,
                data_quality_multiplier=provider_quality.confidence_multiplier,
                feed_delay_minutes=provider_quality.measured_evidence.feed_delay_minutes,
            )
            prediction = self._model_prediction(
                agent_id=agent_id,
                provider=provider_source.provider.value,
                allow_forecast=provider_quality.allow_forecast,
            )
            provider_forecasts.append(
                evaluate_liquidity_target(
                    agent_id=agent_id,
                    provider=provider_source.provider,
                    target=None,
                    features=features,
                    data_quality_status=provider_quality.status,
                    data_quality_limitations=tuple(
                        issue.description for issue in provider_quality.issues
                    ),
                    recommended_verification_steps=tuple(
                        issue.recommended_verification_step
                        for issue in provider_quality.issues
                    ),
                    allow_forecast=provider_quality.allow_forecast,
                    ml_net_outflow_minor=(
                        max(0, prediction.cash_out_minor - prediction.cash_in_minor)
                        if prediction is not None
                        else None
                    ),
                    ml_confidence=(prediction.confidence if prediction else None),
                    model_version=(prediction.model_version if prediction else None),
                )
            )
        shared_allowed = all(item.allow_forecast for item in quality.provider_results)
        shared_features = build_shared_cash_features(
            source.agent_source.providers,
            current_balance_minor=source.shared_cash_minor,
            evaluated_at=evaluated_at,
            context=context,
            data_quality_multiplier=quality.overall_confidence_multiplier,
            feed_delay_minutes=max(
                (
                    item.measured_evidence.feed_delay_minutes or 0
                    for item in quality.provider_results
                ),
                default=0,
            ),
        )
        shared_limitations = tuple(
            f"{item.provider.value}: {issue.description}"
            for item in quality.provider_results
            for issue in item.issues
        )
        shared_steps = tuple(
            dict.fromkeys(
                issue.recommended_verification_step
                for item in quality.provider_results
                for issue in item.issues
            )
        )
        shared = evaluate_liquidity_target(
            agent_id=agent_id,
            provider=None,
            target=ForecastTarget.SHARED_CASH,
            features=shared_features,
            data_quality_status=quality.overall_status,
            data_quality_limitations=shared_limitations,
            recommended_verification_steps=shared_steps,
            allow_forecast=shared_allowed,
        )
        return LiquidityForecastResponse(
            generated_at=evaluated_at,
            active_scenario_id=ScenarioId(source.scenario.id),
            is_synthetic_data=source.scenario.is_synthetic_data,
            forecast_horizon_minutes=FORECAST_HORIZON_MINUTES,
            method_version=METHOD_VERSION,
            data_quality_summary=ForecastDataQualitySummary(
                evaluator_version=EVALUATOR_VERSION,
                overall_status=quality.overall_status,
                overall_confidence_multiplier=quality.overall_confidence_multiplier,
                shared_cash_allow_forecast=shared_allowed,
                provider_results=[
                    _quality_schema(item) for item in quality.provider_results
                ],
            ),
            shared_cash_forecast=_shared_schema(shared),
            provider_forecasts=[_provider_schema(item) for item in provider_forecasts],
        )

    def _model_prediction(
        self, *, agent_id: str, provider: str, allow_forecast: bool
    ) -> ModelPrediction | None:
        if not allow_forecast or not self._model.available:
            return None
        rows = self._repository.list_ml_observations(
            agent_id=agent_id, provider=provider
        )
        try:
            return self._model.predict(rows)
        except (FileNotFoundError, KeyError, TypeError, ValueError):
            return None


def _scenario_context(
    evaluated_at: datetime, metadata: dict[str, Any]
) -> ScenarioContext:
    is_eid = metadata.get("event") == "EID"
    return ScenarioContext(
        is_eid=is_eid,
        is_holiday=is_eid,
        is_salary_day=evaluated_at.day <= 7 or evaluated_at.day >= 25,
        hour_of_day=evaluated_at.hour,
        day_of_week=evaluated_at.weekday(),
    )


def _quality_schema(item: ProviderEvaluation) -> ProviderForecastDataQuality:
    return ProviderForecastDataQuality(
        provider=item.provider,
        status=item.status,
        confidence_multiplier=item.confidence_multiplier,
        allow_forecast=item.allow_forecast,
        limitations=[issue.description for issue in item.issues],
    )


def _common(item: LiquidityForecast) -> dict[str, object]:
    return {
        "forecast_id": item.forecast_id,
        "agent_id": item.agent_id,
        "generated_at": item.generated_at,
        "forecast_horizon_minutes": FORECAST_HORIZON_MINUTES,
        "current_balance_minor": item.current_balance_minor,
        "predicted_net_outflow_minor": item.predicted_net_outflow_minor,
        "shortage_probability": item.shortage_probability,
        "estimated_shortage_minutes": item.estimated_shortage_minutes,
        "pressure_level": item.pressure_level,
        "confidence": item.confidence,
        "top_factors": [
            ForecastFactor.model_validate(value) for value in item.top_factors
        ],
        "data_quality_status": item.data_quality_status,
        "data_quality_limitations": list(item.data_quality_limitations),
        "method_version": METHOD_VERSION,
        "data_window": DataQualityWindow.model_validate(item.data_window),
        "fallback_used": item.fallback_used,
        "fallback_reason": item.fallback_reason,
        "forecast_blocked": item.forecast_blocked,
        "recommended_verification_steps": list(item.recommended_verification_steps),
        "prediction_source": item.prediction_source,
        "model_version": item.model_version,
    }


def _provider_schema(item: LiquidityForecast) -> ProviderLiquidityForecast:
    assert item.provider is not None
    return ProviderLiquidityForecast.model_validate(
        {**_common(item), "provider": item.provider}
    )


def _shared_schema(item: LiquidityForecast) -> SharedCashLiquidityForecast:
    return SharedCashLiquidityForecast.model_validate(
        {**_common(item), "target": "SHARED_CASH"}
    )
