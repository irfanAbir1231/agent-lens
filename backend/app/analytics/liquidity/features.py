from __future__ import annotations

from datetime import datetime, timedelta

from app.analytics.data_quality.models import (
    DataWindow,
    ProviderSourceData,
    TransactionRecord,
)
from app.analytics.liquidity.models import (
    LOOKBACK_MINUTES,
    RECENT_WINDOW_MINUTES,
    LiquidityFeatures,
    ScenarioContext,
)
from app.schemas.common import ensure_utc_datetime
from app.schemas.enums import TransactionStatus, TransactionType


def build_provider_features(
    source: ProviderSourceData,
    *,
    current_balance_minor: int,
    evaluated_at: datetime,
    context: ScenarioContext,
    data_quality_multiplier: float,
    feed_delay_minutes: float | None,
) -> LiquidityFeatures:
    return _build_features(
        transactions=source.transactions or (),
        current_balance_minor=current_balance_minor,
        evaluated_at=evaluated_at,
        context=context,
        data_quality_multiplier=data_quality_multiplier,
        feed_delay_minutes=feed_delay_minutes,
        provider_balance=True,
        expected_recent_count=5,
        minimum_evidence_count=3,
    )


def build_shared_cash_features(
    sources: tuple[ProviderSourceData, ...],
    *,
    current_balance_minor: int,
    evaluated_at: datetime,
    context: ScenarioContext,
    data_quality_multiplier: float,
    feed_delay_minutes: float | None,
) -> LiquidityFeatures:
    transactions = tuple(
        transaction for source in sources for transaction in (source.transactions or ())
    )
    return _build_features(
        transactions=transactions,
        current_balance_minor=current_balance_minor,
        evaluated_at=evaluated_at,
        context=context,
        data_quality_multiplier=data_quality_multiplier,
        feed_delay_minutes=feed_delay_minutes,
        provider_balance=False,
        expected_recent_count=15,
        minimum_evidence_count=9,
    )


def _build_features(
    *,
    transactions: tuple[TransactionRecord, ...],
    current_balance_minor: int,
    evaluated_at: datetime,
    context: ScenarioContext,
    data_quality_multiplier: float,
    feed_delay_minutes: float | None,
    provider_balance: bool,
    expected_recent_count: int,
    minimum_evidence_count: int,
) -> LiquidityFeatures:
    evaluated_at = ensure_utc_datetime(evaluated_at)
    recent_start = evaluated_at - timedelta(minutes=RECENT_WINDOW_MINUTES)
    lookback_start = evaluated_at - timedelta(minutes=LOOKBACK_MINUTES)
    usable = tuple(
        item
        for item in transactions
        if item.status == TransactionStatus.SUCCESS
        and lookback_start <= ensure_utc_datetime(item.occurred_at) <= evaluated_at
    )
    recent = tuple(
        item for item in usable if ensure_utc_datetime(item.occurred_at) >= recent_start
    )
    prior = tuple(
        item for item in usable if ensure_utc_datetime(item.occurred_at) < recent_start
    )
    recent_in, recent_out = _amounts(recent)
    prior_in, prior_out = _amounts(prior)
    recent_signed = _signed_outflow(recent_in, recent_out, provider_balance)
    prior_signed = _signed_outflow(prior_in, prior_out, provider_balance)
    last_30 = tuple(
        item
        for item in recent
        if ensure_utc_datetime(item.occurred_at) >= evaluated_at - timedelta(minutes=30)
    )
    previous_30 = tuple(item for item in recent if item not in last_30)
    last_in, last_out = _amounts(last_30)
    previous_in, previous_out = _amounts(previous_30)
    last_rate = _signed_outflow(last_in, last_out, provider_balance) / 30
    previous_rate = _signed_outflow(previous_in, previous_out, provider_balance) / 30
    total_recent = recent_in + recent_out
    return LiquidityFeatures(
        current_balance_minor=current_balance_minor,
        recent_cash_in_minor=recent_in,
        recent_cash_out_minor=recent_out,
        prior_cash_in_minor=prior_in,
        prior_cash_out_minor=prior_out,
        recent_transaction_count=len(recent),
        prior_transaction_count=len(prior),
        recent_signed_outflow_rate=recent_signed / RECENT_WINDOW_MINUTES,
        prior_signed_outflow_rate=(prior_signed / 120 if prior else None),
        recent_acceleration=(last_rate - previous_rate if previous_30 else None),
        cash_out_ratio=(recent_out / total_recent if total_recent else 0.0),
        feed_delay_minutes=feed_delay_minutes,
        data_quality_multiplier=data_quality_multiplier,
        expected_recent_count=expected_recent_count,
        minimum_evidence_count=minimum_evidence_count,
        context=context,
        data_window=DataWindow(
            start_at=lookback_start,
            end_at=evaluated_at,
            recent_window_start_at=recent_start,
            lookback_minutes=LOOKBACK_MINUTES,
            recent_window_minutes=RECENT_WINDOW_MINUTES,
        ),
    )


def _amounts(transactions: tuple[TransactionRecord, ...]) -> tuple[int, int]:
    cash_in = sum(
        item.amount_minor
        for item in transactions
        if item.transaction_type == TransactionType.CASH_IN
    )
    cash_out = sum(
        item.amount_minor
        for item in transactions
        if item.transaction_type == TransactionType.CASH_OUT
    )
    return cash_in, cash_out


def _signed_outflow(cash_in: int, cash_out: int, provider_balance: bool) -> int:
    return cash_in - cash_out if provider_balance else cash_out - cash_in
