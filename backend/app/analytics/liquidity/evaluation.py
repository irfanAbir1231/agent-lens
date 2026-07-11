from __future__ import annotations

from datetime import UTC, datetime, timedelta
from math import sqrt
from statistics import mean
from typing import Any

from app.analytics.data_quality.models import ProviderSourceData, TransactionRecord
from app.analytics.liquidity.baseline import active_burn_rate, projected_net_outflow
from app.analytics.liquidity.features import build_provider_features
from app.analytics.liquidity.models import METHOD_VERSION, ScenarioContext
from app.schemas.enums import (
    DataHealthStatus,
    Provider,
    TransactionStatus,
    TransactionType,
)


def evaluate_baseline() -> dict[str, Any]:
    start = datetime(2026, 1, 1, 8, 0, tzinfo=UTC)
    transactions = _evaluation_transactions(start)
    predictions: list[int] = []
    actuals: list[int] = []
    lead_times: list[int] = []
    for hour in range(3, 11):
        cutoff = start + timedelta(hours=hour)
        features = build_provider_features(
            _source(transactions),
            current_balance_minor=1_600_000,
            evaluated_at=cutoff,
            context=ScenarioContext(False, False, False, cutoff.hour, cutoff.weekday()),
            data_quality_multiplier=1.0,
            feed_delay_minutes=2,
        )
        prediction = projected_net_outflow(active_burn_rate(features))
        future = tuple(
            item
            for item in transactions
            if cutoff < item.occurred_at <= cutoff + timedelta(minutes=60)
        )
        if not future:
            continue
        actual = max(
            sum(
                item.amount_minor
                if item.transaction_type == TransactionType.CASH_IN
                else -item.amount_minor
                for item in future
            ),
            0,
        )
        predictions.append(prediction)
        actuals.append(actual)
        depletion = _actual_shortage_minutes(
            future, cutoff=cutoff, balance_minor=1_600_000
        )
        if depletion is not None and prediction >= 1_600_000:
            lead_times.append(depletion)
    errors = [
        prediction - actual
        for prediction, actual in zip(predictions, actuals, strict=True)
    ]
    leakage_check = _leakage_check(transactions, start + timedelta(hours=6))
    return {
        "method_version": METHOD_VERSION,
        "forecast_horizon_minutes": 60,
        "sample_count": len(errors),
        "mae_net_outflow_minor": round(mean(abs(error) for error in errors), 3),
        "rmse_net_outflow_minor": round(sqrt(mean(error**2 for error in errors)), 3),
        "smape_percent": round(_smape(predictions, actuals), 3),
        "shortage_detection_lead_time_minutes": (
            round(mean(lead_times), 3) if lead_times else None
        ),
        "shortage_lead_time_sample_count": len(lead_times),
        "leakage_check_passed": leakage_check,
    }


def _evaluation_transactions(start: datetime) -> tuple[TransactionRecord, ...]:
    records = []
    for index in range(48):
        occurred_at = start + timedelta(minutes=index * 15)
        high_demand = 16 <= index < 28
        transaction_type = (
            TransactionType.CASH_IN
            if high_demand or index % 3 != 0
            else TransactionType.CASH_OUT
        )
        amount = 420_000 if high_demand else 180_000 + (index % 4) * 20_000
        records.append(
            TransactionRecord(
                id=f"EVAL-{index:03d}",
                transaction_type=transaction_type,
                amount_minor=amount,
                status=TransactionStatus.SUCCESS,
                synthetic_account_reference=f"EVAL-ACC-{index % 8:02d}",
                occurred_at=occurred_at,
            )
        )
    return tuple(records)


def _source(records: tuple[TransactionRecord, ...]) -> ProviderSourceData:
    return ProviderSourceData(
        provider=Provider.NAGAD,
        provider_balance_minor=1_600_000,
        feed_status=DataHealthStatus.HEALTHY,
        last_received_at=records[-1].occurred_at,
        feed_reported_balance_minor=1_600_000,
        ledger_balance_minor=1_600_000,
        transactions=records,
    )


def _actual_shortage_minutes(
    records: tuple[TransactionRecord, ...], *, cutoff: datetime, balance_minor: int
) -> int | None:
    balance = balance_minor
    for item in sorted(records, key=lambda value: value.occurred_at):
        balance -= (
            item.amount_minor
            if item.transaction_type == TransactionType.CASH_IN
            else -item.amount_minor
        )
        if balance <= 0:
            return round((item.occurred_at - cutoff).total_seconds() / 60)
    return None


def _smape(predictions: list[int], actuals: list[int]) -> float:
    terms = []
    for prediction, actual in zip(predictions, actuals, strict=True):
        denominator = abs(prediction) + abs(actual)
        if denominator:
            terms.append(200 * abs(prediction - actual) / denominator)
    return mean(terms) if terms else 0.0


def _leakage_check(records: tuple[TransactionRecord, ...], cutoff: datetime) -> bool:
    context = ScenarioContext(False, False, False, cutoff.hour, cutoff.weekday())
    before = build_provider_features(
        _source(records),
        current_balance_minor=1_600_000,
        evaluated_at=cutoff,
        context=context,
        data_quality_multiplier=1.0,
        feed_delay_minutes=2,
    )
    future = TransactionRecord(
        id="FUTURE-LEAK-CHECK",
        transaction_type=TransactionType.CASH_IN,
        amount_minor=99_000_000,
        status=TransactionStatus.SUCCESS,
        synthetic_account_reference="EVAL-FUTURE",
        occurred_at=cutoff + timedelta(minutes=1),
    )
    after = build_provider_features(
        _source(records + (future,)),
        current_balance_minor=1_600_000,
        evaluated_at=cutoff,
        context=context,
        data_quality_multiplier=1.0,
        feed_delay_minutes=2,
    )
    return before == after
