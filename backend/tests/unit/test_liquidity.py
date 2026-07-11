from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest

from app.analytics.data_quality.models import ProviderSourceData, TransactionRecord
from app.analytics.liquidity.baseline import (
    active_burn_rate,
    estimated_shortage_minutes,
    projected_net_outflow,
)
from app.analytics.liquidity.confidence import calculate_confidence
from app.analytics.liquidity.evaluation import evaluate_baseline
from app.analytics.liquidity.evaluator import evaluate_liquidity_target
from app.analytics.liquidity.features import (
    build_provider_features,
    build_shared_cash_features,
)
from app.analytics.liquidity.models import (
    ForecastTarget,
    LiquidityFeatures,
    ScenarioContext,
)
from app.analytics.liquidity.rules import pressure_level
from app.schemas.enums import (
    DataHealthStatus,
    PressureLevel,
    Provider,
    TransactionStatus,
    TransactionType,
)

CUTOFF = datetime(2026, 4, 10, 9, 30, tzinfo=UTC)
CONTEXT = ScenarioContext(False, False, False, 9, 4)


def tx(
    index: int,
    transaction_type: TransactionType,
    amount: int,
    *,
    minutes_ago: int,
) -> TransactionRecord:
    return TransactionRecord(
        id=f"TX-{index}",
        transaction_type=transaction_type,
        amount_minor=amount,
        status=TransactionStatus.SUCCESS,
        synthetic_account_reference=f"ACC-{index}",
        occurred_at=CUTOFF - timedelta(minutes=minutes_ago),
    )


def source(
    provider: Provider, transactions: tuple[TransactionRecord, ...]
) -> ProviderSourceData:
    return ProviderSourceData(
        provider=provider,
        provider_balance_minor=1_000_000,
        feed_status=DataHealthStatus.HEALTHY,
        last_received_at=CUTOFF - timedelta(minutes=2),
        feed_reported_balance_minor=1_000_000,
        ledger_balance_minor=1_000_000,
        transactions=transactions,
    )


def features(
    transactions: tuple[TransactionRecord, ...],
) -> LiquidityFeatures:
    return build_provider_features(
        source(Provider.BKASH, transactions),
        current_balance_minor=1_000_000,
        evaluated_at=CUTOFF,
        context=CONTEXT,
        data_quality_multiplier=1.0,
        feed_delay_minutes=2,
    )


def test_provider_and_shared_cash_use_opposite_accounting_directions() -> None:
    transactions = tuple(
        tx(i, TransactionType.CASH_IN, 200_000, minutes_ago=i * 5) for i in range(1, 6)
    )
    provider = features(transactions)
    shared = build_shared_cash_features(
        (source(Provider.BKASH, transactions),),
        current_balance_minor=1_000_000,
        evaluated_at=CUTOFF,
        context=CONTEXT,
        data_quality_multiplier=1.0,
        feed_delay_minutes=2,
    )

    assert provider.recent_signed_outflow_rate > 0
    assert shared.recent_signed_outflow_rate < 0


def test_future_transactions_never_change_features() -> None:
    past = tuple(
        tx(i, TransactionType.CASH_IN, 100_000, minutes_ago=i * 5) for i in range(1, 6)
    )
    future = replace(
        past[0],
        id="FUTURE",
        amount_minor=99_000_000,
        occurred_at=CUTOFF + timedelta(minutes=1),
    )

    assert features(past) == features(past + (future,))


def test_weighted_rate_projection_and_shortage_math() -> None:
    recent = tuple(
        tx(i, TransactionType.CASH_IN, 120_000, minutes_ago=i * 5) for i in range(1, 6)
    )
    prior = (
        tx(6, TransactionType.CASH_IN, 240_000, minutes_ago=90),
        tx(7, TransactionType.CASH_IN, 240_000, minutes_ago=120),
    )
    built = features(recent + prior)
    rate = active_burn_rate(built)

    assert rate == pytest.approx(8_500)
    assert projected_net_outflow(rate) == 510_000
    assert estimated_shortage_minutes(1_000_000, rate) == 118
    assert estimated_shortage_minutes(0, rate) == 0
    assert estimated_shortage_minutes(1_000_000, 0) is None


@pytest.mark.parametrize(
    ("minutes", "expected"),
    [
        (0, PressureLevel.CRITICAL),
        (60, PressureLevel.CRITICAL),
        (61, PressureLevel.HIGH),
        (180, PressureLevel.HIGH),
        (181, PressureLevel.WATCH),
        (360, PressureLevel.WATCH),
        (361, PressureLevel.NORMAL),
        (None, PressureLevel.NORMAL),
    ],
)
def test_pressure_thresholds(minutes: int | None, expected: PressureLevel) -> None:
    assert (
        pressure_level(
            estimated_minutes=minutes, evidence_sufficient=True, blocked=False
        )
        == expected
    )


def test_sparse_history_uses_fallback_and_reduces_confidence() -> None:
    built = features((tx(1, TransactionType.CASH_IN, 300_000, minutes_ago=10),))
    result = evaluate_liquidity_target(
        agent_id="AGENT-TEST",
        provider=Provider.BKASH,
        target=None,
        features=built,
        data_quality_status=DataHealthStatus.INCOMPLETE,
        data_quality_limitations=("Sparse sample",),
        recommended_verification_steps=("Collect records",),
        allow_forecast=True,
    )

    assert result.fallback_used is True
    assert result.fallback_reason == "SPARSE_RECENT_ACTIVITY"
    assert result.pressure_level == PressureLevel.UNKNOWN
    assert result.confidence < calculate_confidence(
        built, fallback_used=False, blocked=False
    )


def test_blocked_target_is_unknown_without_fake_estimates() -> None:
    built = features(
        tuple(
            tx(i, TransactionType.CASH_IN, 200_000, minutes_ago=i * 5)
            for i in range(1, 6)
        )
    )
    result = evaluate_liquidity_target(
        agent_id="AGENT-TEST",
        provider=None,
        target=ForecastTarget.SHARED_CASH,
        features=built,
        data_quality_status=DataHealthStatus.CONFLICTING,
        data_quality_limitations=("Conflicting source",),
        recommended_verification_steps=("Reconcile",),
        allow_forecast=False,
    )

    assert result.forecast_blocked is True
    assert result.pressure_level == PressureLevel.UNKNOWN
    assert result.confidence == 0
    assert result.shortage_probability is None
    assert result.estimated_shortage_minutes is None


def test_negative_balance_is_blocked_as_invalid_input() -> None:
    built = replace(
        features(
            tuple(
                tx(i, TransactionType.CASH_IN, 200_000, minutes_ago=i * 5)
                for i in range(1, 6)
            )
        ),
        current_balance_minor=-1,
    )
    result = evaluate_liquidity_target(
        agent_id="AGENT-TEST",
        provider=Provider.BKASH,
        target=None,
        features=built,
        data_quality_status=DataHealthStatus.HEALTHY,
        data_quality_limitations=(),
        recommended_verification_steps=(),
        allow_forecast=True,
    )

    assert result.forecast_blocked is True
    assert result.pressure_level == PressureLevel.UNKNOWN
    assert result.confidence == 0
    assert "negative" in result.data_quality_limitations[0].lower()


def test_forecast_identifiers_are_stable() -> None:
    built = features(
        tuple(
            tx(i, TransactionType.CASH_IN, 200_000, minutes_ago=i * 5)
            for i in range(1, 6)
        )
    )
    first = evaluate_liquidity_target(
        agent_id="AGENT-TEST",
        provider=Provider.BKASH,
        target=None,
        features=built,
        data_quality_status=DataHealthStatus.HEALTHY,
        data_quality_limitations=(),
        recommended_verification_steps=(),
        allow_forecast=True,
    )
    second = evaluate_liquidity_target(
        agent_id="AGENT-TEST",
        provider=Provider.BKASH,
        target=None,
        features=built,
        data_quality_status=DataHealthStatus.HEALTHY,
        data_quality_limitations=(),
        recommended_verification_steps=(),
        allow_forecast=True,
    )

    assert first.forecast_id == second.forecast_id
    assert first.forecast_id.startswith("FORECAST-")


def test_chronological_evaluation_reports_real_metrics_and_leakage_check() -> None:
    result = evaluate_baseline()

    assert result["sample_count"] > 0
    assert result["mae_net_outflow_minor"] is not None
    assert result["rmse_net_outflow_minor"] is not None
    assert result["smape_percent"] is not None
    assert result["leakage_check_passed"] is True
