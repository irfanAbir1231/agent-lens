from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta
from statistics import median

from app.analytics.anomaly.models import (
    LOOKBACK_MINUTES,
    RECENT_MINUTES,
    AnomalyEvaluation,
    Evidence,
    PeerBaseline,
)
from app.analytics.data_quality.models import ProviderEvaluation, ProviderSourceData
from app.schemas.enums import DataHealthStatus, TransactionStatus

BLOCKING_STATUSES = {DataHealthStatus.CONFLICTING, DataHealthStatus.UNAVAILABLE}


def build_peer_baseline(
    sources: list[ProviderSourceData], *, evaluated_at: datetime
) -> PeerBaseline:
    start = evaluated_at - timedelta(minutes=RECENT_MINUTES)
    counts: list[int] = []
    volumes: list[int] = []
    for source in sources:
        usable = _usable(source, start=start, end=evaluated_at)
        counts.append(len(usable))
        volumes.append(sum(item.amount_minor for item in usable))
    return PeerBaseline(
        recent_count_median=float(median(counts)) if counts else 0.0,
        recent_volume_median=float(median(volumes)) if volumes else 0.0,
    )


def evaluate_provider(
    *,
    agent_id: str,
    source: ProviderSourceData,
    quality: ProviderEvaluation,
    baseline: PeerBaseline,
    evaluated_at: datetime,
    is_eid: bool,
    ml_anomaly_score: float | None = None,
) -> AnomalyEvaluation:
    start_at = evaluated_at - timedelta(minutes=LOOKBACK_MINUTES)
    recent_start = evaluated_at - timedelta(minutes=RECENT_MINUTES)
    recent = _usable(source, start=recent_start, end=evaluated_at)
    recent_count = len(recent)
    volume = sum(item.amount_minor for item in recent)
    limitations = tuple(issue.description for issue in quality.issues)
    if quality.status in BLOCKING_STATUSES:
        return AnomalyEvaluation(
            agent_id,
            source.provider,
            0.0,
            "BLOCKED",
            0.0,
            True,
            quality.status,
            (),
            baseline,
            recent_count,
            volume,
            (),
            limitations
            + (
                "Authoritative anomaly evaluation is blocked until provider "
                "data is reconciled.",
            ),
            start_at,
            evaluated_at,
        )

    evidence: list[Evidence] = []
    if ml_anomaly_score is not None and ml_anomaly_score >= 0.5:
        evidence.append(
            Evidence(
                "ISOLATION_FOREST_SCORE",
                "The offline Isolation Forest model identified transaction-level "
                "deviation from the synthetic training baseline.",
                ml_anomaly_score,
                0.5,
                min(0.3, ml_anomaly_score * 0.3),
            )
        )
    count_ratio = _ratio(recent_count, baseline.recent_count_median)
    volume_ratio = _ratio(volume, baseline.recent_volume_median)
    if count_ratio >= 1.3:
        evidence.append(
            Evidence(
                "VELOCITY_SPIKE",
                f"Recent transaction count is {count_ratio:.2f}x the provider "
                "peer median.",
                count_ratio,
                baseline.recent_count_median,
                min(0.32, (count_ratio - 1) * 0.4),
            )
        )
    if volume_ratio >= 1.45:
        evidence.append(
            Evidence(
                "PEER_VOLUME_DEVIATION",
                f"Recent provider volume is {volume_ratio:.2f}x the provider "
                "peer median.",
                volume_ratio,
                baseline.recent_volume_median,
                min(0.45, (volume_ratio - 1) * 0.5),
            )
        )

    amount_bands = Counter(
        round(item.amount_minor / 50_000) * 50_000 for item in recent
    )
    repeated = max(amount_bands.values(), default=0)
    repeated_share = repeated / recent_count if recent_count else 0.0
    if repeated >= 4 and repeated_share >= 0.5:
        evidence.append(
            Evidence(
                "REPEATED_AMOUNT_PATTERN",
                f"{repeated} of {recent_count} recent transactions fall in the "
                "same 50,000-minor-unit amount band.",
                repeated_share,
                None,
                min(0.38, repeated_share * 0.45),
            )
        )

    balance = source.provider_balance_minor or 0
    coverage_ratio = volume / balance if balance > 0 else 0.0
    if coverage_ratio >= 1.5:
        evidence.append(
            Evidence(
                "LIQUIDITY_CONCENTRATION",
                f"Recent provider volume is {coverage_ratio:.2f}x the current "
                "balance; this is operational liquidity evidence only.",
                coverage_ratio,
                1.5,
                min(0.3, (coverage_ratio - 1) * 0.15),
            )
        )

    failure_rate = (
        sum(item.status == TransactionStatus.FAILED for item in recent) / recent_count
        if recent_count
        else 0.0
    )
    if failure_rate >= 0.2:
        evidence.append(
            Evidence(
                "ELEVATED_FAILURE_RATE",
                f"Recent failed-transaction rate is {failure_rate:.0%}.",
                failure_rate,
                0.2,
                min(0.2, failure_rate * 0.5),
            )
        )

    raw_score = min(1.0, sum(item.contribution for item in evidence))
    explanations: list[str] = []
    if is_eid:
        explanations.append(
            "Eid demand can legitimately increase transaction count and volume "
            "across providers."
        )
        explanations.append(
            "An explicit 55% contextual discount was applied; elevated volume "
            "alone does not imply misconduct."
        )
        raw_score *= 0.45
    score = round(raw_score, 3)
    confidence = round(
        min(1.0, quality.confidence_multiplier * min(1.0, recent_count / 6)), 3
    )
    level = (
        "NONE"
        if score < 0.25
        else "WATCH"
        if score < 0.5
        else "REVIEW"
        if score < 0.75
        else "PRIORITY_REVIEW"
    )
    return AnomalyEvaluation(
        agent_id,
        source.provider,
        score,
        level,
        confidence,
        False,
        quality.status,
        tuple(evidence),
        baseline,
        recent_count,
        volume,
        tuple(explanations),
        limitations,
        start_at,
        evaluated_at,
    )


def _usable(source: ProviderSourceData, *, start: datetime, end: datetime) -> tuple:
    return tuple(
        item for item in (source.transactions or ()) if start <= item.occurred_at <= end
    )


def _ratio(value: float, baseline: float) -> float:
    return value / baseline if baseline > 0 else (1.0 if value == 0 else 2.0)
