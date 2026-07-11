from __future__ import annotations

from math import ceil

from app.analytics.liquidity.models import (
    FORECAST_HORIZON_MINUTES,
    LiquidityFeatures,
)


def active_burn_rate(features: LiquidityFeatures) -> float:
    rate = features.recent_signed_outflow_rate
    if features.prior_signed_outflow_rate is not None:
        rate = (0.75 * rate) + (0.25 * features.prior_signed_outflow_rate)
    if rate > 0:
        if features.context.is_eid:
            rate *= 1.15
        if features.context.is_salary_day:
            rate *= 1.10
    return rate


def projected_net_outflow(rate: float) -> int:
    return max(round(rate * FORECAST_HORIZON_MINUTES), 0)


def estimated_shortage_minutes(balance_minor: int, rate: float) -> int | None:
    if balance_minor <= 0:
        return 0
    if rate <= 0:
        return None
    return ceil(balance_minor / rate)
