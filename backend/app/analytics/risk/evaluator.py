from __future__ import annotations

from app.analytics.anomaly.models import AnomalyEvaluation
from app.schemas.enums import (
    AlertType,
    DataHealthStatus,
    PressureLevel,
    Severity,
    UserRole,
)
from app.schemas.forecast import ProviderLiquidityForecast
from app.schemas.risk import RiskAssessment

RULE_VERSION = "risk-fusion-rules-v1"
BLOCKING = {DataHealthStatus.CONFLICTING, DataHealthStatus.UNAVAILABLE}
PRESSURE_RANK = {
    PressureLevel.UNKNOWN: 0,
    PressureLevel.NORMAL: 0,
    PressureLevel.WATCH: 1,
    PressureLevel.HIGH: 2,
    PressureLevel.CRITICAL: 3,
}


def fuse_risk(
    anomaly: AnomalyEvaluation,
    forecast: ProviderLiquidityForecast,
    *,
    allow_ai_from_quality: bool,
    is_eid: bool,
) -> RiskAssessment:
    reasons: list[str] = []
    pressure = PressureLevel(forecast.pressure_level)
    if anomaly.blocked or anomaly.data_quality_status in BLOCKING:
        reasons.append(
            f"{anomaly.provider.value} evidence is "
            f"{anomaly.data_quality_status.value}; authoritative anomaly "
            "conclusions are blocked."
        )
        return _result(
            Severity.MEDIUM,
            AlertType.DATA_QUALITY,
            reasons,
            confidence=forecast.confidence,
            allow_ai=False,
            role=UserRole.PROVIDER_OPERATIONS,
            allowed=["manual_verification", "feed_escalation"],
        )

    if anomaly.evidence:
        reasons.extend(item.description for item in anomaly.evidence[:3])
    pressure_rank = PRESSURE_RANK[pressure]
    if pressure_rank:
        reasons.append(
            f"Provider-only liquidity forecast is {pressure.value} with "
            f"confidence {forecast.confidence:.2f}."
        )

    if (
        is_eid
        and anomaly.score < 0.5
        and anomaly.data_quality_status == DataHealthStatus.HEALTHY
    ):
        reasons.append(
            "Eid context explains elevated demand; the unusual-activity score "
            "remains below review level after the explicit discount."
        )
        return _result(
            Severity.LOW,
            AlertType.LIQUIDITY_PRESSURE,
            reasons,
            confidence=min(anomaly.confidence, forecast.confidence),
            allow_ai=allow_ai_from_quality,
            role=UserRole.PROVIDER_OPERATIONS,
            allowed=["continue_monitoring", "manual_verification"],
        )

    pressured = pressure_rank >= 2
    unusual = anomaly.score >= 0.5 or (
        pressured and anomaly.score >= 0.25 and bool(anomaly.evidence)
    )
    if unusual and pressured:
        alert_type = AlertType.COMBINED_OPERATIONAL_REVIEW
        severity = (
            Severity.CRITICAL
            if anomaly.score >= 0.75 and pressure_rank == 3
            else Severity.HIGH
        )
        role = UserRole.RISK_ANALYST
    elif unusual:
        alert_type = AlertType.UNUSUAL_ACTIVITY
        severity = Severity.HIGH if anomaly.score >= 0.75 else Severity.MEDIUM
        role = UserRole.RISK_ANALYST
    elif pressured:
        alert_type = AlertType.LIQUIDITY_PRESSURE
        severity = Severity.HIGH if pressure_rank == 3 else Severity.MEDIUM
        role = UserRole.PROVIDER_OPERATIONS
    elif pressure_rank == 1:
        alert_type = AlertType.LIQUIDITY_PRESSURE
        severity = Severity.MEDIUM
        role = UserRole.PROVIDER_OPERATIONS
    else:
        alert_type = AlertType.UNUSUAL_ACTIVITY
        severity = Severity.LOW
        role = UserRole.RISK_ANALYST
        reasons.append(
            "Measured provider activity is within the current contextual baseline."
        )

    confidence = round(min(anomaly.confidence, forecast.confidence), 3)
    return _result(
        severity,
        alert_type,
        reasons,
        confidence=confidence,
        allow_ai=allow_ai_from_quality and confidence >= 0.75,
        role=role,
        allowed=["manual_verification", "continue_monitoring", "provider_escalation"],
    )


def _result(
    severity: Severity,
    alert_type: AlertType,
    reasons: list[str],
    *,
    confidence: float,
    allow_ai: bool,
    role: UserRole,
    allowed: list[str],
) -> RiskAssessment:
    priority = {
        Severity.CRITICAL: 1,
        Severity.HIGH: 2,
        Severity.MEDIUM: 3,
        Severity.LOW: 4,
    }[severity]
    return RiskAssessment(
        severity=severity,
        alert_type=alert_type,
        priority=priority,
        reasons=reasons,
        confidence=max(0.0, min(1.0, round(confidence, 3))),
        allow_ai_advisory=allow_ai,
        required_human_role=role,
        allowed_actions=allowed,
        prohibited_actions=[
            "automatic_financial_action",
            "automatic_account_restriction",
            "declare_fraud_or_guilt",
            "convert_or_combine_provider_balances",
        ],
        rule_version=RULE_VERSION,
    )
