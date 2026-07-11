from __future__ import annotations

from app.analytics.liquidity.models import (
    FactorEffect,
    ForecastFactor,
    LiquidityFeatures,
)


def build_factors(
    features: LiquidityFeatures, *, rate: float, fallback_used: bool
) -> tuple[ForecastFactor, ...]:
    factors = [
        ForecastFactor(
            code="NET_OUTFLOW_RATE",
            label="Weighted net outflow rate",
            value=f"{round(rate)} minor units/minute",
            effect=(
                FactorEffect.INCREASES_PRESSURE
                if rate > 0
                else FactorEffect.DECREASES_PRESSURE
            ),
        ),
        ForecastFactor(
            code="RECENT_SAMPLE",
            label="Recent successful transactions",
            value=str(features.recent_transaction_count),
            effect=(
                FactorEffect.CONTEXT
                if features.recent_transaction_count >= features.expected_recent_count
                else FactorEffect.LIMITS_CONFIDENCE
            ),
        ),
    ]
    if features.context.is_eid:
        factors.append(
            ForecastFactor(
                code="EID_CONTEXT",
                label="Eid demand context",
                value="active",
                effect=FactorEffect.INCREASES_PRESSURE,
            )
        )
    if features.context.is_salary_day:
        factors.append(
            ForecastFactor(
                code="SALARY_DAY_CONTEXT",
                label="Salary-day context",
                value="active",
                effect=FactorEffect.INCREASES_PRESSURE,
            )
        )
    if fallback_used:
        factors.append(
            ForecastFactor(
                code="FALLBACK_USED",
                label="Sparse-history fallback",
                value="180-minute average",
                effect=FactorEffect.LIMITS_CONFIDENCE,
            )
        )
    return tuple(factors[:4])
