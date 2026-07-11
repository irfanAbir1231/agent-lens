from __future__ import annotations

from app.analytics.liquidity.models import LiquidityFeatures


def calculate_confidence(
    features: LiquidityFeatures, *, fallback_used: bool, blocked: bool
) -> float:
    if blocked or features.current_balance_minor < 0:
        return 0.0
    sample = min(features.total_transaction_count / features.expected_recent_count, 1.0)
    coverage = min(
        features.recent_transaction_count / features.expected_recent_count, 1.0
    )
    delay = features.feed_delay_minutes
    freshness = 1.0 if delay is not None and delay <= 5 else 0.9
    if delay is None or delay > 30:
        freshness = 0.0
    elif delay > 15:
        freshness = 0.8
    stability = 0.9
    if features.prior_signed_outflow_rate is not None:
        denominator = max(
            abs(features.recent_signed_outflow_rate),
            abs(features.prior_signed_outflow_rate),
            1.0,
        )
        divergence = min(
            abs(
                features.recent_signed_outflow_rate - features.prior_signed_outflow_rate
            )
            / denominator,
            1.0,
        )
        stability = max(0.6, 1 - (0.4 * divergence))
    fallback = 0.7 if fallback_used else 1.0
    confidence = (
        features.data_quality_multiplier
        * sample
        * coverage
        * freshness
        * stability
        * fallback
    )
    return round(max(0.0, min(confidence, 1.0)), 3)
