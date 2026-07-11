from __future__ import annotations

from hashlib import sha256

from app.analytics.liquidity.baseline import (
    active_burn_rate,
    estimated_shortage_minutes,
    projected_net_outflow,
)
from app.analytics.liquidity.confidence import calculate_confidence
from app.analytics.liquidity.explanations import build_factors
from app.analytics.liquidity.fallback import fallback_burn_rate
from app.analytics.liquidity.models import (
    METHOD_VERSION,
    ForecastTarget,
    LiquidityFeatures,
    LiquidityForecast,
)
from app.analytics.liquidity.rules import pressure_level, shortage_risk_estimate
from app.schemas.enums import DataHealthStatus, Provider


def evaluate_liquidity_target(
    *,
    agent_id: str,
    provider: Provider | None,
    target: ForecastTarget | None,
    features: LiquidityFeatures,
    data_quality_status: DataHealthStatus,
    data_quality_limitations: tuple[str, ...],
    recommended_verification_steps: tuple[str, ...],
    allow_forecast: bool,
    ml_net_outflow_minor: int | None = None,
    ml_confidence: float | None = None,
    model_version: str | None = None,
) -> LiquidityForecast:
    invalid_balance = features.current_balance_minor < 0
    blocked = not allow_forecast or invalid_balance
    fallback_used = False
    fallback_reason: str | None = None
    if blocked:
        rate = 0.0
    elif ml_net_outflow_minor is not None:
        rate = max(0.0, float(ml_net_outflow_minor))
    elif features.recent_transaction_count < features.expected_recent_count:
        fallback_used = True
        fallback_reason = (
            "NO_USABLE_HISTORY"
            if features.total_transaction_count == 0
            else "SPARSE_RECENT_ACTIVITY"
        )
        rate = fallback_burn_rate(features)
    else:
        rate = active_burn_rate(features)
    evidence_sufficient = (
        features.total_transaction_count >= features.minimum_evidence_count
        and not invalid_balance
    )
    confidence = calculate_confidence(
        features, fallback_used=fallback_used, blocked=blocked
    )
    if ml_confidence is not None and not blocked:
        confidence = min(confidence, ml_confidence * features.data_quality_multiplier)
    shortage_minutes = (
        None
        if blocked
        else estimated_shortage_minutes(features.current_balance_minor, rate)
    )
    pressure = pressure_level(
        estimated_minutes=shortage_minutes,
        evidence_sufficient=evidence_sufficient,
        blocked=blocked,
    )
    limitations = list(data_quality_limitations)
    if invalid_balance:
        limitations.append("Current balance is negative and cannot support a forecast.")
    if not evidence_sufficient and not blocked:
        limitations.append(
            "Transaction evidence is too weak for pressure classification."
        )
    return LiquidityForecast(
        forecast_id=_forecast_id(
            agent_id=agent_id,
            target=provider.value
            if provider is not None
            else ForecastTarget.SHARED_CASH,
            generated_at=features.data_window.end_at.isoformat(),
        ),
        agent_id=agent_id,
        provider=provider,
        target=target,
        generated_at=features.data_window.end_at,
        current_balance_minor=features.current_balance_minor,
        predicted_net_outflow_minor=(0 if blocked else projected_net_outflow(rate)),
        shortage_probability=shortage_risk_estimate(
            estimated_minutes=shortage_minutes,
            confidence=confidence,
            pressure=pressure,
        ),
        estimated_shortage_minutes=shortage_minutes,
        pressure_level=pressure,
        confidence=confidence,
        top_factors=(
            ()
            if blocked
            else build_factors(features, rate=rate, fallback_used=fallback_used)
        ),
        data_quality_status=data_quality_status,
        data_quality_limitations=tuple(dict.fromkeys(limitations)),
        data_window=features.data_window,
        fallback_used=fallback_used,
        fallback_reason=fallback_reason,
        forecast_blocked=blocked,
        recommended_verification_steps=recommended_verification_steps,
        prediction_source=(
            "XGBOOST_MODEL"
            if ml_net_outflow_minor is not None and not blocked
            else "DETERMINISTIC_FALLBACK"
        ),
        model_version=model_version or METHOD_VERSION,
    )


def _forecast_id(*, agent_id: str, target: str, generated_at: str) -> str:
    payload = f"{agent_id}|{target}|{generated_at}|{METHOD_VERSION}|60"
    digest = sha256(payload.encode()).hexdigest()[:16].upper()
    return f"FORECAST-{digest}"
