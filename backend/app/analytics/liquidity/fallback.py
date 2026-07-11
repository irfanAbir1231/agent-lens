from __future__ import annotations

from app.analytics.liquidity.models import LiquidityFeatures


def fallback_burn_rate(features: LiquidityFeatures) -> float:
    signed_total = (
        features.recent_signed_outflow_rate * 60
        + (features.prior_signed_outflow_rate or 0) * 120
    )
    return signed_total / 180
