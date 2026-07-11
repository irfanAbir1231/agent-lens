from __future__ import annotations

import re

from app.ai.schemas import (
    AdvisoryProviderContext,
    SanitizedAdvisoryInput,
    SanitizedEvidence,
    SanitizedSource,
)
from app.schemas.alert import AlertDetail, RetrievalSource
from app.schemas.enums import DataHealthStatus, PressureLevel
from app.schemas.forecast import ProviderLiquidityForecast

FORBIDDEN_INPUT_PATTERNS = (
    re.compile(r"SIM-ACC-", re.IGNORECASE),
    re.compile(r"\b(?:pin|otp|password|secret|api[_ -]?key)\b", re.IGNORECASE),
    re.compile(r"\b(?:\+?8801|01)[3-9]\d{8}\b"),
)


def build_advisory_input(
    *,
    analysis_id: str,
    agent_id: str,
    eligible: list[tuple[AlertDetail, ProviderLiquidityForecast]],
) -> SanitizedAdvisoryInput:
    payload = SanitizedAdvisoryInput(
        analysis_id=analysis_id,
        agent_id=agent_id,
        providers=[_provider_context(alert, forecast) for alert, forecast in eligible],
    )
    serialized = payload.model_dump_json()
    if any(pattern.search(serialized) for pattern in FORBIDDEN_INPUT_PATTERNS):
        raise UnsafeAdvisoryInputError(
            "The minimized advisory payload contained a prohibited value."
        )
    return payload


def _provider_context(
    alert: AlertDetail, forecast: ProviderLiquidityForecast
) -> AdvisoryProviderContext:
    return AdvisoryProviderContext(
        provider=alert.provider,
        data_quality_status=DataHealthStatus(alert.anomaly.data_quality_status),
        data_quality_confidence=alert.anomaly.confidence,
        pressure_level=PressureLevel(forecast.pressure_level),
        forecast_confidence=forecast.confidence,
        estimated_shortage_minutes=forecast.estimated_shortage_minutes,
        anomaly_score=alert.anomaly.anomaly_score,
        anomaly_evidence=[
            SanitizedEvidence(
                code=item.code,
                description=item.description,
                measured_value=item.measured_value,
                baseline_value=item.baseline_value,
            )
            for item in alert.anomaly.evidence
        ],
        legitimate_explanations=alert.anomaly.legitimate_explanations,
        limitations=alert.limitations,
        alert_type=alert.alert_type,
        severity=alert.severity,
        risk_reasons=alert.risk.reasons,
        required_human_role=alert.risk.required_human_role,
        allowed_actions=alert.risk.allowed_actions,
        prohibited_actions=alert.risk.prohibited_actions,
        policy_sources=[_source(item) for item in alert.policy_sources],
        similar_cases=[_source(item) for item in alert.similar_cases],
    )


def _source(item: RetrievalSource) -> SanitizedSource:
    return SanitizedSource(
        source_id=item.source_id,
        title=item.title,
        excerpt=item.excerpt[:500],
        relevance_reason=item.relevance_reason,
    )


class UnsafeAdvisoryInputError(ValueError):
    pass
